from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.config import settings
from ....jobs.extract_resume import extract_resume
from ....models.resume import Resume
from ....schemas import user as user_schemas
from ....schemas.preferences import JobPreferences
from ....schemas.profile import ProfileResponse, ProfileUpdate
from ....services import preferences as preferences_service
from ....services import profile as profile_service
from ....services import resume as resume_service
from ....services import user as user_service
from ...deps.auth import get_current_user
from ...deps.db import get_db
from ...deps.plan import plan_gate

router = APIRouter(prefix='/users')
public_router = APIRouter(prefix='/users')


class UpdateProfileRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


def _check_self(user_id: int, current_user: user_schemas.UserBase):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail='Forbidden')


def _resume_response(r, user_id: int) -> dict:
    if settings.APP_ENV == 'local':
        url = f'/uploads/users/{user_id}/resumes/{r.stored_name}'
    else:
        url = f'{settings.CLOUDFLARE_R2_PUBLIC_URL}/{user_id}/resumes/{r.stored_name}'
    return {
        'id': r.id,
        'original_name': r.original_name,
        'file_size': r.file_size,
        'is_default': r.is_default,
        'url': url,
        'extraction': r.extraction_status,
        'created_at': r.created_at.isoformat() if r.created_at else None,
    }


@public_router.post('/check-user-name', response_model=user_schemas.UserNameCheckResponse)
async def check_user_name_availability(
    payload: user_schemas.UserNameCheckRequest,
    db: AsyncSession = Depends(get_db),
):
    return await user_service.check_user_name_availability(db, payload.user_name)


@public_router.get('/security-questions', response_model=list[str])
async def get_security_questions():
    return [q.value for q in user_schemas.SecurityQuestion]


@router.get('/{user_id}', response_model=user_schemas.UserBase)
async def get_user(
    user_id: int,
    current_user: user_schemas.UserBase = Depends(get_current_user),
):
    _check_self(user_id, current_user)
    return current_user


@router.patch('/{user_id}')
async def update_user(
    user_id: int,
    payload: UpdateProfileRequest,
    current_user: user_schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    return await user_service.update_profile(
        db,
        user_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        avatar_url=payload.avatar_url,
    )


@router.post('/{user_id}/avatar')
async def upload_avatar(
    user_id: int,
    file: UploadFile = File(...),
    current_user: user_schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    avatar_url = await user_service.upload_avatar(db, user_id, file)
    return {'avatar_url': avatar_url}


@router.post('/{user_id}/change-password')
async def change_password(
    user_id: int,
    payload: ChangePasswordRequest,
    current_user: user_schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    await user_service.change_password(db, user_id, payload.current_password, payload.new_password)
    return {'message': 'Password updated'}


@router.get('/{user_id}/settings')
async def get_settings(
    user_id: int,
    current_user: user_schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    return {'settings': await user_service.get_settings(db, user_id)}


@router.patch('/{user_id}/settings')
async def update_settings(
    user_id: int,
    payload: user_schemas.UserSettingsRequest,
    current_user: user_schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    settings_patch = payload.settings.model_dump(exclude_unset=True)
    return {'settings': await user_service.update_settings(db, user_id, settings_patch)}


@router.get('/{user_id}/onboarding')
async def get_onboarding(
    user_id: int,
    current_user: user_schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    # Accounts created before onboarding existed have no row; they are never sent through setup.
    onboarding = await user_service.get_onboarding(db, user_id)
    return {'onboarding': user_schemas.OnboardingResponse.model_validate(onboarding) if onboarding else None}


@router.patch('/{user_id}/onboarding', response_model=user_schemas.OnboardingResponse)
async def update_onboarding(
    user_id: int,
    payload: user_schemas.OnboardingUpdate,
    current_user: user_schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    return await user_service.update_onboarding(db, user_id, payload)


@router.get('/{user_id}/profile')
async def get_profile(
    user_id: int,
    current_user: user_schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    return {'profile': await profile_service.get_profile(db, user_id)}


@router.put('/{user_id}/profile', response_model=ProfileResponse)
async def save_profile(
    user_id: int,
    payload: ProfileUpdate,
    current_user: user_schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    return await profile_service.save_profile(db, user_id, payload)


@router.get('/{user_id}/preferences')
async def get_preferences(
    user_id: int,
    current_user: user_schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    return {'preferences': await preferences_service.get_preferences(db, user_id)}


@router.put('/{user_id}/preferences', response_model=JobPreferences)
async def save_preferences(
    user_id: int,
    payload: JobPreferences,
    current_user: user_schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    return await preferences_service.save_preferences(db, user_id, payload)


@router.get('/{user_id}/skills')
async def get_user_skills(
    user_id: int,
    current_user: user_schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    return await user_service.get_skills(db, user_id)


@router.post('/{user_id}/skills/{skill_id}')
async def add_user_skill(
    user_id: int,
    skill_id: int,
    current_user: user_schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    return await user_service.add_skill(db, user_id, skill_id)


@router.delete('/{user_id}/skills/{skill_id}')
async def remove_user_skill(
    user_id: int,
    skill_id: int,
    current_user: user_schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    return await user_service.remove_skill(db, user_id, skill_id)


@router.get('/{user_id}/resumes')
async def list_resumes(
    user_id: int,
    current_user: user_schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    resumes = await resume_service.list_resumes(db, user_id)
    return [_resume_response(r, user_id) for r in resumes]


@router.post(
    '/{user_id}/resumes',
    status_code=202,
    dependencies=[plan_gate('max_resumes', lambda uid: select(func.count(Resume.id)).where(Resume.user_id == uid))],
)
async def upload_resume(
    user_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: user_schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    resume = await resume_service.upload_resume(db, user_id, file)
    background_tasks.add_task(extract_resume, resume.id)
    return _resume_response(resume, user_id)


@router.get('/{user_id}/resumes/{resume_id}')
async def get_resume(
    user_id: int,
    resume_id: int,
    current_user: user_schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    return _resume_response(await resume_service.get_resume(db, user_id, resume_id), user_id)


@router.post('/{user_id}/resumes/{resume_id}/replace', status_code=202)
async def replace_resume(
    user_id: int,
    resume_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: user_schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Setup's Replace: the new CV takes the old one's place and builds a fresh profile."""
    _check_self(user_id, current_user)
    resume = await resume_service.replace_resume(db, user_id, resume_id, file)
    background_tasks.add_task(extract_resume, resume.id)
    return _resume_response(resume, user_id)


@router.delete('/{user_id}/resumes/{resume_id}')
async def delete_resume(
    user_id: int,
    resume_id: int,
    current_user: user_schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    await resume_service.delete_resume(db, user_id, resume_id)
    return {'deleted': resume_id}


@router.patch('/{user_id}/resumes/{resume_id}/default', status_code=204)
async def set_default_resume(
    user_id: int,
    resume_id: int,
    current_user: user_schemas.UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _check_self(user_id, current_user)
    await resume_service.set_default_resume(db, user_id, resume_id)
