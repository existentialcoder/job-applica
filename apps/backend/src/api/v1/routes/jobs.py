from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ....schemas import job as schemas
from ....schemas.user import UserBase
from ....models.job import Job
from ...deps.auth import get_current_user
from ...deps.db import get_db
from ...deps.pagination import pagination_params
from ...deps.plan import plan_gate, extraction_gate
from ....services import job as job_service
from ....services import plan as plan_service
from ....services import llm as llm_service

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

@router.post(
    '/',
    response_model=schemas.JobBase,
    description='Create a new job',
    dependencies=[plan_gate('max_job_applications', lambda uid: select(func.count(Job.id)).where(Job.user_id == uid))],
)
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


@router.post('/extract-from-page', response_model=schemas.JobExtractResult, dependencies=[extraction_gate()])
async def extract_job_from_page(
    payload: schemas.PageExtractRequest,
    current_user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        data = await llm_service.extract_job_from_page(payload.page_text, payload.url)
        result = schemas.JobExtractResult(**data)
    except Exception:
        return schemas.JobExtractResult(is_job_page=False)

    if result.is_job_page:
        await plan_service.increment_extraction_count(db, current_user)

    return result
