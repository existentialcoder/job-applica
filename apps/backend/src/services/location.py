from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.job import Job


async def get_distinct_locations(
    db: AsyncSession, user_id: int | None, search: str | None = None, limit: int = 20
) -> list[str]:
    city = Job.location['city'].astext
    q = select(city).distinct().where(Job.user_id == user_id, city.is_not(None))
    if search:
        q = q.where(city.ilike(f'%{search}%'))

    result = await db.execute(q.order_by(city).limit(limit))
    return list(result.scalars().all())
