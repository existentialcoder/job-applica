from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from ....schemas import job as schemas
from ...deps.db import get_db
from ...deps.pagination import pagination_params
from ....services import job as job_service

router = APIRouter(prefix='/jobs')

# @router.post('/', response_model=schemas.JobBase)
# def create_job(job_in: schemas.JobBase, db: Session = Depends(get_db)):
#     return job_service.create_job(db, job_in)

# @router.get('/{job_id}', response_model=schemas.JobBase)
# def get_job(job_id: UUID, db: Session = Depends(get_db)):
#     db_job = job_service.get_job(db, job_id)
#     if not db_job:
#         raise HTTPException(status_code=404, detail='Job not found')
#     return db_job

@router.get('/', response_model=list[schemas.JobBase])
def list_jobs(query: str | None = None, pagination: dict = Depends(pagination_params), db: Session = Depends(get_db)):
    return job_service.get_jobs(db, pagination, query)

# @router.put('/{job_id}', response_model=schemas.JobBase)
# def update_job(job_id: UUID, job_update: schemas.JobBase, db: Session = Depends(get_db)):
#     db_job = job_service.update_job(db, job_id, job_update)
#     if not db_job:
#         raise HTTPException(status_code=404, detail='Job not found')
#     return db_job

# @router.delete('/{job_id}')bs
# def delete_job(job_id: UUID, db: Session = Depends(get_db)):
#     success = job_service.delete_job(db, job_id)
#     if not success:
#         raise HTTPException(status_code=404, detail='Job not found')
#     return {'detail': 'Job deleted'}
