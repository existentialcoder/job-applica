from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import HttpUrl
from fastapi import HTTPException

from ..models.company import Company
from ..schemas.company import CompanyBase, CompanyCreate
from ..api.deps.pagination import build_paginated_response, get_paginated_response_model, paginate_query

PaginatedCompanies = get_paginated_response_model(CompanyBase)


async def get_companies(db: AsyncSession, pagination: dict) -> PaginatedCompanies:
    count_result = await db.execute(select(func.count()).select_from(Company))
    total = count_result.scalar()

    result = await db.execute(paginate_query(select(Company), pagination))
    companies = [CompanyBase.model_validate(c) for c in result.scalars().all()]

    return build_paginated_response(items=companies, total=total, **pagination)


async def create_company(db: AsyncSession, company_data: CompanyCreate) -> CompanyBase:
    result = await db.execute(select(Company).where(Company.name == company_data.name))
    if result.scalars().first():
        raise HTTPException(status_code=409, detail='Company already exists')

    company_obj = Company(**company_data.model_dump(exclude_unset=True))
    if isinstance(company_obj.website, HttpUrl):
        company_obj.website = str(company_obj.website)

    db.add(company_obj)
    await db.commit()
    await db.refresh(company_obj)
    return CompanyBase.model_validate(company_obj)
