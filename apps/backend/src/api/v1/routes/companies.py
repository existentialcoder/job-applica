from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....schemas import company as schemas
from ....schemas.user import UserBase
from ...deps.auth import get_current_user
from ...deps.db import get_db
from ...deps.pagination import pagination_params
from ....services import company as company_service

router = APIRouter(prefix='/companies')

@router.get('', response_model=company_service.PaginatedCompanies, description='List companies for current user\'s jobs')
async def list_companies(
    search: str | None = Query(None),
    pagination: dict = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
    user: UserBase = Depends(get_current_user),
):
    return await company_service.get_companies(db, pagination, user_id=user.id, search=search)

@router.post('/', response_model=schemas.CompanyBase, description='Create a new company')
async def create_company(company_data: schemas.CompanyBase, db: AsyncSession = Depends(get_db)):
    return await company_service.create_company(db, company_data)
