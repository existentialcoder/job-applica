from sqlalchemy.orm import Session
from .models import Job
from .schemas import JobBase
from passlib.context import CryptContext
from uuid import UUID

# pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")


# def create_user(db: Session, user: UserCreate) -> User:
#     hashed_password = pwd_context.hash(user.password)
#     db_user = User(**user.dict(exclude={"password"}), password=hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user

# def get_user(db: Session, user_id: UUID) -> User | None:
#     return db.query(User).filter(User.user_id == user_id).first()

# def get_users(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(User).offset(skip).limit(limit).all()


# --- JOB CRUD ---
def create_job(db: Session, job: JobBase) -> Job:
    db_job = Job(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_job(db: Session, job_id: UUID) -> Job | None:
    return db.query(Job).filter(Job.job_id == job_id).first()

def get_jobs(db: Session, skip: int, limit: int, job_title: str | None = None):
    query = db.query(Job)
    if job_title:
        query = query.filter(Job.job_title.ilike(f"%{job_title}%"))
    return query.offset(skip).limit(limit).all()

def update_job(db: Session, job_id: UUID, job_update: JobBase) -> Job | None:
    db_job = db.query(Job).filter(Job.job_id == job_id).first()
    if not db_job:
        return None
    for key, value in job_update.dict(exclude_unset=True).items():
        setattr(db_job, key, value)
    db.commit()
    db.refresh(db_job)
    return db_job

def delete_job(db: Session, job_id: UUID) -> bool:
    db_job = db.query(Job).filter(Job.job_id == job_id).first()
    if not db_job:
        return False
    db.delete(db_job)
    db.commit()
    return True
