from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr

# User schemas
# class UserBase(BaseModel):
#     first_name: str
#     last_name: str
#     email: EmailStr
#     skills: List[str] = []

# class UserCreate(UserBase):
#     password: str

# class User(UserBase):
#     user_id: UUID

#     class Config:
#         from_attributes = True


# Job schemas
class JobBase(BaseModel):
    job_title: str = ''
    company: str = ''
    location: str = ''
    status: str = ''
    category: str = ''
    salary_range: str = ''
    required_skills: List[str] = []
    job_description: Optional[str] = ""
    min_years_of_experience: int = 0
    max_years_of_experience: int = 0


class Job(JobBase):
    job_id: UUID

    class Config:
        from_attributes = True
