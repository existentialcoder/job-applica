from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ....schemas import user as schemas
from ....core.config import settings
from ...deps.db import get_db
from ....services import user as user_service

router = APIRouter(prefix='/auth')

@router.post('/signup', description='User signup API')
def signup_user(user_data: schemas.UserSignup, db: Session = Depends(get_db)):
    if not user_data.email and not user_data.user_name:
        raise HTTPException(status_code=400, detail='Either email or user_name must be provided')
    return user_service.create_user(db, user_data)

@router.post('/login', response_model=schemas.UserLoginTokenResponse , description='User Login API')
def login(response: Response, login_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    login_result = user_service.user_login(db, login_data)
    response.set_cookie(
        key='refresh_token',
        value=login_result.refresh_token,
        httponly=True,
        secure=True,
        samesite='strict',
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

    return login_result
