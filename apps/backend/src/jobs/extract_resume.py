"""Background job: turn an uploaded CV into a read-only snapshot. The user's first CV also creates their profile.

Runs in-process after the upload response (FastAPI BackgroundTasks), so a restart can interrupt it;
resume_interrupted() picks those up again on startup.
"""

import hashlib
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.countries import COUNTRIES
from ..core.crypto import encrypt
from ..core.exceptions import PlanLimitReached
from ..db.session import AsyncSessionLocal
from ..models.profile import ProfileContact, UserProfile
from ..models.resume import Resume, ResumeSnapshot
from ..models.skill import Skill
from ..models.user import User, user_skill_table
from ..schemas.profile import ExtractedProfile, Location
from ..services import company as company_service
from ..services import llm
from ..services import plan as plan_service
from ..services.redaction import RedactionLeak, contacts_from, redact
from ..services.skill import extract_skill_name_from_label

logger = logging.getLogger(__name__)

# ponytail: only rows idle this long are re-run on startup, so a job interrupted within its first 2 minutes
# stays pending (the page gives up after ~45 s and offers another upload); move to a job table if that bites.
INTERRUPTED_AFTER = timedelta(minutes=2)

# 'pending': waiting for or reading with the AI; 'filling': writing the snapshot, profile and companies.
IN_PROGRESS = ('pending', 'filling')

# Part of every snapshot's content_hash: bump it when the extraction prompt or schema changes, so a CV
# re-uploaded afterwards is extracted again instead of reusing a snapshot built by the old prompt.
EXTRACTION_VERSION = 4

PROFILE_FIELDS = (
    'headline',
    'current_title',
    'current_company',
    'years_experience',
    'summary',
    'experience',
    'education',
    'languages',
    'certifications',
    'awards',
)


async def extract_resume(resume_id: int) -> None:
    async with AsyncSessionLocal() as db:
        resume = await db.get(Resume, resume_id)
        if resume is None or resume.extraction_status != 'pending':
            return
        try:
            resume.extraction_status = await _extract(db, resume)
            await db.commit()
            return
        except Exception:
            logger.exception('CV extraction failed for resume %s', resume_id)
            await db.rollback()
        await db.execute(
            update(Resume)
            .where(Resume.id == resume_id, Resume.extraction_status.in_(IN_PROGRESS))
            .values(extraction_status='failed')
        )
        await db.commit()


async def resume_interrupted() -> None:
    """Re-run extractions a restart cut short. Bumping updated_at claims a row, so two workers never both take it."""
    async with AsyncSessionLocal() as db:
        ids = await db.scalars(
            update(Resume)
            .where(
                Resume.extraction_status.in_(IN_PROGRESS),
                Resume.updated_at < datetime.now(UTC) - INTERRUPTED_AFTER,
            )
            .values(extraction_status='pending', updated_at=func.now())
            .returning(Resume.id)
        )
        claimed = ids.all()
        await db.commit()
    for resume_id in claimed:
        await extract_resume(resume_id)


