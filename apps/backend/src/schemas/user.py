from pydantic import BaseModel, Field, EmailStr

class UserSignupKey(str):
    USER_NAME = 'username'
    EMAIL = 'email'

class UserBase(BaseModel):
    first_name: str
    last_name: str
    user_name: str | None = None
    email: EmailStr | None = None
    signup_key: UserSignupKey
