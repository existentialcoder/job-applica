from enum import Enum
from pydantic import BaseModel, EmailStr, model_validator
from typing import Any, Optional
from .base import BaseSchema

class UserSignupKey(str, Enum):
    USER_NAME = 'USER_NAME'
    EMAIL = 'EMAIL'

class SecurityQuestion(str, Enum):
    FIRST_PET = 'What was the name of your first pet?'
    MOTHERS_MAIDEN_NAME = "What is your mother's maiden name?"
    FIRST_SCHOOL = 'What was the name of your first school?'
    BIRTH_CITY = 'What city were you born in?'
    CHILDHOOD_NICKNAME = 'What was your childhood nickname?'

class UserBase(BaseSchema):
    first_name: str
    last_name: str
    user_name: str
    email: EmailStr | None = None
    signup_key: UserSignupKey
    has_password: bool = False
    security_question: str | None = None
    avatar_url: str | None = None
    plan: str = 'free'
    settings: dict[str, Any] = {}

    @model_validator(mode='before')
    @classmethod
    def _derive_has_password(cls, data: Any) -> Any:
        hashed_password = data.get('hashed_password') if isinstance(data, dict) else getattr(data, 'hashed_password', None)
        has_password = bool(hashed_password) and len(hashed_password) > 0
        if isinstance(data, dict):
            return {**data, 'has_password': has_password}
        return {**{field: getattr(data, field, None) for field in cls.model_fields}, 'has_password': has_password}


class UserSettings(BaseModel):
    """Partial update payload — only provided keys are merged into existing settings."""
    settings: dict[str, Any]

class UserSignup(BaseModel):
    first_name: str
    last_name: str
    user_name: str | None = None
    email: EmailStr | None = None
    password: str
    signup_key: UserSignupKey
    security_question: Optional[SecurityQuestion] = None
    security_answer: Optional[str] = None

    @model_validator(mode='after')
    def _require_security_question_without_email(self):
        if not self.email and not (self.security_question and self.security_answer and self.security_answer.strip()):
            raise ValueError('A security question and answer are required when signing up without an email')
        return self

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
    signup_key: str
    email: Optional[EmailStr] = None
    purpose: Optional[str] = None

class UserNameCheckRequest(BaseModel):
    user_name: str

class UserNameCheckResponse(BaseModel):
    is_available: bool

class ResetMechanismRequestPayload(BaseModel):
    identifier: EmailStr | str
