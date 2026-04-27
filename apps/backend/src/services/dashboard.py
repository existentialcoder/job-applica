from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models.job import Job
from src.models.company import Company
from src.models.board import Board, DEFAULT_STAGES
from src.schemas.dashboard import (
    DashboardStats, OverviewStats, StageCount, StageInfo, WeekCount, PlatformCount, CompanyCount,
)

GHOST_DAYS = 14
STUCK_DAYS = 7

# Terminal stages that don't count as "active" in the pipeline.
# Jobs in these keys are excluded from stuck/ghosted metrics.
TERMINAL_KEYS = {'Rejected', 'Withdrawn', 'Saved'}


def _load_stages(db: Session, user_id: int, board_id: int | None) -> list[dict]:
    """Return the ordered stage list for the given board (or the default board)."""
    if board_id is not None:
        board = db.query(Board).filter(Board.id == board_id, Board.user_id == user_id).first()
        if board and board.stages:
            return board.stages
    else:
        default = db.query(Board).filter(Board.user_id == user_id, Board.is_default == True).first()
        if default and default.stages:
            return default.stages
    return DEFAULT_STAGES


def get_dashboard_stats(db: Session, user_id: int, board_id: int | None = None) -> DashboardStats:
    q = db.query(Job).filter(Job.user_id == user_id)
    if board_id is not None:
        q = q.filter(Job.board_id == board_id)
    all_jobs = q.all()

    raw_stages = _load_stages(db, user_id, board_id)
    stage_keys  = [s['key'] for s in raw_stages]
    active_keys = {s['key'] for s in raw_stages if s['key'] not in TERMINAL_KEYS}
    # "First non-saved active stage" is used for ghosted detection
    applied_key = next((s['key'] for s in raw_stages if s['key'] not in TERMINAL_KEYS), 'Applied')

    now          = datetime.now(timezone.utc)
    ghost_cutoff = now - timedelta(days=GHOST_DAYS)
    stuck_cutoff = now - timedelta(days=STUCK_DAYS)

    # ── Overview ─────────────────────────────────────────────────────────────
    total_saved      = sum(1 for j in all_jobs if j.status == 'Saved')
    total_applied    = sum(1 for j in all_jobs if j.status != 'Saved')
    total_offers     = sum(1 for j in all_jobs if j.status == 'Offer')
    total_rejected   = sum(1 for j in all_jobs if j.status == 'Rejected')
    total_withdrawn  = sum(1 for j in all_jobs if j.status == 'Withdrawn')
    total_active     = sum(1 for j in all_jobs if j.status in active_keys)

    # Interviews = all active stages beyond the first entry stage
    interview_keys = active_keys - {applied_key}
    total_interviews = sum(1 for j in all_jobs if j.status in interview_keys)

    total_ghosted = sum(
        1 for j in all_jobs
        if j.status == applied_key and j.updated_at and j.updated_at < ghost_cutoff
    )
    total_stuck = sum(
        1 for j in all_jobs
        if j.status in active_keys and j.updated_at and j.updated_at < stuck_cutoff
    )

    base           = total_applied or 1
    responded      = total_interviews + total_rejected + total_withdrawn + total_offers
    response_rate  = round(responded / base * 100, 1)
    interview_rate = round(total_interviews / base * 100, 1)
    offer_rate     = round(total_offers / base * 100, 1)

    # ── By stage ─────────────────────────────────────────────────────────────
    raw: dict[str, int] = {}
    for j in all_jobs:
        raw[j.status] = raw.get(j.status, 0) + 1

    by_stage = [StageCount(stage=k, count=raw.get(k, 0)) for k in stage_keys]

    # ── By week (last 12 weeks) ───────────────────────────────────────────────
    twelve_weeks_ago = now - timedelta(weeks=12)
    weekly: dict[str, int] = {}
    for j in all_jobs:
        ref = j.applied_date if j.applied_date else (j.created_at.date() if j.created_at else None)
        if ref is None:
            continue
        if hasattr(ref, 'date'):
            ref = ref.date()
        if ref < twelve_weeks_ago.date():
            continue
        week_start = ref - timedelta(days=ref.weekday())
        key = week_start.isoformat()
        weekly[key] = weekly.get(key, 0) + 1

    by_week = [WeekCount(week=k, count=v) for k, v in sorted(weekly.items())]

    # ── By platform ──────────────────────────────────────────────────────────
    plat: dict[str, int] = {}
    for j in all_jobs:
        if j.source_platform:
            p = j.source_platform.value if hasattr(j.source_platform, 'value') else str(j.source_platform)
            plat[p] = plat.get(p, 0) + 1

    by_platform = [
        PlatformCount(platform=k, count=v)
        for k, v in sorted(plat.items(), key=lambda x: -x[1])
    ]

    # ── Top companies ─────────────────────────────────────────────────────────
    company_q = (
        db.query(Company.name, func.count(Job.id).label('cnt'))
        .join(Job, Job.company_id == Company.id)
        .filter(Job.user_id == user_id)
    )
    if board_id is not None:
        company_q = company_q.filter(Job.board_id == board_id)
    rows = company_q.group_by(Company.name).order_by(func.count(Job.id).desc()).limit(8).all()
    top_companies = [CompanyCount(company=name, count=cnt) for name, cnt in rows]

    return DashboardStats(
        stages=[StageInfo(key=s['key'], label=s['label'], color=s['color']) for s in raw_stages],
        overview=OverviewStats(
            total_saved=total_saved,
            total_applied=total_applied,
            total_interviews=total_interviews,
            total_offers=total_offers,
            total_rejected=total_rejected,
            total_withdrawn=total_withdrawn,
            total_ghosted=total_ghosted,
            total_stuck=total_stuck,
            total_active=total_active,
            response_rate=response_rate,
            interview_rate=interview_rate,
            offer_rate=offer_rate,
        ),
        by_stage=by_stage,
        by_week=by_week,
        by_platform=by_platform,
        top_companies=top_companies,
    )
