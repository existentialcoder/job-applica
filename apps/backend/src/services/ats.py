from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.job import Job
from ..models.resume import Resume
from ..models.user import User
from ..schemas.ats import ATSReport
from .llm import ats_score_report


async def get_resume(db: AsyncSession, user_id: int, resume_id: int) -> Resume | None:
    result = await db.execute(select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id))
    return result.scalar_one_or_none()


async def get_default_resume(db: AsyncSession, user_id: int) -> Resume | None:
    result = await db.execute(select(Resume).where(Resume.user_id == user_id, Resume.is_default == True))
    resume = result.scalar_one_or_none()
    if resume:
        return resume
    result = await db.execute(select(Resume).where(Resume.user_id == user_id).order_by(Resume.id.desc()).limit(1))
    return result.scalar_one_or_none()


async def calculate_score(
    resume_text: str,
    job_description: str,
    required_skills: list[str],
) -> ATSReport:
    return await ats_score_report(resume_text, job_description, required_skills)


async def score_job(
    db: AsyncSession,
    user: User,
    job: Job,
    resume_id: int | None = None,
) -> ATSReport | None:
    resume = await get_resume(db, user.id, resume_id) if resume_id else await get_default_resume(db, user.id)
    if not resume or not resume.parsed_text or not job.description:
        return None

    required_skills = [s.name for s in job.required_skills]
    report = await calculate_score(
        resume.parsed_text,
        job.description,
        required_skills,
    )
    report.resume_id = resume.id
    return report


async def score_quick(
    db: AsyncSession,
    user: User,
    job_description: str,
    required_skills: list[str] | None = None,
    resume_id: int | None = None,
) -> ATSReport | None:
    resume = await get_resume(db, user.id, resume_id) if resume_id else await get_default_resume(db, user.id)
    if not resume or not resume.parsed_text:
        return None

    report = await calculate_score(resume.parsed_text, job_description, required_skills or [])
    report.resume_id = resume.id
    return report
