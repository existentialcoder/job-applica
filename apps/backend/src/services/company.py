from urllib.parse import urlparse

import httpx
from fastapi import HTTPException
from pydantic import HttpUrl
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..api.deps.pagination import PaginatedResponse, build_paginated_response, paginate_query
from ..core.constants import Constants
from ..models.company import Company
from ..models.job import Job
from ..schemas.company import CompanyBase, CompanyCreate

PaginatedCompanies = PaginatedResponse[CompanyBase]


async def get_company_by_id(db: AsyncSession, company_id: int) -> Company | None:
    result = await db.execute(select(Company).where(Company.id == company_id))
    return result.scalar_one_or_none()


async def get_company_by_name(db: AsyncSession, company_name: str) -> Company | None:
    result = await db.execute(select(Company).where(Company.name.ilike(company_name)))
    return result.scalar_one_or_none()


async def get_companies(
    db: AsyncSession, pagination: dict, user_id: int | None = None, search: str | None = None
) -> PaginatedCompanies:
    q = select(Company)
    if user_id is not None:
        # Only return companies linked to this user's jobs
        q = q.where(
            Company.id.in_(select(Job.company_id).where(Job.user_id == user_id, Job.company_id.is_not(None)).distinct())
        )
    if search:
        q = q.where(Company.name.ilike(f'%{search}%'))

    count_result = await db.execute(select(func.count()).select_from(q.subquery()))
    total = count_result.scalar() or 0

    result = await db.execute(paginate_query(q.order_by(Company.name), pagination))
    companies = [CompanyBase.model_validate(c) for c in result.scalars().all()]

    return build_paginated_response(items=companies, total=total, **pagination)


async def create_company(db: AsyncSession, company_data: CompanyCreate) -> Company:
    result = await db.execute(select(Company).where(Company.name == company_data.name))
    if result.scalars().first():
        raise HTTPException(status_code=409, detail='Company already exists')

    data = company_data.model_dump(exclude_unset=True)
    company_obj = Company(**data)
    if isinstance(company_obj.website, HttpUrl):
        company_obj.website = str(company_obj.website)
    if isinstance(company_obj.logo_url, HttpUrl):
        company_obj.logo_url = str(company_obj.logo_url)

    db.add(company_obj)
    await db.commit()
    await db.refresh(company_obj)
    return company_obj


async def derive_logo_url(website: str | HttpUrl | None) -> str | None:
    if not website:
        return None
    domain = urlparse(str(website)).netloc.lstrip('www.')
    if not domain:
        return None
    url = Constants.LOGO_URL_TEMPLATE.format(domain=domain)
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.head(url)
            return url if r.status_code == 200 else None
    except Exception:
        return None


async def get_or_create_company(db: AsyncSession, name: str, website: str | None = None) -> Company:
    """The tracker's company row for a name, created (with a logo when the website is known) if missing."""
    company = await get_company_by_name(db, name)
    if company is None:
        if website and '://' not in website:
            website = f'https://{website}'
        company = Company(name=name, website=website, logo_url=await derive_logo_url(website))
        db.add(company)
        await db.flush()
    elif website and not company.logo_url:
        company.logo_url = await derive_logo_url(website if '://' in website else f'https://{website}')
    return company
