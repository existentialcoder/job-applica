from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import ValidationError
from fastapi import HTTPException
import jwt
from jwt import InvalidTokenError

from ..core.utils import hash_password, verify_password, create_token
from ..core.config import settings
from ..core.constants import Constants
from ..models.user import User
from ..schemas.user import UserBase, UserSignup, UserLogin, UserLoginTokenResponse, TokenPayload


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

    user_name = user_data.email or user_data.user_name
    user_obj = User(**user_data.model_dump(exclude={'password'}, exclude_unset=True))
    user_obj.hashed_password = hash_password(user_data.password)
    user_obj.user_name = user_name

    db.add(user_obj)
    await db.commit()
    await db.refresh(user_obj)
    return UserBase.model_validate(user_obj)


async def user_login(db: AsyncSession, login_data: UserLogin) -> UserLoginTokenResponse:
    result = await db.execute(
        select(User).where((User.email == login_data.username) | (User.user_name == login_data.username))
    )
    user_data = result.scalar_one_or_none()

    if not user_data:
        raise HTTPException(status_code=404, detail='User not found')

    if not user_data.hashed_password:
        raise HTTPException(status_code=400, detail='This account uses social login. Please sign in with Google or LinkedIn.')

    if not verify_password(login_data.password, user_data.hashed_password):
        raise HTTPException(status_code=401, detail='Incorrect password')

    token_data: TokenPayload = {
        'sub': str(user_data.id),
        'user_name': user_data.user_name,
        'signup_key': user_data.signup_key,
        'email': user_data.email,
    }

    access_token = create_token(token_data, expiry=settings.ACCESS_TOKEN_EXPIRE_MINUTES, expiry_type='minutes', secret=settings.AUTH_SECRET, algorithm=Constants.AUTH_ALGORITHM)
    refresh_token = create_token(token_data, expiry=settings.REFRESH_TOKEN_EXPIRE_DAYS, expiry_type='days', secret=settings.AUTH_SECRET, algorithm=Constants.AUTH_ALGORITHM)

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
