from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Optional
from .base import BaseSchema

class UserSignupKey(str, Enum):
    USER_NAME = 'USER_NAME'
    EMAIL = 'EMAIL'

class UserBase(BaseSchema):
    first_name: str
    last_name: str
    user_name: str
    email: EmailStr | None = None
    signup_key: UserSignupKey

class UserSignup(BaseModel):
    first_name: str
    last_name: str
    user_name: str | None = None
    email: EmailStr | None = None
    password: str
    signup_key: UserSignupKey

class UserLogin(BaseModel):
    user_id: str
    password: str

class UserLoginTokenResponse(BaseModel):
    message: str
    access_token: str
    refresh_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: str
    user_name: str
    signup_key: UserSignupKey
    email: Optional[EmailStr] = None
