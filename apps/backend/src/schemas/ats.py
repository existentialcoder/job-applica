from pydantic import BaseModel
from typing import Optional


class ATSReport(BaseModel):
    score: float  # 0.0 – 100.0
    matched_skills: list[str]
    missing_skills: list[str]
    suggestions: list[str]
    resume_id: Optional[int] = None


class ATSScoreRequest(BaseModel):
    """Score request tied to a saved job."""
    resume_id: Optional[int] = None  # omit to use the user's default CV


class ATSQuickScoreRequest(BaseModel):
    """Score request for an unsaved job — pass raw JD text from the extension."""
    job_description: str
    required_skills: list[str] = []   # from the extraction step; ensures score matches dashboard
    resume_id: Optional[int] = None   # omit to use the user's default CV
