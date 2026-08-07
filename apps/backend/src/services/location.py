from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.job import Job


async def get_distinct_locations(
    db: AsyncSession, user_id: int | None, search: str | None = None, limit: int = 20
) -> list[str]:
    q = select(Job.location).where(Job.user_id == user_id)
    if search:
        q = q.where(Job.location['city'].astext.ilike(f'%{search}%'))

    result = await db.execute(q.order_by(Job.location['city'].astext).limit(limit))
    return list(result.scalars().all())
