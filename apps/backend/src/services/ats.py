import re

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.resume import Resume
from ..models.job import Job
from ..models.user import User
from ..schemas.ats import ATSReport
from .llm import ats_score_report


async def get_resume(db: AsyncSession, user_id: int, resume_id: int) -> Resume | None:
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_default_resume(db: AsyncSession, user_id: int) -> Resume | None:
    result = await db.execute(
        select(Resume).where(Resume.user_id == user_id, Resume.is_default == True)
    )
    resume = result.scalar_one_or_none()
    if resume:
        return resume
    # Fall back to the most recently uploaded resume
    result = await db.execute(
        select(Resume).where(Resume.user_id == user_id).order_by(Resume.id.desc()).limit(1)
    )
    return result.scalar_one_or_none()


_SKIP_WORDS = {
    'A', 'I', 'We', 'The', 'An', 'In', 'On', 'At', 'As', 'Be', 'Or', 'And', 'For',
    'With', 'From', 'Our', 'You', 'Are', 'Will', 'Have', 'Has', 'Can', 'May', 'Must',
    'This', 'That', 'They', 'Your', 'All', 'New', 'Any', 'Not', 'Use', 'Its', 'Our',
    'Who', 'Key', 'Job', 'Per', 'Via', 'Of', 'To', 'Do', 'By',
}

_SKILL_RE = re.compile(
    r'\b(?:[A-Z][a-zA-Z0-9+#.]*(?:\.[a-zA-Z0-9]+)*'
    r'|[A-Z]{2,}(?:[0-9]+)?'
    r'|[a-zA-Z][a-zA-Z0-9]*[-+#][a-zA-Z0-9+#]+)\b'
)


def calculate_free(resume_text: str, job_description: str) -> ATSReport:
    """No-LLM ATS score: TF-IDF cosine similarity + regex skill extraction."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity as _cosine

    try:
        vec = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), min_df=1)
        matrix = vec.fit_transform([resume_text.lower(), job_description.lower()])
        sim = float(_cosine(matrix[0:1], matrix[1:2])[0][0])
        score = round(min(sim * 150, 100.0), 1)
    except Exception:
        score = 0.0

    candidates = list(dict.fromkeys(_SKILL_RE.findall(job_description)))
    candidates = [c for c in candidates if c not in _SKIP_WORDS and len(c) > 1]

    matched, missing = [], []
    for term in candidates:
        pattern = r'(?<![A-Za-z0-9])' + re.escape(term) + r'(?![A-Za-z0-9])'
        if re.search(pattern, resume_text, re.IGNORECASE):
            matched.append(term)
        else:
            missing.append(term)

    suggestions: list[str] = []
    if score < 50:
        suggestions.append('Low keyword overlap — tailor your resume to mirror the job description language.')
    if missing:
        suggestions.append(f'Consider highlighting: {", ".join(missing[:5])}')

    return ATSReport(
        score=score,
        matched_skills=matched[:20],
        missing_skills=missing[:15],
        suggestions=suggestions,
    )


async def calculate_score(
    resume_text: str,
    job_description: str,
    required_skills: list[str],
) -> ATSReport:
    return await ats_score_report(resume_text, job_description, required_skills)


# ── Public scoring entry points ───────────────────────────────────────────────

async def score_job(
    db: AsyncSession,
    user: User,
    job: Job,
    resume_id: int | None = None,
) -> ATSReport | None:
    resume = (
        await get_resume(db, user.id, resume_id) if resume_id
        else await get_default_resume(db, user.id)
    )
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
    resume = (
        await get_resume(db, user.id, resume_id) if resume_id
        else await get_default_resume(db, user.id)
    )
    if not resume or not resume.parsed_text:
        return None

    report = await calculate_score(resume.parsed_text, job_description, required_skills or [])
    report.resume_id = resume.id
    return report
