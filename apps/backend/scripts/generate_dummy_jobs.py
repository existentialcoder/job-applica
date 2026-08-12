"""
Insert dummy jobs into Postgres for a given user.

Run from apps/backend, with the project venv active:
python scripts/seed_dummy_jobs.py --user you@example.com [--file scripts/dummy_jobs_ats_v2.json]

The seed preserves the ATS report schema exactly as:

{
    "score": ...,
    "matched_skills": [...],
    "matched_experience": [...],
    "missing_skills": [...],
    "experience_gaps": [...],
    "suggestions": [...],
    "resume_id": ...,
    "_hash": "...",
    "_version": ...
}

If an ATS report is supplied with legacy keys such as `summary` or
`missing_keywords`, they are normalized before insertion. No extra keys are
written to `ats_report`.
"""

import argparse
import asyncio
import hashlib
import json
import os
import random
import sys
from datetime import UTC, date, datetime
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import AsyncSessionLocal
from src.models.board import DEFAULT_STAGES, Board
from src.models.company import Company
from src.models.job import Job
from src.models.resume import Resume
from src.models.skill import Skill
from src.models.user import User

ATS_REPORT_KEYS = (
    "score",
    "matched_skills",
    "matched_experience",
    "missing_skills",
    "experience_gaps",
    "suggestions",
    "resume_id",
    "_hash",
    "_version",
)

EXTRA_BOARD_NAMES = [
    "My Applications",
    "Remote Search",
    "Dream Companies",
    "Backup Options",
    "Referral Leads",
]


async def get_user(db: AsyncSession, identifier: str) -> User | None:
    result = await db.execute(select(User).where((User.email == identifier) | (User.user_name == identifier)))
    return result.scalar_one_or_none()


async def get_or_create_boards(db: AsyncSession, user: User, min_boards: int) -> list[Board]:
    result = await db.execute(select(Board).where(Board.user_id == user.id))
    boards = list(result.scalars().all())

    needed = min_boards - len(boards)
    if needed > 0:
        used_names = {b.name for b in boards}
        available_names = [n for n in EXTRA_BOARD_NAMES if n not in used_names]

        for i in range(needed):
            name = available_names[i] if i < len(available_names) else f"Board {len(boards) + 1}"
            board = Board(
                name=name,
                stages=DEFAULT_STAGES,
                user_id=user.id,
                is_default=not boards and i == 0,
            )
            db.add(board)
            boards.append(board)

        await db.commit()

        for board in boards:
            await db.refresh(board)

        print(f"User had {len(boards) - needed} board(s) — created {needed} more to reach {len(boards)}")

    return boards


def resolve_status(board: Board, stage_key: str) -> str:
    keys = [s["key"] for s in board.stages] if board.stages else [s["key"] for s in DEFAULT_STAGES]
    return stage_key if stage_key in keys else keys[0]


class CompanyCache:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._cache: dict[str, Company] = {}

    async def get_or_create(self, data: dict[str, Any] | None) -> Company | None:
        # The requested ATS/job shape allows company: null.
        if data is None:
            return None

        name = data["name"]
        if name in self._cache:
            return self._cache[name]

        result = await self.db.execute(select(Company).where(Company.name == name))
        company = result.scalar_one_or_none()

        if not company:
            company = Company(
                name=name,
                website=data.get("website"),
                email=data.get("email"),
                size=data.get("size"),
                industry=data.get("industry"),
                description=data.get("description"),
                logo_url=data.get("logo_url"),
            )
            self.db.add(company)
            await self.db.flush()

        self._cache[name] = company
        return company


class SkillCache:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._cache: dict[str, Skill] = {}

    async def get_or_create_many(self, entries: list[dict[str, Any]]) -> list[Skill]:
        skills = []

        for entry in entries:
            name = entry["name"]

            if name not in self._cache:
                result = await self.db.execute(select(Skill).where(Skill.name == name))
                skill = result.scalar_one_or_none()

                if not skill:
                    skill = Skill(
                        name=name,
                        label=entry["label"],
                    )
                    self.db.add(skill)
                    await self.db.flush()

                self._cache[name] = skill

            skills.append(self._cache[name])

        return skills


