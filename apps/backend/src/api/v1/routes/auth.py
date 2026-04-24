from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ....schemas import user as schemas
from ....core.config import settings
from ....core.constants import Constants
from ....core.utils import create_token
from ...deps.auth import get_current_user
from ...deps.db import get_db
from ....services import user as user_service
from ....services import oauth as oauth_service
from ....models.user import User

router = APIRouter(prefix='/auth')


class RefreshRequest(BaseModel):
    refresh_token: str


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
