import sqlalchemy
from sqlalchemy.orm import Session
from ..models.job import Job
from ..schemas.job import JobBase
from ..api.deps.pagination import paginate_query

# allowed_job_query_fields = [JobBase.title, JobBase.description, JobBase.company]

def get_jobs(db: Session, pagination: dict, query: str | None = None) -> list[JobBase]:
    # query maybe like this query="company: Acme Inc,location: Remote"
    q = db.query(Job)

    # if query:
    #     query_filters = []
    #     for field in allowed_job_query_fields:
    #         query_filters.append(getattr(JobBase, field).ilike(f'%{query}%'))
    #     q = q.filter(sqlalchemy.or_(*query_filters))
    return paginate_query(q, pagination)
