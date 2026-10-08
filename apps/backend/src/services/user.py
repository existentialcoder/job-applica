import os

import jwt
from fastapi import HTTPException, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from pydantic import EmailStr, ValidationError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.constants import Constants
from ..core.utils import create_token, hash_password, verify_password
from ..models.skill import Skill
from ..models.user import AccountRecovery, User
from ..schemas.settings import UserSettings
from ..schemas.user import TokenPayload, UserBase, UserLoginTokenResponse, UserNameCheckResponse, UserSignup
from ..utils.file_storage import get_file_storage_factory

ALLOWED_AVATAR_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
MAX_AVATAR_MB = 2


async def _get_user_or_404(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user


def decode_token(token: str, secret: str = settings.AUTH_SECRET) -> TokenPayload:
    try:
        payload = jwt.decode(token, secret, algorithms=[Constants.AUTH_ALGORITHM])
        return TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(status_code=401, detail='Invalid or expired token')


async def create_user(db: AsyncSession, user_data: UserSignup) -> UserBase:
    result = await db.execute(select(User).where(User.user_name == user_data.user_name))
    if result.scalars().first():
        raise HTTPException(status_code=409, detail=f'User already exists with user_name: ${user_data.user_name}')

    user_name = user_data.user_name or user_data.email
    assert user_name is not None  # signup_user route already rejects payloads with neither
    user_obj = User(
        **user_data.model_dump(exclude={'password', 'security_question', 'security_answer'}, exclude_unset=True)
    )
    user_obj.hashed_password = hash_password(user_data.password)
    user_obj.user_name = user_name
    user_obj.settings = UserSettings().model_dump()

    db.add(user_obj)
    if user_data.security_question and user_data.security_answer:
        await db.flush()
        db.add(
            AccountRecovery(
                user_id=user_obj.id,
                security_question=user_data.security_question,
                hashed_security_answer=hash_password(user_data.security_answer),
            )
        )
    await db.commit()
    await db.refresh(user_obj)
    return UserBase.model_validate(user_obj)


async def check_user_name_availability(db: AsyncSession, user_name: str) -> UserNameCheckResponse:
    existing_user_count = await db.execute(select(func.count(User.user_name)).where(User.user_name == user_name))

    return UserNameCheckResponse(is_available=existing_user_count.scalar() == 0)


async def user_login(db: AsyncSession, login_data: OAuth2PasswordRequestForm) -> UserLoginTokenResponse:
    result = await db.execute(
        select(User).where((User.email == login_data.username) | (User.user_name == login_data.username))
    )
    user_data = result.scalar_one_or_none()

    if not user_data:
        raise HTTPException(status_code=404, detail='User not found')

    if not user_data.hashed_password:
        raise HTTPException(
            status_code=400, detail='This account uses social login. Please sign in with Google or LinkedIn.'
        )

    if not verify_password(login_data.password, user_data.hashed_password):
        raise HTTPException(status_code=401, detail='Incorrect password')

    token_data: dict = {
        'sub': str(user_data.id),
        'user_name': user_data.user_name,
        'signup_key': user_data.signup_key,
        'email': user_data.email,
    }

    access_token = create_token(
        token_data,
        expiry=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        expiry_type='minutes',
        secret=settings.AUTH_SECRET,
        algorithm=Constants.AUTH_ALGORITHM,
    )
    refresh_token = create_token(
        token_data,
        expiry=settings.REFRESH_TOKEN_EXPIRE_DAYS,
        expiry_type='days',
        secret=settings.AUTH_SECRET,
        algorithm=Constants.AUTH_ALGORITHM,
    )

    return UserLoginTokenResponse(
        message='Successfully logged in',
        access_token=access_token,
        refresh_token=refresh_token,
        token_type='Bearer',
    )


async def get_user_by_id(db: AsyncSession, user_id: int) -> UserBase:
    result = await db.execute(select(User).where(User.id == user_id))
    user_data = result.scalar_one_or_none()
    if not user_data:
        raise HTTPException(status_code=404, detail='User not found')
    return UserBase.model_validate(user_data)


async def get_user_by_user_name(db: AsyncSession, user_name: str) -> User:
    result = await db.execute(select(User).where(User.user_name == user_name))
    user_data = result.scalar_one_or_none()
    if not user_data:
        raise HTTPException(status_code=404, detail='User not found')
    return user_data


async def get_user_by_email(db: AsyncSession, user_email: EmailStr) -> User:
    result = await db.execute(select(User).where(User.email == user_email))
    user_data = result.scalar_one_or_none()
    if not user_data:
        raise HTTPException(status_code=404, detail='User not found')
    return user_data


async def update_profile(
    db: AsyncSession,
    user_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
    avatar_url: str | None = None,
) -> User:
    user = await _get_user_or_404(db, user_id)
    if first_name is not None:
        user.first_name = first_name
    if last_name is not None:
        user.last_name = last_name
    if avatar_url is not None:
        user.avatar_url = avatar_url
    await db.commit()
    await db.refresh(user)
    return user


async def upload_avatar(db: AsyncSession, user_id: int, file: UploadFile) -> str:
    if file.content_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(status_code=400, detail='Only JPEG, PNG, WebP and GIF images are accepted')

    ext = os.path.splitext(file.filename or 'avatar')[1] or '.jpg'
    file_storage = get_file_storage_factory()(
        destination_path=f'{user_id}/avatars', file=file, max_size_mb=MAX_AVATAR_MB, stored_name=f'avatar{ext}'
    )
    key, _ = await file_storage.upload()
    base_url = (
        f'{settings.BACKEND_URL}/uploads/users' if settings.APP_ENV == 'local' else settings.CLOUDFLARE_R2_PUBLIC_URL
    )
    avatar_url = f'{base_url}/{key}'

    user = await _get_user_or_404(db, user_id)
    user.avatar_url = avatar_url
    await db.commit()
    return avatar_url


async def change_password(db: AsyncSession, user_id: int, current_password: str, new_password: str) -> None:
    user = await _get_user_or_404(db, user_id)
    if not user.hashed_password:
        raise HTTPException(status_code=400, detail='Password change not available for OAuth accounts')
    if not verify_password(current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail='Current password is incorrect')
    user.hashed_password = hash_password(new_password)
    await db.commit()


async def get_settings(db: AsyncSession, user_id: int) -> dict:
    user = await _get_user_or_404(db, user_id)
    return {**UserSettings().model_dump(), **(user.settings or {})}


async def update_settings(db: AsyncSession, user_id: int, settings_patch: dict) -> dict:
    user = await _get_user_or_404(db, user_id)
    user.settings = {**(user.settings or {}), **settings_patch}
    await db.commit()
    await db.refresh(user)
    return user.settings


async def get_skills(db: AsyncSession, user_id: int) -> list[Skill]:
    user = await _get_user_or_404(db, user_id)
    return user.skills


async def add_skill(db: AsyncSession, user_id: int, skill_id: int) -> list[Skill]:
    user = await _get_user_or_404(db, user_id)
    skill_result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = skill_result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail='Skill not found')
    if skill not in user.skills:
        user.skills.append(skill)
        await db.commit()
    return user.skills


async def remove_skill(db: AsyncSession, user_id: int, skill_id: int) -> list[Skill]:
    user = await _get_user_or_404(db, user_id)
    skill_result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = skill_result.scalar_one_or_none()
    if skill and skill in user.skills:
        user.skills.remove(skill)
        await db.commit()
    return user.skills
