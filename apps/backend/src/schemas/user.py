from enum import Enum
from pydantic import BaseModel, Field, EmailStr

class UserSignupKey(str, Enum):
    USER_NAME = 'USER_NAME'
    EMAIL = 'EMAIL'

class UserBase(BaseModel):
    first_name: str
    last_name: str
    user_name: str | None = None
    email: EmailStr | None = None
    signup_key: UserSignupKey
