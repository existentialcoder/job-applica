from sqlalchemy.orm import Session
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
    except (InvalidTokenError, ValidationError) as ex:
        raise HTTPException(status_code=401, detail='Invalid or expired token')

def create_user(db: Session, user_data: UserSignup) -> UserBase:
    existing_users = db.query(User).filter(User.user_name == user_data.user_name).all()
    if len(existing_users) > 0:
        raise HTTPException(status_code=409, detail=f'User already exists with user_name: ${user_data.user_name}')
    hashed_password = hash_password(user_data.password)

    user_name = user_data.email or user_data.user_name

    user_data = User(**user_data.model_dump(exclude={'password'}, exclude_unset=True))
    user_data.hashed_password = hashed_password
    user_data.user_name = user_name

    db.add(user_data)
    db.commit()
    db.refresh(user_data)

    return UserBase.model_validate(user_data)

def user_login(db: Session, login_data: UserLogin) -> UserLoginTokenResponse:
    # Check if user name and password match
    user_data = db.query(User).filter(User.email == login_data.username or User.user_name == login_data.username).first()

    if not user_data:
        raise HTTPException(status_code=404, detail = 'User not found')
    
    # Check if passwords match
    is_authenticated = verify_password(login_data.password, user_data.hashed_password)

    if not is_authenticated:
        raise HTTPException(status_code=401, detail='Incorrect password')
    
    token_data: TokenPayload = {
        'sub': str(user_data.id),
        'user_name': user_data.user_name,
        'signup_key': user_data.signup_key,
        'email': user_data.email
    }

    access_token = create_token(token_data,
                                expiry=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
                                expiry_type='minutes',
                                secret=settings.AUTH_SECRET,
                                algorithm=Constants.AUTH_ALGORITHM)
    
    refresh_token = create_token(token_data,
                                 expiry=settings.REFRESH_TOKEN_EXPIRE_DAYS,
                                 expiry_type='days',
                                 secret=settings.AUTH_SECRET,
                                 algorithm=Constants.AUTH_ALGORITHM)

    return UserLoginTokenResponse(
        message='Successfully logged in',
        access_token=access_token,
        refresh_token=refresh_token,
        token_type='Bearer'
    )

def get_user_by_id(db: Session, user_id: int) -> UserBase | None:
    user_data = db.query(User).filter(User.id == user_id).first()
    if not user_data:
        raise HTTPException(status_code=404, detail='User not found')
    return UserBase.model_validate(user_data)
