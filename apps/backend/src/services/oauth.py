import secrets
import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.constants import Constants
from ..core.utils import create_token
from ..models.user import User
from ..schemas.user import UserLoginTokenResponse, TokenPayload

GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'

LINKEDIN_AUTH_URL = 'https://www.linkedin.com/oauth/v2/authorization'
LINKEDIN_TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
LINKEDIN_USERINFO_URL = 'https://api.linkedin.com/v2/userinfo'


def _make_redirect_uri(provider: str) -> str:
    return f'{settings.BACKEND_URL}/api/v1/auth/{provider}/callback'


def get_google_auth_url(origin: str = 'web') -> str:
    state = f'{origin}:{secrets.token_urlsafe(16)}'
    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': _make_redirect_uri('google'),
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
        'access_type': 'offline',
        'prompt': 'select_account',
    }
    query = '&'.join(f'{k}={v}' for k, v in params.items())
    return f'{GOOGLE_AUTH_URL}?{query}'


def get_linkedin_auth_url(origin: str = 'web') -> str:
    state = f'{origin}:{secrets.token_urlsafe(16)}'
    params = {
        'response_type': 'code',
        'client_id': settings.LINKEDIN_CLIENT_ID,
        'redirect_uri': _make_redirect_uri('linkedin'),
        'state': state,
        'scope': 'openid profile email',
    }
    query = '&'.join(f'{k}={v}' for k, v in params.items())
    return f'{LINKEDIN_AUTH_URL}?{query}'


async def exchange_google_code(code: str) -> dict:
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(GOOGLE_TOKEN_URL, data={
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': _make_redirect_uri('google'),
            'grant_type': 'authorization_code',
        })
    if token_resp.status_code != 200:
        raise HTTPException(status_code=400, detail='Failed to exchange Google code')
    token_data = token_resp.json()

    async with httpx.AsyncClient() as client:
        info_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={'Authorization': f'Bearer {token_data["access_token"]}'},
        )
    if info_resp.status_code != 200:
        raise HTTPException(status_code=400, detail='Failed to fetch Google user info')
    return info_resp.json()


async def exchange_linkedin_code(code: str) -> dict:
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(LINKEDIN_TOKEN_URL, data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': _make_redirect_uri('linkedin'),
            'client_id': settings.LINKEDIN_CLIENT_ID,
            'client_secret': settings.LINKEDIN_CLIENT_SECRET,
        }, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    if token_resp.status_code != 200:
        raise HTTPException(status_code=400, detail='Failed to exchange LinkedIn code')
    token_data = token_resp.json()

    async with httpx.AsyncClient() as client:
        info_resp = await client.get(
            LINKEDIN_USERINFO_URL,
            headers={'Authorization': f'Bearer {token_data["access_token"]}'},
        )
    if info_resp.status_code != 200:
        raise HTTPException(status_code=400, detail='Failed to fetch LinkedIn user info')
    return info_resp.json()


def get_or_create_oauth_user(db: Session, provider: str, provider_id: str, email: str,
                              first_name: str, last_name: str, avatar_url: str | None) -> User:
    id_field = User.google_id if provider == 'google' else User.linkedin_id

    valid_signup_keys = {'USER_NAME', 'EMAIL'}

    user = db.query(User).filter(id_field == provider_id).first()
    if user:
        changed = False
        if user.signup_key not in valid_signup_keys:
            user.signup_key = 'USER_NAME'
            changed = True
        if avatar_url and not user.avatar_url:
            user.avatar_url = avatar_url
            changed = True
        if changed:
            db.commit()
            db.refresh(user)
        return user

    if email:
        user = db.query(User).filter(User.email == email).first()
        if user:
            setattr(user, f'{provider}_id', provider_id)
            if user.signup_key not in valid_signup_keys:
                user.signup_key = 'USER_NAME'
            if avatar_url and not user.avatar_url:
                user.avatar_url = avatar_url
            db.commit()
            db.refresh(user)
            return user

    base_username = (email.split('@')[0] if email else f'{first_name}{last_name}').lower()
    user_name = base_username
    suffix = 1
    while db.query(User).filter(User.user_name == user_name).first():
        user_name = f'{base_username}{suffix}'
        suffix += 1

    user = User(
        first_name=first_name,
        last_name=last_name,
        user_name=user_name,
        email=email or None,
        signup_key='USER_NAME',
        hashed_password=None,
        avatar_url=avatar_url,
    )
    setattr(user, f'{provider}_id', provider_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_tokens_for_user(user: User) -> UserLoginTokenResponse:
    token_data: TokenPayload = {
        'sub': str(user.id),
        'user_name': user.user_name,
        'signup_key': user.signup_key,
        'email': user.email,
    }
    access_token = create_token(
        token_data,
        expiry=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        expiry_type='minutes',
        secret=settings.AUTH_SECRET,
        algorithm=Constants.AUTH_ALGORITHM,
    )
    refresh_token = create_token(
        token_data,
        expiry=settings.REFRESH_TOKEN_EXPIRE_DAYS,
        expiry_type='days',
        secret=settings.AUTH_SECRET,
        algorithm=Constants.AUTH_ALGORITHM,
    )
    return UserLoginTokenResponse(
        message='Successfully logged in via OAuth',
        access_token=access_token,
        refresh_token=refresh_token,
        token_type='Bearer',
    )
