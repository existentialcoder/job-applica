import hashlib

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....api.deps.auth import get_current_user
from ....api.deps.db import get_db
from ....models.job import JobAtsScore
from ....models.user import User
from ....schemas.ats import ATSQuickScoreRequest, ATSReport, ATSScoreRequest
from ....schemas.user import UserBase
from ....services import ats as ats_service
from ....services.job import get_job_with_id

# ── Job-tied scoring ──────────────────────────────────────────────────────────
router = APIRouter(prefix='/jobs')


_CACHE_VERSION = 6  # bump this to invalidate all stored ATS reports


def _content_hash(resume_text: str, jd: str) -> str:
    return f'{_CACHE_VERSION}:' + hashlib.sha256(f'{resume_text}\x00{jd}'.encode()).hexdigest()[:24]


async def _latest_score(db: AsyncSession, job_id: int) -> JobAtsScore | None:
    return await db.scalar(
        select(JobAtsScore).where(JobAtsScore.job_id == job_id).order_by(JobAtsScore.created_at.desc()).limit(1)
    )


def _to_report(row: JobAtsScore) -> ATSReport:
    # Rows backfilled from older report versions may lack some list fields.
    return ATSReport.model_validate(
        {'matched_skills': [], 'missing_skills': [], 'suggestions': [], **row.report}
        | {'score': row.score, 'resume_id': row.resume_id}
    )


@router.get('/{job_id}/ats-score', response_model=ATSReport | None)
async def get_latest_ats_score(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    """Latest match report for a saved job, or null if it was never scored."""
    if not await get_job_with_id(db, current_user, job_id):
        raise HTTPException(status_code=404, detail='Job not found')
    latest = await _latest_score(db, job_id)
    return _to_report(latest) if latest else None


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
    user = user_result.scalar_one()

    # Resolve which resume will be used so we can check the cache before calling the LLM
    resume = (
        await ats_service.get_resume(db, user.id, payload.resume_id)
        if payload.resume_id
        else await ats_service.get_default_resume(db, user.id)
    )
    if not resume:
        raise HTTPException(status_code=404, detail='Resume not found')
    if not resume.parsed_text:
        raise HTTPException(status_code=422, detail='Resume has no extracted text — try re-uploading it')
    if not job.description:
        raise HTTPException(status_code=422, detail='Job has no description to score against')

    current_hash = _content_hash(resume.parsed_text, job.description)
    latest = await _latest_score(db, job.id)
    if latest and latest.input_hash == current_hash:
        return _to_report(latest)

    report = await ats_service.score_job(db, user, job, resume_id=resume.id)
    if not report:
        raise HTTPException(status_code=422, detail='Cannot score: missing resume text or job description')

    job.ats_score = report.score
    db.add(
        JobAtsScore(
            job_id=job.id,
            resume_id=report.resume_id,
            score=report.score,
            report=report.model_dump(),
            input_hash=current_hash,
        )
    )
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
    user = user_result.scalar_one()

    report = await ats_service.score_quick(
        db,
        user,
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
