from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .db import get_db
from ...schemas.user import UserBase
from ...services import user as user_service

api_v1_prefix = '/api/v1'

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{api_v1_prefix}/auth/login"
)

TokenDep = Annotated[str, Depends(reusable_oauth2)]

def get_current_user(token: TokenDep, db: Session=Depends(get_db)) -> UserBase:
    token = user_service.decode_token(token)
    user = user_service.get_user_by_id(db, token.sub)
    return UserBase.model_validate(user)
