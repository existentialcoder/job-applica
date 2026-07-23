import re
import secrets
from datetime import datetime, timedelta, timezone
from enum import Enum
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ....schemas import user as schemas
from ....core.config import settings
from ....core.constants import Constants
from ....core.utils import create_token, hash_password, verify_password
from ...deps.auth import get_current_user
from ...deps.db import get_db
from ....services import user as user_service
from ....services import oauth as oauth_service
from ....services import connected_accounts as ca_service
from ....services.email import email_service
from ....services.email_theme import resolve_email_theme
from ....models.user import User

router = APIRouter(prefix='/auth')

class ResetMechanism(str, Enum):
    otp = 'otp'
    security_question = 'security_question'

class RefreshRequest(BaseModel):
    refresh_token: str

class ResetMechanismRequest(BaseModel):
    user_identifier: EmailStr | str

class VerifyResetMechanismResponse(BaseModel):
    is_valid: bool
    token: str | None

class ResetMechanismResponse(BaseModel):
    mechanism: ResetMechanism
    context: dict = {}

class VerifyResetMechanismRequest(BaseModel):
    user_identifier: EmailStr | str
    mechanism: ResetMechanism
    question: str | None = None
    answer: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@router.get('/me', response_model=schemas.UserBase, description='Get current user profile')
def get_me(current_user: schemas.UserBase = Depends(get_current_user)):
    return current_user


