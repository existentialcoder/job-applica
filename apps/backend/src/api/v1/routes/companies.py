from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ....schemas import company as schemas
from ...deps.db import get_db
from ...deps.pagination import pagination_params
from ....services import company as company_service

router = APIRouter(prefix='/companies')

@router.get('', response_model=company_service.PaginatedCompanies, description='List all companies')
def list_companies(pagination: dict = Depends(pagination_params), db: Session = Depends(get_db)):
    return company_service.get_companies(db, pagination)

# @router.get('/{company_id}', response_model=schemas.JobBase)
# def get_company(company_id: int, db: Session = Depends(get_db)):
#     db_job = company_service.get_company(db, company_id)
#     if not db_job:
#         raise HTTPException(status_code=404, detail='Job not found')
#     return db_job

@router.post('/', response_model=schemas.Company, description='Create a new company')
def create_company(company_data: schemas.CompanyCreate, db: Session = Depends(get_db)):
    return company_service.create_company(db, company_data)

# @router.delete('/{company_id}', description='Delete existing job')
# def delete_company(company_id: int, db: Session = Depends(get_db)):
#     success = company_service.delete_job(db, company_id)
#     if not success:
#         raise HTTPException(status_code=404, detail='Job not found')
#     return {'detail': 'Job deleted'}
