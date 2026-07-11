import os
import uuid
from docx import Document
from pypdf import PdfReader
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..models.resume import Resume
from ..models.skill import Skill
from ..models.user import User
from ..core.config import settings
from ..utils.file_uploader import FileUploader
from ..services import plan as plan_service
from ..services.llm import extract_skills_from_resume

UPLOAD_BASE = os.path.join(os.path.dirname(__file__), '..', '..', 'uploads')
ALLOWED_TYPES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
}
MAX_SIZE_MB = 5

def _parse_resume_text(file: UploadFile, dest: str) -> str:
    if file.content_type == 'application/pdf':
        with open(dest, 'rb') as f:
            reader = PdfReader(f)
            text = ''
            for page in reader.pages:
                text += page.extract_text() or ''
            return text

    doc = Document(dest)
    return '\n'.join([p.text for p in doc.paragraphs])


async def list_resumes(db: AsyncSession, user_id: int) -> list[Resume]:
    result = await db.execute(
        select(Resume).where(Resume.user_id == user_id).order_by(Resume.id.desc())
    )
    return result.scalars().all()


async def upload_resume(db: AsyncSession, user_id: int, plan: str, file: UploadFile) -> tuple[Resume, dict | None]:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail='Only PDF and Word documents are accepted')

    warning = None
    if settings.APP_ENV != 'local':
        warning = await plan_service.check_plan_limit(
            db, user_id, plan, 'max_resumes',
            select(func.count(Resume.id)).where(Resume.user_id == user_id),
        )

    ext = os.path.splitext(file.filename or 'resume')[1] or '.pdf'
    stored_name = f'{uuid.uuid4().hex}{ext}'
    user_resume_dir = os.path.join(UPLOAD_BASE, str(user_id), 'resumes')
    dest = os.path.join(user_resume_dir, stored_name)
    r2_key = f'{user_id}/resumes/{stored_name}'

    uploader = FileUploader(destination_path=dest, file=file, max_size_mb=MAX_SIZE_MB)
    # Always write to disk first — _parse_resume_text reads from dest
    size = await uploader.upload_local()
    parsed_text = _parse_resume_text(file, dest)

    if settings.APP_ENV != 'local':
        # Push the already-saved local file to R2; UploadFile stream is exhausted at this point
        await uploader.upload_disk_to_cloudflare(
            bucket=settings.CLOUDFLARE_R2_BUCKET_NAME,
            key=r2_key,
            content_type=file.content_type or 'application/octet-stream',
        )

    existing_count_result = await db.execute(
        select(func.count(Resume.id)).where(Resume.user_id == user_id)
    )
    is_first = existing_count_result.scalar() == 0

    resume = Resume(
        user_id=user_id,
        original_name=file.filename or stored_name,
        stored_name=stored_name,
        file_path=dest,
        file_size=size,
        parsed_text=parsed_text,
        is_default=is_first,
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)

    return resume, warning


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
        result = await db.execute(
            select(Skill).where(func.lower(Skill.name) == name.lower())
        )
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
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail='Resume not found')

    uploader = FileUploader(destination_path=resume.file_path)
    if settings.APP_ENV == 'local':
        await uploader.delete_file_from_local()
    else:
        await uploader.delete_file_from_cloudflare(
            bucket=settings.CLOUDFLARE_R2_BUCKET_NAME,
            key=f'{user_id}/resumes/{resume.stored_name}',
        )
    await db.delete(resume)
    await db.commit()


async def sync_skills_background(user_id: int, resume_text: str) -> None:
    """Run after upload in a background task — creates its own DB session."""
    from ..db.session import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        await _sync_extracted_skills(db, user_id, resume_text)


async def set_default_resume(db: AsyncSession, user_id: int, resume_id: int) -> Resume:
    existing = await db.execute(
        select(Resume).where(Resume.user_id == user_id, Resume.is_default == True)
    )
    for r in existing.scalars().all():
        r.is_default = False

    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail='Resume not found')

    resume.is_default = True
    await db.commit()
    await db.refresh(resume)
    return resume
