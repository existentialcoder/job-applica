import os
import uuid
import shutil
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ....schemas import user as schemas
from ....core.config import settings
from ....core.constants import Constants
from ....core.utils import create_token, hash_password, verify_password
from ...deps.auth import get_current_user
from ...deps.db import get_db
from ....services import user as user_service
from ....services import oauth as oauth_service
from ....models.user import User
from ....models.skill import Skill
from ....models.resume import Resume

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'uploads', 'resumes')
ALLOWED_TYPES = {'application/pdf', 'application/msword',
                 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}
MAX_SIZE_MB = 10

AVATAR_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'uploads', 'avatars')
ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
MAX_AVATAR_MB = 2

router = APIRouter(prefix='/auth')


class RefreshRequest(BaseModel):
    refresh_token: str


class UpdateProfileRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.get('/me', response_model=schemas.UserBase, description='Get current user profile')
def get_me(current_user: schemas.UserBase = Depends(get_current_user)):
    return current_user


@router.post('/refresh', description='Exchange a refresh token for a new access token')
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    try:
        token_data = user_service.decode_token(payload.refresh_token)
    except HTTPException:
        raise HTTPException(status_code=401, detail='Invalid or expired refresh token')

    user = db.query(User).filter(User.id == int(token_data.sub)).first()
    if not user:
        raise HTTPException(status_code=401, detail='User not found')

    new_payload = {
        'sub': str(user.id),
        'user_name': user.user_name,
        'signup_key': user.signup_key,
        'email': user.email,
    }
    access_token = create_token(
        new_payload,
        expiry=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        expiry_type='minutes',
        secret=settings.AUTH_SECRET,
        algorithm=Constants.AUTH_ALGORITHM,
    )
    return {'access_token': access_token, 'token_type': 'Bearer'}


@router.get('/settings', description='Get current user settings')
def get_settings(current_user: schemas.UserBase = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user.id).first()
    return {'settings': user.settings if user else {}}