@router.post('/refresh', description='Exchange a refresh token for a new access token')
async def refresh_token(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        token_data = user_service.decode_token(payload.refresh_token)
    except HTTPException:
        raise HTTPException(status_code=401, detail='Invalid or expired refresh token')

    result = await db.execute(select(User).where(User.id == int(token_data.sub)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail='User not found')

    new_payload = {
        'sub': str(user.id),
        'user_name': user.user_name,
        'signup_key': user.signup_key,
        'email': user.email,
    }
    access_token = create_token(
        new_payload,
        expiry=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        expiry_type='minutes',
        secret=settings.AUTH_SECRET,
        algorithm=Constants.AUTH_ALGORITHM,
    )
    return {'access_token': access_token, 'token_type': 'Bearer'}


@router.post('/signup', description='User signup API')
async def signup_user(user_data: schemas.UserSignup, db: AsyncSession = Depends(get_db)):
    if not user_data.email and not user_data.user_name:
        raise HTTPException(status_code=400, detail='Either email or user_name must be provided')
    return await user_service.create_user(db, user_data)


@router.post('/login', response_model=schemas.UserLoginTokenResponse, description='User Login API')
async def login(login_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    return await user_service.user_login(db, login_data)


# ── Google OAuth ──────────────────────────────────────────────────────────────

@router.get('/google', description='Redirect to Google OAuth consent screen')
def google_login(origin: str = 'web'):
    url = ca_service.google_auth_url(origin=origin)
    return RedirectResponse(url)


@router.get('/google/callback', description='Google OAuth callback — handles both login and scope upgrades')
async def google_callback(code: str, state: str = '', db: AsyncSession = Depends(get_db)):
    if not code:
        raise HTTPException(status_code=400, detail='Missing authorization code')

    state_data = ca_service.verify_state(state) or {}
    origin = state_data.get('origin', 'web')
    purpose = state_data.get('purpose', 'login')

    result = await oauth_service.exchange_google_code(code)
    user_info = result['user_info']

    if purpose == 'upgrade':
        user_id = state_data.get('user_id')
        if not user_id:
            raise HTTPException(status_code=400, detail='Invalid upgrade state')
        await ca_service.upsert(
            db=db,
            user_id=int(user_id),
            provider='google',
            provider_user_id=user_info.get('sub', ''),
            provider_email=user_info.get('email'),
            display_name=f"{user_info.get('given_name', '')} {user_info.get('family_name', '')}".strip(),
            avatar_url=user_info.get('picture'),
            access_token=result['access_token'],
            refresh_token=result.get('refresh_token'),
            expires_in=result.get('expires_in'),
            scopes=result['scopes'],
        )
        return RedirectResponse(f'{settings.FRONTEND_URL}/plugins?connected=google')

    user = await oauth_service.get_or_create_oauth_user(
        db=db,
        provider='google',
        provider_id=user_info.get('sub', ''),
        email=user_info.get('email', ''),
        first_name=user_info.get('given_name', ''),
        last_name=user_info.get('family_name', ''),
        avatar_url=user_info.get('picture'),
        access_token=result['access_token'],
        refresh_token=result.get('refresh_token'),
        expires_in=result.get('expires_in'),
        scopes=result['scopes'],
    )

    tokens = oauth_service.create_tokens_for_user(user)
    relay_path = '/auth/relay' if origin == 'extension' else '/auth/callback'
    redirect_url = (
        f'{settings.FRONTEND_URL}{relay_path}'
        f'?access_token={tokens.access_token}'
        f'&refresh_token={tokens.refresh_token}'
    )
    return RedirectResponse(redirect_url)


# ── LinkedIn OAuth ────────────────────────────────────────────────────────────

@router.get('/linkedin', description='Redirect to LinkedIn OAuth consent screen')
def linkedin_login(origin: str = 'web'):
    url = oauth_service.get_linkedin_auth_url(origin)
    return RedirectResponse(url)


@router.get('/linkedin/callback', description='LinkedIn OAuth callback')
async def linkedin_callback(code: str, state: str = '', db: AsyncSession = Depends(get_db)):
    if not code:
        raise HTTPException(status_code=400, detail='Missing authorization code')

    origin = state.split(':')[0] if ':' in state else 'web'

    result = await oauth_service.exchange_linkedin_code(code)
    user_info = result['user_info']

    user = await oauth_service.get_or_create_oauth_user(
        db=db,
        provider='linkedin',
        provider_id=user_info.get('sub', ''),
        email=user_info.get('email', ''),
        first_name=user_info.get('given_name', ''),
        last_name=user_info.get('family_name', ''),
        avatar_url=user_info.get('picture'),
        access_token=result['access_token'],
        refresh_token=result.get('refresh_token'),
        expires_in=result.get('expires_in'),
        scopes=result['scopes'],
    )

    tokens = oauth_service.create_tokens_for_user(user)
    relay_path = '/auth/relay' if origin == 'extension' else '/auth/callback'
    redirect_url = (
        f'{settings.FRONTEND_URL}{relay_path}'
        f'?access_token={tokens.access_token}'
        f'&refresh_token={tokens.refresh_token}'
    )
    return RedirectResponse(redirect_url)

@router.get('/get-reset-mechanism', description='API to get the reset password mechanism based on user status')
async def get_retry_mechanism(user_identifier: str, db: AsyncSession = Depends(get_db)) -> ResetMechanismResponse:
    is_email = bool(re.match(Constants.EMAIL_REGEX, user_identifier))

    get_user_handler = user_service.get_user_by_email if is_email else user_service.get_user_by_user_name
    target_user = await get_user_handler(db, user_identifier)

    # If security_question is provided always use it
    if target_user.security_question:
        return ResetMechanismResponse(mechanism='security_question', context={
            'security_question': target_user.security_question
        })

    return ResetMechanismResponse(mechanism='otp', context={'request_for_email': is_email == False})


@router.get('/request-reset-otp', description='API to send a one-time password to the email on file for password reset')
async def request_reset_otp(user_identifier: str, db: AsyncSession = Depends(get_db)):
    is_email = bool(re.match(Constants.EMAIL_REGEX, user_identifier))

    get_user_handler = user_service.get_user_by_email if is_email else user_service.get_user_by_user_name
    target_user = await get_user_handler(db, user_identifier)

    if not target_user.email:
        raise HTTPException(status_code=400, detail='No email on file for this account')

    otp_code = f'{secrets.randbelow(1_000_000):06d}'
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=Constants.OTP_EXPIRE_MINUTES)

    target_user.settings = {
        **target_user.settings,
        'otp': {
            'value': hash_password(otp_code),
            'expires_at': expires_at.isoformat(),
        },
    }
    await db.commit()

    await email_service.send_template_email(
        to=target_user.email,
        subject='Your password reset code',
        template_name='otp_code.html',
        context={
            'otp_code': otp_code,
            'expires_in_minutes': Constants.OTP_EXPIRE_MINUTES,
            'theme': resolve_email_theme(target_user.settings),
        },
    )

    return {'ok': True}


@router.post('/verify-reset-mechanism', description='API to verify the security question and answer to reset password')
async def verify_reset_mechanism(payload: VerifyResetMechanismRequest, db: AsyncSession = Depends(get_db)):
    user_identifier = payload.user_identifier

    is_email = bool(re.match(Constants.EMAIL_REGEX, user_identifier))

    get_user_handler = user_service.get_user_by_email if is_email else user_service.get_user_by_user_name
    target_user = await get_user_handler(db, user_identifier)

    if payload.mechanism == ResetMechanism.security_question and target_user.security_question != payload.question:
        raise HTTPException(status_code=401, detail='Invalid security question')
    if payload.mechanism == ResetMechanism.otp:
        otp_expires_at = target_user.settings.get('otp', {}).get('expires_at')
        if not otp_expires_at:
            raise HTTPException(status_code=401, detail='OTP has expired')
        expiry = datetime.fromisoformat(otp_expires_at)
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        if expiry < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail='OTP has expired')

    token_data: schemas.TokenPayload = {
        'sub': str(target_user.id),
        'user_name': target_user.user_name,
        'signup_key': target_user.signup_key,
        'email': target_user.email,
        'purpose': 'password_reset',
    }

    if payload.mechanism == ResetMechanism.security_question:
        is_valid = bool(target_user.hashed_security_answer) and verify_password(payload.answer, target_user.hashed_security_answer)
    else:
        stored_otp_hash = target_user.settings.get('otp', {}).get('value')
        is_valid = bool(stored_otp_hash) and verify_password(payload.answer, stored_otp_hash)

    token = create_token(token_data,
        expiry=Constants.RESET_TOKEN_EXPIRE_MINUTES,
        expiry_type='minutes',
        secret=settings.AUTH_SECRET,
        algorithm=Constants.AUTH_ALGORITHM
    ) if is_valid else None

    if payload.mechanism == ResetMechanism.otp and is_valid:
        target_user.settings = {**target_user.settings, 'otp': {}}
        await db.commit()

    return VerifyResetMechanismResponse(is_valid=is_valid, token=token)


@router.post('/reset-password', description='API to set a new password using a verified password-reset token')
async def reset_password(payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    try:
        token_data = user_service.decode_token(payload.token)
    except HTTPException:
        raise HTTPException(status_code=401, detail='Invalid or expired reset token')

    if token_data.purpose != 'password_reset':
        raise HTTPException(status_code=401, detail='Invalid or expired reset token')

    result = await db.execute(select(User).where(User.id == int(token_data.sub)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    user.hashed_password = hash_password(payload.new_password)
    await db.commit()

    return {'ok': True}
