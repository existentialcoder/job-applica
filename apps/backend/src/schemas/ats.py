from pydantic import BaseModel


class ATSReport(BaseModel):
    score: float  # 0.0 – 100.0
    matched_skills: list[str]
    matched_experience: list[str] = []
    missing_skills: list[str]
    experience_gaps: list[str] = []
    suggestions: list[str]
    resume_id: int | None = None


class ATSScoreRequest(BaseModel):
    """Score request tied to a saved job."""

    resume_id: int | None = None  # omit to use the user's default CV


class ATSQuickScoreRequest(BaseModel):
    """Score request for an unsaved job — pass raw JD text from the extension."""

    job_description: str
    required_skills: list[str] = []  # from the extraction step; ensures score matches dashboard
    resume_id: int | None = None  # omit to use the user's default CV
