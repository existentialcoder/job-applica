from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.job import Job
from ..models.location import Location


async def get_distinct_cities(
    db: AsyncSession, user_id: int | None, search: str | None = None, limit: int = 20
) -> list[str]:
    q = (
        select(Location.city)
        .join(Job, Job.location_id == Location.id)
        .where(Job.user_id == user_id, Location.city.is_not(None))
        .distinct()
    )
    if search:
        q = q.where(Location.city.ilike(f'%{search}%'))

    result = await db.execute(q.order_by(Location.city).limit(limit))
    return list(result.scalars().all())
