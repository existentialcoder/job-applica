from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....schemas.user import UserBase
from ....services import location as location_service
from ...deps.auth import get_current_user
from ...deps.db import get_db

router = APIRouter(prefix='/locations')


@router.get('/cities', response_model=list[str], description="List distinct cities used across the current user's jobs")
async def list_cities(
    search: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    user: UserBase = Depends(get_current_user),
):
    return await location_service.get_distinct_cities(db, user_id=user.id, search=search)
