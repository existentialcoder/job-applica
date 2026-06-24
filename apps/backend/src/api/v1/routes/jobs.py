from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ....schemas import job as schemas
from ....schemas.user import UserBase
from ...deps.auth import get_current_user
from ...deps.db import get_db
from ...deps.pagination import pagination_params
from ....services import job as job_service

router = APIRouter(prefix='/jobs')

@router.get('', response_model=job_service.PaginatedJobs, description='List all jobs')
async def list_jobs(user: UserBase = Depends(get_current_user), filters: schemas.JobFilterParams = Depends(), pagination: dict = Depends(pagination_params), db: AsyncSession = Depends(get_db)):
    return await job_service.get_jobs(db, user, pagination, filters)

@router.get('/{job_id}', response_model=schemas.JobBase)
async def get_job(job_id: int, user: UserBase = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    db_job = await job_service.get_job(db, user, job_id)
    if not db_job:
        raise HTTPException(status_code=404, detail='Job not found')
    return db_job

@router.post('/', response_model=schemas.JobBase, description='Create a new job')
async def create_job(job_in: schemas.JobCreate, user: UserBase = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await job_service.create_job(db, user, job_in)

@router.patch('/{job_id}', response_model=schemas.JobBase, description='Update existing job')
async def update_job(job_id: int, job_update: schemas.JobUpdate, user: UserBase = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    db_job = await job_service.update_job(db, job_id, user, job_update)
    if not db_job:
        raise HTTPException(status_code=404, detail='Job not found')
    return db_job

@router.delete('/{job_id}', description='Delete existing job')
async def delete_job(job_id: int, user: UserBase = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    success = await job_service.delete_job(db, user, job_id)
    if not success:
        raise HTTPException(status_code=404, detail='Job not found')
    return {'detail': 'Job deleted'}
