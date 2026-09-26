import io
from collections.abc import Sequence

import pdfplumber
from docx import Document
from fastapi import HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.resume import Resume
from ..models.skill import Skill
from ..models.user import User
from ..services.llm import extract_skills_from_resume
from ..utils.file_storage import get_file_storage_factory

ALLOWED_TYPES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
}
MAX_SIZE_MB = 5


def _parse_resume_text(content_type: str | None, data: bytes) -> str:
    if content_type == 'application/pdf':
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            return '\n'.join(page.extract_text() or '' for page in pdf.pages)

    doc = Document(io.BytesIO(data))
    return '\n'.join([p.text for p in doc.paragraphs])


async def list_resumes(db: AsyncSession, user_id: int) -> Sequence[Resume]:
    result = await db.execute(select(Resume).where(Resume.user_id == user_id).order_by(Resume.id.desc()))
    return result.scalars().all()


async def upload_resume(db: AsyncSession, user_id: int, file: UploadFile) -> Resume:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail='Only PDF and Word documents are accepted')

    file_storage = get_file_storage_factory()(destination_path=f'{user_id}/resumes', file=file, max_size_mb=MAX_SIZE_MB)
    key, size = await file_storage.upload()
    await file.seek(0)
    parsed_text = _parse_resume_text(file.content_type, await file.read())

    if not parsed_text.strip():
        await file_storage.delete_file(key)
        raise HTTPException(
            status_code=422,
            detail='Could not extract any text from this file — try a different export or format',
        )

    existing_count_result = await db.execute(select(func.count(Resume.id)).where(Resume.user_id == user_id))
    is_first = existing_count_result.scalar() == 0

    resume = Resume(
        user_id=user_id,
        original_name=file.filename or file_storage.stored_name,
        stored_name=file_storage.stored_name,
        file_path=key,
        file_size=size,
        parsed_text=parsed_text,
        is_default=is_first,
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)

    return resume


async def _sync_extracted_skills(db: AsyncSession, user_id: int, resume_text: str) -> None:
    """Extract skills from resume text, create any that don't exist yet, and link to user profile.

    Normalisation: lookup is case-insensitive so 'python' and 'Python' resolve
    to the same row. The first-seen casing wins (stored as-is from Claude output,
    which produces canonical names like 'Python', 'FastAPI', 'PostgreSQL').
    """
    extracted = await extract_skills_from_resume(resume_text)
    if not extracted:
        return

    user_row = await db.execute(select(User).where(User.id == user_id))
    user = user_row.scalar_one_or_none()
    if not user:
        return

    existing_ids = {s.id for s in user.skills}

    for name in extracted:
        # Case-insensitive lookup — avoids duplicates like 'python' vs 'Python'
        result = await db.execute(select(Skill).where(func.lower(Skill.name) == name.lower()))
        skill = result.scalar_one_or_none()

        if skill is None:
            # First time this skill appears — create it from the extracted name
            skill = Skill(name=name, label=name)
            db.add(skill)
            await db.flush()  # get skill.id without committing

        if skill.id not in existing_ids:
            user.skills.append(skill)
            existing_ids.add(skill.id)

    await db.commit()


async def delete_resume(db: AsyncSession, user_id: int, resume_id: int) -> None:
    result = await db.execute(select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail='Resume not found')

    await get_file_storage_factory()().delete_file(f'{user_id}/resumes/{resume.stored_name}')
    await db.delete(resume)
    await db.commit()


async def sync_skills_background(user_id: int, resume_text: str) -> None:
    """Run after upload in a background task — creates its own DB session."""
    from ..db.session import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        await _sync_extracted_skills(db, user_id, resume_text)


async def set_default_resume(db: AsyncSession, user_id: int, resume_id: int) -> Resume:
    existing = await db.execute(select(Resume).where(Resume.user_id == user_id, Resume.is_default == True))
    for r in existing.scalars().all():
        r.is_default = False

    result = await db.execute(select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail='Resume not found')

    resume.is_default = True
    await db.commit()
    await db.refresh(resume)
    return resume