def parse_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.now(UTC)

    # Supports both:
    #   2026-07-31
    #   2026-07-31T08:01:59.833533Z
    if len(value) == 10:
        parsed = datetime.strptime(value, "%Y-%m-%d")
        return parsed.replace(tzinfo=UTC)

    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def normalize_ats_report(
    report: dict[str, Any] | None,
    ats_score: float | None,
    ats_resume_id: int | None,
) -> dict[str, Any] | None:
    if report is None:
        return None

    normalized = {
        "score": report.get("score", ats_score),
        "matched_skills": report.get("matched_skills", []),
        "matched_experience": report.get("matched_experience", []),
        "missing_skills": report.get(
            "missing_skills",
            report.get("missing_keywords", []),
        ),
        "experience_gaps": report.get("experience_gaps", []),
        "suggestions": report.get("suggestions", []),
        "resume_id": ats_resume_id,
        "_hash": report.get("_hash"),
        "_version": report.get("_version", 6),
    }

    # Generate a stable hash if the JSON did not provide one.
    if not normalized["_hash"]:
        hash_payload = {key: normalized[key] for key in ATS_REPORT_KEYS if key not in {"_hash", "_version"}}
        canonical = json.dumps(
            hash_payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        normalized["_hash"] = hashlib.md5(canonical.encode("utf-8")).hexdigest()[:24]

    # Build the dict from the allow-list so no legacy/extra fields survive.
    return {key: normalized[key] for key in ATS_REPORT_KEYS}


async def seed(
    user_identifier: str,
    file_path: str,
    resume_assign_ratio: float,
    min_boards: int,
) -> None:
    with open(file_path, encoding="utf-8") as f:
        jobs_data = json.load(f)

    async with AsyncSessionLocal() as db:
        user = await get_user(db, user_identifier)

        if not user:
            print(
                f"No user found matching '{user_identifier}' (checked email and user_name)",
                file=sys.stderr,
            )
            sys.exit(1)

        boards = await get_or_create_boards(db, user, min_boards)

        print(f"Distributing jobs across {len(boards)} board(s): {', '.join(b.name for b in boards)}")

        companies = CompanyCache(db)
        skills = SkillCache(db)

        resumes_result = await db.execute(select(Resume.id).where(Resume.user_id == user.id))
        resume_ids = [row[0] for row in resumes_result.all()]

        created = 0

        for job_data in jobs_data:
            board = random.choice(boards)
            status = resolve_status(board, job_data["stage_key"])

            company = await companies.get_or_create(job_data.get("company"))
            required_skills = await skills.get_or_create_many(job_data.get("required_skills", []))

            ats_score = job_data.get("ats_score")
            ats_resume_id = job_data.get("ats_resume_id")

            if ats_score is not None and ats_resume_id is None and resume_ids and random.random() < resume_assign_ratio:
                ats_resume_id = random.choice(resume_ids)

            ats_report = normalize_ats_report(
                job_data.get("ats_report"),
                ats_score,
                ats_resume_id,
            )

            job = Job(
                title=job_data["title"],
                status=status,
                position=job_data["position"],
                category=job_data.get("category"),
                salary_range=job_data.get("salary_range"),
                description=job_data.get("description"),
                years_of_experience=job_data.get("years_of_experience"),
                source_url=job_data.get("source_url"),
                source_platform=job_data.get("source_platform"),
                applied_date=parse_date(job_data.get("applied_date")),
                notes=job_data.get("notes"),
                ats_score=ats_score,
                ats_resume_id=ats_resume_id,
                ats_report=ats_report,
                user_id=user.id,
                company_id=company.id if company else None,
                required_skills=required_skills,
                work_model=job_data["work_model"],
                location=job_data.get("location"),
                board_id=board.id,
                created_at=parse_datetime(job_data.get("created_at")),
                updated_at=parse_datetime(job_data.get("updated_at") or job_data.get("created_at")),
            )

            db.add(job)
            created += 1

        await db.commit()

        print(f"Inserted {created} dummy jobs for user {user.id} ({user.email or user.user_name})")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--user",
        required=True,
        help="Target user's email or username",
    )
    parser.add_argument(
        "--file",
        default="scripts/dummy_jobs_ats_v2.json",
    )
    parser.add_argument(
        "--resume-assign-ratio",
        type=float,
        default=0.3,
    )
    parser.add_argument(
        "--min-boards",
        type=int,
        default=4,
        help="Ensure at least this many boards exist",
    )

    args = parser.parse_args()

    asyncio.run(
        seed(
            args.user,
            args.file,
            args.resume_assign_ratio,
            args.min_boards,
        )
    )


if __name__ == "__main__":
    main()
