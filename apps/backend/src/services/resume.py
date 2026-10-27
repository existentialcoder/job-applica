from collections.abc import Sequence

from fastapi import HTTPException, UploadFile
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.profile import ProfileContact, UserProfile
from ..models.resume import Resume
from ..models.user import user_skill_table
from ..utils.file_storage import get_file_storage_factory
from .cv_text import cv_text

ALLOWED_TYPES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
}
MAX_SIZE_MB = 5


async def list_resumes(db: AsyncSession, user_id: int) -> Sequence[Resume]:
    result = await db.execute(select(Resume).where(Resume.user_id == user_id).order_by(Resume.id.desc()))
    return result.scalars().all()


async def get_resume(db: AsyncSession, user_id: int, resume_id: int) -> Resume:
    resume = await db.scalar(select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id))
    if not resume:
        raise HTTPException(status_code=404, detail='Resume not found')
    return resume


async def upload_resume(db: AsyncSession, user_id: int, file: UploadFile) -> Resume:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail='Only PDF and Word documents are accepted')

    file_storage = get_file_storage_factory()(destination_path=f'{user_id}/resumes', file=file, max_size_mb=MAX_SIZE_MB)
    key, size = await file_storage.upload()
    await file.seek(0)
    parsed_text = cv_text(file.content_type, await file.read())

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
        extraction_status='pending',
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)

    return resume


async def replace_resume(db: AsyncSession, user_id: int, resume_id: int, file: UploadFile) -> Resume:
    """Swap a CV for a new file and drop everything built from the old one, so extraction starts the profile afresh.

    The new file is stored first: if it's rejected, the old CV and profile are untouched. Skills the user added
    by hand stay; only those taken from the old CV go.
    """
    old = await get_resume(db, user_id, resume_id)
    was_default = old.is_default
    new = await upload_resume(db, user_id, file)

    await db.execute(
        delete(user_skill_table).where(
            user_skill_table.c.user_id == user_id,
            user_skill_table.c.resume_id == old.id,
            user_skill_table.c.source == 'cv',
        )
    )
    await db.execute(delete(UserProfile).where(UserProfile.user_id == user_id))
    await db.execute(delete(ProfileContact).where(ProfileContact.user_id == user_id))
    new.is_default = was_default or new.is_default
    await delete_resume(db, user_id, old.id)  # commits the lot
    await db.refresh(new)
    return new


async def delete_resume(db: AsyncSession, user_id: int, resume_id: int) -> None:
    result = await db.execute(select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail='Resume not found')

    await get_file_storage_factory()().delete_file(f'{user_id}/resumes/{resume.stored_name}')
    await db.delete(resume)
    await db.commit()


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
