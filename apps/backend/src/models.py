from sqlalchemy import Column, String, Integer, Enum, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid
# from enums import JobStatus

Base = declarative_base()

# class User(Base):
#     __tablename__ = 'users'

#     user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     first_name = Column(String, nullable=False)
#     last_name = Column(String, nullable=False)
#     email = Column(String, unique=True, nullable=False)
#     password = Column(String, nullable=False)
#     skills = Column(ARRAY(String))

#     jobs = relationship('Job', back_populates='user')


class Job(Base):
    __tablename__ = 'jobs'

    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=False)
    status = Column(String, nullable=False)
    category = Column(String, nullable=False)
    salary_range = Column(String)
    required_skills = Column(ARRAY(String))
    job_description = Column(String)
    min_years_of_experience = Column(Integer)
    max_years_of_experience = Column(Integer)