async def _extract(db: AsyncSession, resume: Resume) -> str:
    assert resume.parsed_text  # upload rejects files with no text
    user = await db.get(User, resume.user_id)
    assert user is not None  # resumes cascade-delete with their user
    has_profile = await db.scalar(select(UserProfile.id).where(UserProfile.user_id == user.id)) is not None
    found = redact(resume.parsed_text, (user.first_name, user.last_name))
    content_hash = hashlib.sha256(f'{EXTRACTION_VERSION}:{resume.parsed_text}'.encode()).hexdigest()

    same_text = await db.scalar(
        select(ResumeSnapshot).where(ResumeSnapshot.user_id == user.id, ResumeSnapshot.content_hash == content_hash)
    )
    counted = False
    if same_text is not None:
        extracted = ExtractedProfile.model_validate(same_text, from_attributes=True)
    else:
        # The CV that creates the profile is the first step of signing up, so it never counts against the plan.
        if has_profile:
            if await _over_extraction_limit(db, user):
                return 'limit_reached'
            counted = True
        try:
            result = await llm.extract_profile(found.text)
        except RedactionLeak:
            return 'failed'
        if result is None:
            return 'failed'
        extracted = result

    # The AI part is done; tell the "Reading your CV" screen it's on its last stage.
    resume.extraction_status = 'filling'
    await db.commit()

    role = extracted.current_role()
    values = {
        'headline': extracted.headline,
        'current_title': role.title if role else None,
        'current_company': role.company if role else None,
        'years_experience': extracted.years_experience,
        'summary': extracted.summary,
        'experience': [e.model_dump() for e in extracted.experience],
        'education': [e.model_dump() for e in extracted.education],
        'languages': [e.model_dump() for e in extracted.languages],
        'certifications': [e.model_dump() for e in extracted.certifications],
        'awards': [e.model_dump() for e in extracted.awards],
    }
    now = datetime.now(UTC)
    db.add(
        ResumeSnapshot(
            resume_id=resume.id,
            user_id=user.id,
            skills=extracted.skills,
            content_hash=content_hash,
            extracted_at=now,
            **values,
        )
    )
    if not has_profile:
        db.add(
            UserProfile(
                user_id=user.id,
                source_resume_id=resume.id,
                field_sources=dict.fromkeys(PROFILE_FIELDS, 'auto'),
                extracted_at=now,
                **values,
            )
        )
        # A contact row can outlive its profile (e.g. a profile removed by hand), so fill it in rather than insert.
        contact = await db.scalar(select(ProfileContact).where(ProfileContact.user_id == user.id))
        if contact is None:
            contact = ProfileContact(user_id=user.id)
            db.add(contact)
        details = contacts_from(found, user.email)
        if extracted.location:
            details |= {k: v for k, v in _place(extracted.location).items() if v}
        for field, value in details.items():
            setattr(contact, field, encrypt(value))
    for entry in extracted.experience:
        if entry.company:
            await company_service.get_or_create_company(db, entry.company, entry.company_website)
    await _link_skills(db, user.id, resume.id, extracted.skills)
    if counted:
        await plan_service.increment_extraction_count(db, user)
    return 'done'


def _place(location: Location) -> dict[str, str | None]:
    """City as written; country spelled the way the app's country list spells it, when it's one we know."""
    country = (location.country or '').strip()
    known = next((name for name, _ in COUNTRIES.values() if name.lower() == country.lower()), None)
    return {'city': (location.city or '').strip() or None, 'country': known or country or None}


async def _over_extraction_limit(db: AsyncSession, user: User) -> bool:
    if not settings.CHECK_PLAN_LIMIT:
        return False
    try:
        await plan_service.check_plan_limit(
            db, user.id, user.plan, 'max_monthly_extractions', plan_service.extraction_count(user.id)
        )
    except PlanLimitReached:
        return True
    return False


async def _link_skills(db: AsyncSession, user_id: int, resume_id: int, names: list[str]) -> None:
    """Add the CV's skills as source='cv'; skills the user already has keep their source, so a CV never removes them."""
    linked = set(await db.scalars(select(user_skill_table.c.skill_id).where(user_skill_table.c.user_id == user_id)))
    seen: set[str] = set()
    for label in (n.strip() for n in names):
        # Same normalized key the skills API uses, so 'Node.js' from a CV and from the UI are one skill.
        key = extract_skill_name_from_label(label)
        if not key or key in seen:
            continue
        seen.add(key)
        skill = await db.scalar(select(Skill).where(Skill.name == key))
        if skill is None:
            skill = Skill(name=key, label=label)
            db.add(skill)
            await db.flush()
        if skill.id not in linked:
            await db.execute(
                insert(user_skill_table).values(user_id=user_id, skill_id=skill.id, source='cv', resume_id=resume_id)
            )
            linked.add(skill.id)
