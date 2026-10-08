import json
from datetime import UTC, datetime

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.exceptions import PlanLimitReached
from ..models.user import UsageCounter

WARN_THRESHOLD = 0.8
EXTRACTION_RESOURCE = 'monthly_extractions'


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
    current = result.scalar() or 0

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


def current_month() -> str:
    return datetime.now(UTC).strftime('%Y-%m')


async def increment_extraction_count(db: AsyncSession, user) -> None:
    """Increment the monthly extraction counter for a confirmed job-page scan."""
    if _get_limit(user.plan, 'max_monthly_extractions') == -1:
        return
    await db.execute(
        insert(UsageCounter)
        .values(user_id=user.id, resource=EXTRACTION_RESOURCE, period=current_month(), count=1)
        .on_conflict_do_update(
            constraint='uq_usage_counters_user_resource_period',
            set_={'count': UsageCounter.count + 1, 'updated_at': func.now()},
        )
    )
    await db.commit()
