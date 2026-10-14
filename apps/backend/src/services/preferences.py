from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.profile import JobPreference
from ..schemas.preferences import JobPreferences


async def get_preferences(db: AsyncSession, user_id: int) -> JobPreferences | None:
    row = await db.scalar(select(JobPreference).where(JobPreference.user_id == user_id))
    return JobPreferences.model_validate(row) if row else None


async def save_preferences(db: AsyncSession, user_id: int, prefs: JobPreferences) -> JobPreferences:
    row = await db.scalar(select(JobPreference).where(JobPreference.user_id == user_id))
    if row is None:
        row = JobPreference(user_id=user_id)
        db.add(row)
    for field, value in prefs.model_dump(mode='json').items():
        setattr(row, field, value)
    await db.commit()
    return prefs
