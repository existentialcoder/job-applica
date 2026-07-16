import os
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ....schemas import user as schemas
from ....core.config import settings
from ....core.utils import verify_password, hash_password
from ...deps.auth import get_current_user
from ...deps.db import get_db
from ...deps.plan import plan_gate
from ....models.user import User
from ....models.skill import Skill
from ....models.resume import Resume
from ....services import resume as resume_service
from sqlalchemy import func
from ....utils.file_uploader import FileUploader

UPLOAD_BASE = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'uploads')
ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
MAX_AVATAR_MB = 2

router = APIRouter(prefix='/users')
class UpdateProfileRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


def _check_self(user_id: int, current_user: schemas.UserBase):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail='Forbidden')


def _resume_response(r, user_id: int) -> dict:
    if settings.APP_ENV == 'local':
        url = f'/uploads/{user_id}/resumes/{r.stored_name}'
    else:
        url = f'{settings.CLOUDFLARE_R2_PUBLIC_URL}/{user_id}/resumes/{r.stored_name}'
    return {
        'id': r.id,
        'original_name': r.original_name,
        'file_size': r.file_size,
        'is_default': r.is_default,
        'url': url,
        'created_at': r.created_at.isoformat() if r.created_at else None,
    }


# ── Profile ───────────────────────────────────────────────────────────────────

@router.get('/{user_id}', response_model=schemas.UserBase)
async def get_user(
    user_id: int,
    current_user: schemas.UserBase = Depends(get_current_user),
):
    _check_self(user_id, current_user)
    return current_user


@router.patch('/{user_id}')
async def update_user(
    user_id: int,
    payload: UpdateProfileRequest,
    current_user: schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    if payload.first_name is not None:
        user.first_name = payload.first_name
    if payload.last_name is not None:
        user.last_name = payload.last_name
    if payload.avatar_url is not None:
        user.avatar_url = payload.avatar_url
    await db.commit()
    await db.refresh(user)
    return user


@router.post('/{user_id}/avatar')
async def upload_avatar(
    user_id: int,
    file: UploadFile = File(...),
    current_user: schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail='Only JPEG, PNG, WebP and GIF images are accepted')

    ext = os.path.splitext(file.filename or 'avatar')[1] or '.jpg'
    stored_name = f'avatar{ext}'
    r2_key = f'avatars/{user_id}/{stored_name}'
    dest = os.path.join(UPLOAD_BASE, 'avatars', str(user_id), stored_name)

    uploader = FileUploader(destination_path=dest, file=file, max_size_mb=MAX_AVATAR_MB)
    if settings.APP_ENV == 'local':
        await uploader.upload_local()
        avatar_url = f'/uploads/avatars/{user_id}/{stored_name}'
    else:
        await uploader.upload_to_cloudflare(bucket=settings.CLOUDFLARE_R2_BUCKET_NAME, key=r2_key)
        avatar_url = f'{settings.CLOUDFLARE_R2_PUBLIC_URL}/{r2_key}'

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    user.avatar_url = avatar_url
    await db.commit()
    return {'avatar_url': avatar_url}


@router.post('/{user_id}/change-password')
async def change_password(
    user_id: int,
    payload: ChangePasswordRequest,
    current_user: schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.hashed_password:
        raise HTTPException(status_code=400, detail='Password change not available for OAuth accounts')
    if not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail='Current password is incorrect')
    user.hashed_password = hash_password(payload.new_password)
    await db.commit()
    return {'message': 'Password updated'}


@router.get('/{user_id}/settings')
async def get_settings(
    user_id: int,
    current_user: schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    return {'settings': user.settings if user else {}}


@router.patch('/{user_id}/settings')
async def update_settings(
    user_id: int,
    payload: schemas.UserSettings,
    current_user: schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    user.settings = {**(user.settings or {}), **payload.settings}
    await db.commit()
    await db.refresh(user)
    return {'settings': user.settings}


# ── Skills ────────────────────────────────────────────────────────────────────

@router.get('/{user_id}/skills')
async def get_user_skills(
    user_id: int,
    current_user: schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    return user.skills if user else []


@router.post('/{user_id}/skills/{skill_id}')
async def add_user_skill(
    user_id: int,
    skill_id: int,
    current_user: schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    skill_result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = skill_result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail='Skill not found')
    if skill not in user.skills:
        user.skills.append(skill)
        await db.commit()
    return user.skills


@router.delete('/{user_id}/skills/{skill_id}')
async def remove_user_skill(
    user_id: int,
    skill_id: int,
    current_user: schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    skill_result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = skill_result.scalar_one_or_none()
    if skill and skill in user.skills:
        user.skills.remove(skill)
        await db.commit()
    return user.skills


# ── Resumes ───────────────────────────────────────────────────────────────────

@router.get('/{user_id}/resumes')
async def list_resumes(
    user_id: int,
    current_user: schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    resumes = await resume_service.list_resumes(db, user_id)
    return [_resume_response(r, user_id) for r in resumes]


@router.post(
    '/{user_id}/resumes',
    dependencies=[plan_gate('max_resumes', lambda uid: select(func.count(Resume.id)).where(Resume.user_id == uid))],
)
async def upload_resume(
    user_id: int,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    current_user: schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    resume = await resume_service.upload_resume(db, user_id, file)
    if background_tasks and resume.parsed_text:
        background_tasks.add_task(resume_service.sync_skills_background, user_id, resume.parsed_text)
    return _resume_response(resume, user_id)


@router.delete('/{user_id}/resumes/{resume_id}')
async def delete_resume(
    user_id: int,
    resume_id: int,
    current_user: schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    await resume_service.delete_resume(db, user_id, resume_id)
    return {'deleted': resume_id}


@router.patch('/{user_id}/resumes/{resume_id}/default', status_code=204)
async def set_default_resume(
    user_id: int,
    resume_id: int,
    current_user: schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    await resume_service.set_default_resume(db, user_id, resume_id)
