import hashlib

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ....api.deps.auth import get_current_user
from ....api.deps.db import get_db
from ....schemas.user import UserBase
from ....schemas.ats import ATSReport, ATSScoreRequest, ATSQuickScoreRequest
from ....services import ats as ats_service
from ....services.job import get_job_with_id
from ....models.user import User

# ── Job-tied scoring ──────────────────────────────────────────────────────────
router = APIRouter(prefix='/jobs')


_CACHE_VERSION = 6  # bump this to invalidate all stored ATS reports

def _content_hash(resume_text: str, jd: str) -> str:
    return hashlib.sha256(f'{resume_text}\x00{jd}'.encode()).hexdigest()[:24]


@router.post('/{job_id}/ats-score', response_model=ATSReport)
async def calculate_ats_score(
    job_id: int,
    payload: ATSScoreRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    """Score the user's CV against a saved job. Returns cached result when JD and CV are unchanged."""
    job = await get_job_with_id(db, current_user, job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Job not found')

    user_result = await db.execute(select(User).where(User.id == current_user.id))
    user = user_result.scalar_one_or_none()

    # Resolve which resume will be used so we can check the cache before calling the LLM
    resume = (
        await ats_service.get_resume(db, user.id, payload.resume_id) if payload.resume_id
        else await ats_service.get_default_resume(db, user.id)
    )
    if not resume or not resume.parsed_text or not job.description:
        raise HTTPException(status_code=422, detail='Cannot score: missing resume text or job description')

    current_hash = _content_hash(resume.parsed_text, job.description)
    cached = job.ats_report or {}

    if (
        cached.get('_hash') == current_hash
        and cached.get('_version') == _CACHE_VERSION
        and cached.get('score') is not None
    ):
        return ATSReport(
            score=cached['score'],
            matched_skills=cached.get('matched_skills', []),
            missing_skills=cached.get('missing_skills', []),
            suggestions=cached.get('suggestions', []),
            resume_id=cached.get('resume_id'),
        )

    report = await ats_service.score_job(db, user, job, resume_id=resume.id)
    if not report:
        raise HTTPException(status_code=422, detail='Cannot score: missing resume text or job description')

    job.ats_score = report.score
    job.ats_resume_id = report.resume_id
    job.ats_report = {**report.model_dump(), '_hash': current_hash, '_version': _CACHE_VERSION}
    await db.commit()

    return report


quick_router = APIRouter(prefix='/ats')


@quick_router.post('/quick-score', response_model=ATSReport)
async def quick_ats_score(
    payload: ATSQuickScoreRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    """Score the user's CV against a raw job description. Ephemeral — nothing is persisted.

    All plans receive the full LLM report. Free users are bounded by the 100-scan/month
    extraction limit, which already caps the total LLM cost to an acceptable level.
    """
    user_result = await db.execute(select(User).where(User.id == current_user.id))
    user = user_result.scalar_one_or_none()

    report = await ats_service.score_quick(
        db, user,
        job_description=payload.job_description,
        required_skills=payload.required_skills,
        resume_id=payload.resume_id,
    )
    if not report:
        raise HTTPException(
            status_code=422,
            detail='Cannot score: no CV found. Upload a resume in your profile first.',
        )

    return report
