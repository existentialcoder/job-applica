from pydantic import BaseModel


class StageInfo(BaseModel):
    key: str
    label: str
    color: str | None = None


class OverviewStats(BaseModel):
    total_saved: int
    total_applied: int
    total_interviews: int
    total_offers: int
    total_rejected: int
    total_withdrawn: int
    total_ghosted: int
    total_stuck: int
    total_active: int
    response_rate: float
    interview_rate: float
    offer_rate: float


class StageCount(BaseModel):
    stage: str
    count: int


class WeekCount(BaseModel):
    week: str
    count: int


class PlatformCount(BaseModel):
    platform: str
    count: int


class CompanyCount(BaseModel):
    company: str
    count: int


class DashboardStats(BaseModel):
    stages: list[StageInfo]
    overview: OverviewStats
    by_stage: list[StageCount]
    by_week: list[WeekCount]
    by_platform: list[PlatformCount]
    top_companies: list[CompanyCount]
