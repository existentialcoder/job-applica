from typing import Callable, Any

from fastapi import Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import settings
from ...services import plan as plan_service
from ...schemas.user import UserBase
from .auth import get_current_user
from .db import get_db


def plan_gate(resource: str, count_fn: Callable[[int], Any]):
    """Dependency factory that enforces a plan resource limit and injects the warning header."""
    async def dep(
        user: UserBase = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        response: Response = None,
    ):
        if not settings.CHECK_PLAN_LIMIT:
            return
        warning = await plan_service.check_plan_limit(
            db, user.id, user.plan, resource, count_fn(user.id)
        )
        response.headers.update(plan_service.warning_header(warning))

    return Depends(dep)


def extraction_gate():
    """Dependency that enforces the monthly extraction quota."""
    async def dep(user: UserBase = Depends(get_current_user)):
        if not settings.CHECK_PLAN_LIMIT:
            return
        plan_service.check_extraction_limit(user.plan, user.settings)

    return Depends(dep)
