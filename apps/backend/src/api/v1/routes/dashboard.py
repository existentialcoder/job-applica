from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api.deps.auth import get_current_user
from src.api.deps.db import get_db
from src.schemas.dashboard import DashboardStats
from src.schemas.user import UserBase
from src.services import dashboard as dashboard_service

router = APIRouter()


@router.get('/dashboard/stats', response_model=DashboardStats)
def get_stats(
    board_id: Optional[int] = Query(None),
    current_user: UserBase = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return dashboard_service.get_dashboard_stats(db, current_user.id, board_id=board_id)
