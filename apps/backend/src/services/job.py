from typing import Type
from sqlalchemy.orm import Session
from ..models.job import Job
from ..schemas.job import JobBase, JobRead
from ..api.deps.pagination import build_paginated_response, get_paginated_response_model, paginate_query

# allowed_job_query_fields = [JobBase.title, JobBase.description, JobBase.company]

PaginatedJobs = get_paginated_response_model(JobBase)

def get_jobs(db: Session, pagination: dict, query: str | None = None) -> PaginatedJobs:
    # query maybe like this query="company: Acme Inc,location: Remote"
    q = db.query(Job)

    # Optional search filter
    # if query:
    #     filters = [getattr(Job, field).ilike(f"%{query}%") for field in allowed_job_query_fields]
    #     q = q.filter(or_(*filters))

    total = q.count()  # total before pagination
    q = paginate_query(q, pagination)

    results = q.all()

    # convert SQLAlchemy models to Pydantic
    jobs = [JobRead.from_orm(job) for job in results]

    return build_paginated_response(
        items=jobs,
        total=total,
        **pagination
    )
