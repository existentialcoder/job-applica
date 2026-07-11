import json
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..core.config import settings
from ..core.exceptions import PlanLimitReached

WARN_THRESHOLD = 0.8


def _get_limit(plan: str, resource: str) -> int:
    return settings.PLAN_LIMITS.get(plan, settings.PLAN_LIMITS['free']).get(resource, -1)


async def check_plan_limit(
    db: AsyncSession,
    user_id: int,
    plan: str,
    resource: str,
    count_query,
) -> dict | None:
    limit = _get_limit(plan, resource)
    if limit == -1:
        return None  # unlimited

    result = await db.execute(count_query)
    current = result.scalar()

    if current >= limit:
        raise PlanLimitReached(resource=resource, current=current, limit=limit, plan=plan)

    remaining = limit - current
    if current >= limit * WARN_THRESHOLD:
        return {'resource': resource, 'current': current, 'limit': limit, 'remaining': remaining}

    return None


def warning_header(warning: dict | None) -> dict:
    if not warning:
        return {}
    return {'X-Plan-Warning': json.dumps(warning)}


def _current_month() -> str:
    return datetime.utcnow().strftime('%Y-%m')


def _extraction_count(user_settings: dict) -> int:
    """Return this month's extraction count from user.settings, resetting if month changed."""
    data = user_settings.get('ext_extractions', {})
    if data.get('month') != _current_month():
        return 0
    return data.get('count', 0)


def check_extraction_limit(plan: str, user_settings: dict) -> None:
    """Raise PlanLimitReached if the user has exhausted their monthly extraction quota."""
    limit = _get_limit(plan, 'max_monthly_extractions')
    if limit == -1:
        return
    current = _extraction_count(user_settings)
    if current >= limit:
        raise PlanLimitReached(
            resource='monthly_extractions',
            current=current,
            limit=limit,
            plan=plan,
        )


async def increment_extraction_count(db: AsyncSession, user) -> None:
    """Increment the monthly extraction counter for a confirmed job-page scan."""
    limit = _get_limit(user.plan, 'max_monthly_extractions')
    if limit == -1:
        return
    month = _current_month()
    count = _extraction_count(user.settings)
    user.settings = {**user.settings, 'ext_extractions': {'month': month, 'count': count + 1}}
    await db.commit()
