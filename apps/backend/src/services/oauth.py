import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.constants import Constants
from ..core.utils import create_token
from ..models.user import User
from ..schemas.user import UserLoginTokenResponse, TokenPayload
from . import connected_accounts as ca_service

GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'

LINKEDIN_AUTH_URL = 'https://www.linkedin.com/oauth/v2/authorization'
LINKEDIN_TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
LINKEDIN_USERINFO_URL = 'https://api.linkedin.com/v2/userinfo'


def _linkedin_redirect_uri() -> str:
    return f'{settings.BACKEND_URL}/api/v1/auth/linkedin/callback'


def get_linkedin_auth_url(origin: str = 'web') -> str:
    import secrets
    from urllib.parse import urlencode
    state = f'{origin}:{secrets.token_urlsafe(16)}'
    params = {
        'response_type': 'code',
        'client_id': settings.LINKEDIN_CLIENT_ID,
        'redirect_uri': _linkedin_redirect_uri(),
        'state': state,
        'scope': 'openid profile email',
    }
    return f'{LINKEDIN_AUTH_URL}?{urlencode(params)}'


async def exchange_google_code(code: str) -> dict:
    """Exchange auth code → returns {access_token, refresh_token, expires_in, scope, user_info}."""
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(GOOGLE_TOKEN_URL, data={
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': f'{settings.BACKEND_URL}/api/v1/auth/google/callback',
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

    granted_scopes = token_data.get('scope', '').split()

    return {
        'access_token': token_data['access_token'],
        'refresh_token': token_data.get('refresh_token'),
        'expires_in': token_data.get('expires_in', 3600),
        'scopes': granted_scopes,
        'user_info': info_resp.json(),
    }


async def exchange_linkedin_code(code: str) -> dict:
    """Exchange auth code → returns {access_token, expires_in, scopes, user_info}."""
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(LINKEDIN_TOKEN_URL, data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': _linkedin_redirect_uri(),
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

    return {
        'access_token': token_data['access_token'],
        'refresh_token': token_data.get('refresh_token'),
        'expires_in': token_data.get('expires_in', 3600),
        'scopes': ['openid', 'profile', 'email'],
        'user_info': info_resp.json(),
    }


def get_or_create_oauth_user(
    db: Session,
    provider: str,
    provider_id: str,
    email: str,
    first_name: str,
    last_name: str,
    avatar_url: str | None,
    access_token: str | None = None,
    refresh_token: str | None = None,
    expires_in: int | None = None,
    scopes: list[str] | None = None,
) -> User:
    # Look up by connected_accounts first
    user = ca_service.get_user_by_provider(db, provider, provider_id)

    if not user:
        # Fall back to email match (account merge)
        if email:
            user = db.query(User).filter(User.email == email).first()

    if not user:
        # New user — create
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
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        if avatar_url and not user.avatar_url:
            user.avatar_url = avatar_url
            db.commit()
            db.refresh(user)

    display_name = f'{first_name} {last_name}'.strip() or email

    # Always upsert the connected_account row — updates token + scopes on re-login
    ca_service.upsert(
        db=db,
        user_id=user.id,
        provider=provider,
        provider_user_id=provider_id,
        provider_email=email,
        display_name=display_name,
        avatar_url=avatar_url,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        scopes=scopes or [],
    )

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
