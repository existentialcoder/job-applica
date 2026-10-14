from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.crypto import decrypt, encrypt
from ..models.company import Company
from ..models.profile import ProfileContact, UserProfile
from ..models.resume import Resume
from ..schemas.profile import ContactDetails, ProfileFields, ProfileResponse, ProfileUpdate
from ..services import company as company_service

CONTACT_FIELDS = tuple(ContactDetails.model_fields)


async def get_profile(db: AsyncSession, user_id: int) -> ProfileResponse | None:
    profile = await db.scalar(select(UserProfile).where(UserProfile.user_id == user_id))
    if profile is None:
        return None
    contact = await db.scalar(select(ProfileContact).where(ProfileContact.user_id == user_id))
    source_name = (
        await db.scalar(select(Resume.original_name).where(Resume.id == profile.source_resume_id))
        if profile.source_resume_id
        else None
    )
    stored = ProfileFields.model_validate(profile, from_attributes=True)
    names = {e.company for e in stored.experience if e.company}
    logos = dict(
        (await db.execute(select(Company.name, Company.logo_url).where(Company.name.in_(names)))).tuples().all()
    )
    return ProfileResponse(
        **stored.model_dump(),
        contacts=ContactDetails(**{f: decrypt(v) for f in CONTACT_FIELDS if contact and (v := getattr(contact, f))}),
        auto_filled=[f for f, source in profile.field_sources.items() if source == 'auto'],
        company_logos={name: logos.get(name) for name in names},
        source_resume_name=source_name,
        confirmed_at=profile.confirmed_at,
    )


async def save_profile(db: AsyncSession, user_id: int, update: ProfileUpdate) -> ProfileResponse:
    """Create or update the profile; any field the user changes stops counting as auto-filled."""
    profile = await db.scalar(select(UserProfile).where(UserProfile.user_id == user_id))
    if profile is None:
        # No CV was read (or extraction failed): the user fills the form in by hand.
        profile = UserProfile(user_id=user_id, field_sources={})
        db.add(profile)
    before = ProfileFields.model_validate(profile, from_attributes=True).model_dump()
    after = ProfileFields(**update.model_dump()).model_dump()
    sources = dict(profile.field_sources)
    for field, value in after.items():
        if value != before[field]:
            setattr(profile, field, value)
            sources[field] = 'user'
    profile.field_sources = sources
    for entry in update.experience:
        if entry.company:
            await company_service.get_or_create_company(db, entry.company, entry.company_website)
    if update.confirm and profile.confirmed_at is None:
        profile.confirmed_at = datetime.now(UTC)

    contact = await db.scalar(select(ProfileContact).where(ProfileContact.user_id == user_id))
    if contact is None:
        contact = ProfileContact(user_id=user_id)
        db.add(contact)
    for field in CONTACT_FIELDS:
        value = getattr(update.contacts, field)
        setattr(contact, field, encrypt(value) if value else None)

    await db.commit()
    result = await get_profile(db, user_id)
    assert result is not None  # just written
    return result
