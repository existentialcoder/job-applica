import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from uuid import UUID

from src import models, schemas, controller, database

# Create tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title='Job Applica API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

# --- Dependencies ---
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Job Endpoints ---
@app.post('/jobs/', response_model=schemas.Job)
def create_job(job: schemas.JobBase, db: Session = Depends(get_db)):
    return controller.create_job(db, job)

@app.get('/jobs/{job_id}', response_model=schemas.Job)
def get_job(job_id: UUID, db: Session = Depends(get_db)):
    db_job = controller.get_job(db, job_id)
    if not db_job:
        raise HTTPException(status_code=404, detail='Job not found')
    return db_job

@app.get('/jobs/', response_model=list[schemas.Job])
def get_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return controller.get_jobs(db, skip, limit)

@app.put('/jobs/{job_id}', response_model=schemas.Job)
def update_job(job_id: UUID, job_update: schemas.JobBase, db: Session = Depends(get_db)):
    db_job = controller.update_job(db, job_id, job_update)
    if not db_job:
        raise HTTPException(status_code=404, detail='Job not found')
    return db_job

@app.delete('/jobs/{job_id}')
def delete_job(job_id: UUID, db: Session = Depends(get_db)):
    success = controller.delete_job(db, job_id)
    if not success:
        raise HTTPException(status_code=404, detail='Job not found')
    return {'detail': 'Job deleted'}
