from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ....schemas import user as schemas
from ....core.config import settings
from ....core.constants import Constants
from ....core.utils import create_token
from ...deps.auth import get_current_user
from ...deps.db import get_db
from ....services import user as user_service
from ....services import oauth as oauth_service
from ....services import connected_accounts as ca_service
from ....models.user import User

router = APIRouter(prefix='/auth')


class RefreshRequest(BaseModel):
    refresh_token: str


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