@router.patch('/settings', description='Merge-update user settings')
def update_settings(
    payload: schemas.UserSettings,
    current_user: schemas.UserBase = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    user.settings = {**(user.settings or {}), **payload.settings}
    db.commit()
    db.refresh(user)
    return {'settings': user.settings}


@router.post('/signup', description='User signup API')
def signup_user(user_data: schemas.UserSignup, db: Session = Depends(get_db)):
    if not user_data.email and not user_data.user_name:
        raise HTTPException(status_code=400, detail='Either email or user_name must be provided')
    return user_service.create_user(db, user_data)


@router.post('/login', response_model=schemas.UserLoginTokenResponse, description='User Login API')
def login(response: Response, login_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    login_result = user_service.user_login(db, login_data)
    response.set_cookie(
        key='refresh_token',
        value=login_result.refresh_token,
        httponly=True,
        secure=False,
        samesite='lax',
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )
    return login_result


# ── Profile update ───────────────────────────────────────────────────────────

@router.patch('/me', description='Update own profile')
def update_me(
    payload: UpdateProfileRequest,
    current_user: schemas.UserBase = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    if payload.first_name is not None:
        user.first_name = payload.first_name
    if payload.last_name is not None:
        user.last_name = payload.last_name
    if payload.avatar_url is not None:
        user.avatar_url = payload.avatar_url
    db.commit()
    db.refresh(user)
    return user


@router.post('/change-password', description='Change password (email/password users only)')
def change_password(
    payload: ChangePasswordRequest,
    current_user: schemas.UserBase = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user or not user.hashed_password:
        raise HTTPException(status_code=400, detail='Password change not available for OAuth accounts')
    if not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail='Current password is incorrect')
    user.hashed_password = hash_password(payload.new_password)
    db.commit()
    return {'message': 'Password updated'}


# ── Avatar upload ─────────────────────────────────────────────────────────────

@router.post('/avatar', description='Upload a profile avatar image (max 2 MB)')
def upload_avatar(
    file: UploadFile = File(...),
    current_user: schemas.UserBase = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail='Only JPEG, PNG, WebP and GIF images are accepted')

    user_dir = os.path.join(AVATAR_DIR, str(current_user.id))
    os.makedirs(user_dir, exist_ok=True)

    ext = os.path.splitext(file.filename or 'avatar')[1] or '.jpg'
    stored_name = f'avatar{ext}'
    dest = os.path.join(user_dir, stored_name)

    size = 0
    with open(dest, 'wb') as f:
        for chunk in iter(lambda: file.file.read(1024 * 256), b''):
            size += len(chunk)
            if size > MAX_AVATAR_MB * 1024 * 1024:
                f.close()
                os.remove(dest)
                raise HTTPException(status_code=413, detail=f'Image exceeds {MAX_AVATAR_MB} MB limit')
            f.write(chunk)

    avatar_url = f'/uploads/avatars/{current_user.id}/{stored_name}'
    user = db.query(User).filter(User.id == current_user.id).first()
    user.avatar_url = avatar_url
    db.commit()
    return {'avatar_url': avatar_url}


# ── User skills ───────────────────────────────────────────────────────────────

@router.get('/skills', description='Get skills linked to the current user')
def get_user_skills(
    current_user: schemas.UserBase = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == current_user.id).first()
    return user.skills if user else []


@router.post('/skills/{skill_id}', description='Add a skill to the current user')
def add_user_skill(
    skill_id: int,
    current_user: schemas.UserBase = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == current_user.id).first()
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail='Skill not found')
    if skill not in user.skills:
        user.skills.append(skill)
        db.commit()
    return user.skills


@router.delete('/skills/{skill_id}', description='Remove a skill from the current user')
def remove_user_skill(
    skill_id: int,
    current_user: schemas.UserBase = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == current_user.id).first()
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if skill and skill in user.skills:
        user.skills.remove(skill)
        db.commit()
    return user.skills


# ── Resumes ───────────────────────────────────────────────────────────────────

@router.get('/resumes', description='List uploaded resumes')
def list_resumes(
    current_user: schemas.UserBase = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.id.desc()).all()
    return [
        {
            'id': r.id,
            'original_name': r.original_name,
            'file_size': r.file_size,
            'url': f'/uploads/resumes/{current_user.id}/{r.stored_name}',
            'created_at': r.created_at,
        }
        for r in resumes
    ]


@router.post('/resumes', description='Upload a resume (PDF or DOCX, max 10 MB)')
def upload_resume(
    file: UploadFile = File(...),
    current_user: schemas.UserBase = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail='Only PDF and Word documents are accepted')

    user_dir = os.path.join(UPLOAD_DIR, str(current_user.id))
    os.makedirs(user_dir, exist_ok=True)

    ext = os.path.splitext(file.filename or 'resume')[1] or '.pdf'
    stored_name = f'{uuid.uuid4().hex}{ext}'
    dest = os.path.join(user_dir, stored_name)

    size = 0
    with open(dest, 'wb') as f:
        for chunk in iter(lambda: file.file.read(1024 * 256), b''):
            size += len(chunk)
            if size > MAX_SIZE_MB * 1024 * 1024:
                f.close()
                os.remove(dest)
                raise HTTPException(status_code=413, detail=f'File exceeds {MAX_SIZE_MB} MB limit')
            f.write(chunk)

    resume = Resume(
        user_id=current_user.id,
        original_name=file.filename or stored_name,
        stored_name=stored_name,
        file_path=dest,
        file_size=size,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {
        'id': resume.id,
        'original_name': resume.original_name,
        'file_size': resume.file_size,
        'url': f'/uploads/resumes/{current_user.id}/{stored_name}',
        'created_at': resume.created_at,
    }


@router.delete('/resumes/{resume_id}', description='Delete a resume')
def delete_resume(
    resume_id: int,
    current_user: schemas.UserBase = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail='Resume not found')
    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)
    db.delete(resume)
    db.commit()
    return {'deleted': resume_id}


# ── Google OAuth ──────────────────────────────────────────────────────────────

@router.get('/google', description='Redirect to Google OAuth consent screen')
def google_login(origin: str = 'web'):
    url = oauth_service.get_google_auth_url(origin)
    return RedirectResponse(url)


@router.get('/google/callback', description='Google OAuth callback')
async def google_callback(code: str, state: str = '', db: Session = Depends(get_db)):
    if not code:
        raise HTTPException(status_code=400, detail='Missing authorization code')

    origin = state.split(':')[0] if ':' in state else 'web'

    user_info = await oauth_service.exchange_google_code(code)

    user = oauth_service.get_or_create_oauth_user(
        db=db,
        provider='google',
        provider_id=user_info.get('sub', ''),
        email=user_info.get('email', ''),
        first_name=user_info.get('given_name', ''),
        last_name=user_info.get('family_name', ''),
        avatar_url=user_info.get('picture'),
    )

    tokens = oauth_service.create_tokens_for_user(user)

    relay_path = '/auth/relay' if origin == 'extension' else '/auth/callback'
    redirect_url = (
        f'{settings.FRONTEND_URL}{relay_path}'
        f'?access_token={tokens.access_token}'
        f'&refresh_token={tokens.refresh_token}'
    )
    return RedirectResponse(redirect_url)


# ── LinkedIn OAuth ────────────────────────────────────────────────────────────

@router.get('/linkedin', description='Redirect to LinkedIn OAuth consent screen')
def linkedin_login(origin: str = 'web'):
    url = oauth_service.get_linkedin_auth_url(origin)
    return RedirectResponse(url)


@router.get('/linkedin/callback', description='LinkedIn OAuth callback')
async def linkedin_callback(code: str, state: str = '', db: Session = Depends(get_db)):
    if not code:
        raise HTTPException(status_code=400, detail='Missing authorization code')

    origin = state.split(':')[0] if ':' in state else 'web'

    user_info = await oauth_service.exchange_linkedin_code(code)

    user = oauth_service.get_or_create_oauth_user(
        db=db,
        provider='linkedin',
        provider_id=user_info.get('sub', ''),
        email=user_info.get('email', ''),
        first_name=user_info.get('given_name', ''),
        last_name=user_info.get('family_name', ''),
        avatar_url=user_info.get('picture'),
    )

    tokens = oauth_service.create_tokens_for_user(user)

    relay_path = '/auth/relay' if origin == 'extension' else '/auth/callback'
    redirect_url = (
        f'{settings.FRONTEND_URL}{relay_path}'
        f'?access_token={tokens.access_token}'
        f'&refresh_token={tokens.refresh_token}'
    )
    return RedirectResponse(redirect_url)
