from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ....schemas import job as schemas
from ...deps.db import get_db
from ...deps.pagination import pagination_params
from ....services import job as job_service

router = APIRouter(prefix='/jobs')

@router.get('', response_model=job_service.PaginatedJobs, description='List all jobs')
def list_jobs(filters: schemas.JobFilterParams = Depends(), pagination: dict = Depends(pagination_params), db: Session = Depends(get_db)):
    return job_service.get_jobs(db, pagination, filters)

@router.get('/{job_id}', response_model=schemas.JobBase)
def get_job(job_id: int, db: Session = Depends(get_db)):
    db_job = job_service.get_job(db, job_id)
    if not db_job:
        raise HTTPException(status_code=404, detail='Job not found')
    return db_job

@router.post('/', response_model=schemas.JobBase, description='Create a new job')
def create_job(job_in: schemas.JobCreate, db: Session = Depends(get_db)):
    return job_service.create_job(db, job_in)


@router.patch('/{job_id}', response_model=schemas.JobBase, description='Update existing job')
def update_job(job_id: int, job_update: schemas.JobUpdate, db: Session = Depends(get_db)):
    db_job = job_service.update_job(db, job_id, job_update)
    if not db_job:
        raise HTTPException(status_code=404, detail='Job not found')

    return db_job

@router.delete('/{job_id}', description='Delete existing job')
def delete_job(job_id: int, db: Session = Depends(get_db)):
    success = job_service.delete_job(db, job_id)
    if not success:
        raise HTTPException(status_code=404, detail='Job not found')
    return {'detail': 'Job deleted'}
