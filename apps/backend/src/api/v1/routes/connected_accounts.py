from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ....schemas.connected_account import ConnectedAccountOut, ConnectUrlResponse
from ....schemas.user import UserBase
from ....services import connected_accounts as ca_service
from ...deps.auth import get_current_user
from ...deps.db import get_db

router = APIRouter(prefix='/connected-accounts')

VALID_PROVIDERS = {'google', 'linkedin'}
VALID_FEATURES = {'gmail', 'calendar'}


@router.get('', response_model=list[ConnectedAccountOut])
async def list_connected_accounts(
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ca_service.list_for_user(db, current_user.id)


@router.get('/google/connect', response_model=ConnectUrlResponse)
def get_google_connect_url(
    features: str = '',
    current_user: UserBase = Depends(get_current_user),
):
    requested = [f.strip() for f in features.split(',') if f.strip() in VALID_FEATURES]
    url = ca_service.google_auth_url(
        origin='web',
        user_id=current_user.id,
        features=requested or None,
    )
    return ConnectUrlResponse(url=url)


@router.delete('/{provider}', status_code=204)
async def disconnect_provider(
    provider: str,
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if provider not in VALID_PROVIDERS:
        raise HTTPException(status_code=400, detail=f'Unknown provider: {provider}')
    if not await ca_service.disconnect(db, current_user.id, provider):
        raise HTTPException(status_code=404, detail='Account not connected')
