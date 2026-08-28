import enum
from typing import Any

from pydantic import BaseModel, EmailStr, model_validator

from .base import BaseSchema
from .settings import UserSettings


class UserSignupKey(enum.StrEnum):
    USER_NAME = 'USER_NAME'
    EMAIL = 'EMAIL'


class SecurityQuestion(enum.StrEnum):
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

    @model_validator(mode='before')
    @classmethod
    def _derive_has_password(cls, data: Any) -> Any:
        hashed_password = (
            data.get('hashed_password') if isinstance(data, dict) else getattr(data, 'hashed_password', None)
        )
        has_password = bool(hashed_password)
        if isinstance(data, dict):
            return {**data, 'has_password': has_password}
        return {**{field: getattr(data, field, None) for field in cls.model_fields}, 'has_password': has_password}


class UserSettingsRequest(BaseModel):
    settings: UserSettings


class UserSignup(BaseModel):
    first_name: str
    last_name: str
    user_name: str | None = None
    email: EmailStr | None = None
    password: str
    signup_key: UserSignupKey
    security_question: SecurityQuestion | None = None
    security_answer: str | None = None

    @model_validator(mode='after')
    def _require_security_question_without_email(self):
        if not self.email and not (self.security_question and self.security_answer and self.security_answer.strip()):
            raise ValueError('A security question and answer are required when signing up without an email')
        return self


class UserLoginTokenResponse(BaseModel):
    message: str
    access_token: str
    refresh_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: str
    user_name: str
    signup_key: str
    email: EmailStr | None = None
    purpose: str | None = None


class UserNameCheckRequest(BaseModel):
    user_name: str


class UserNameCheckResponse(BaseModel):
    is_available: bool


class ResetMechanismRequestPayload(BaseModel):
    identifier: EmailStr | str
