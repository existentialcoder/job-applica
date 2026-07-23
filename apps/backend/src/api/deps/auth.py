from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_db
from ...core.constants import Constants
from ...schemas.user import UserBase
from ...services import user as user_service

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{Constants.API_V1_PREFIX}/auth/login"
)

TokenDep = Annotated[str, Depends(reusable_oauth2)]

async def get_current_user(token: TokenDep, db: AsyncSession = Depends(get_db)) -> UserBase:
    token_data = user_service.decode_token(token)
    if token_data.purpose:
        raise HTTPException(status_code=401, detail='This token cannot be used for authentication')
    user = await user_service.get_user_by_id(db, int(token_data.sub))
    return UserBase.model_validate(user)
