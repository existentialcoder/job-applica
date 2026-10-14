"""add 'filling' extraction status

The extraction job sets resumes.extraction_status = 'filling' once the AI has read the CV and it is writing
the snapshot and profile, so the "Reading your CV" screen can show which stage it's at.

Revision ID: d9e1f3a5c7b2
Revises: c3d8f0a2e5b7
Create Date: 2026-10-13

"""

from collections.abc import Sequence

from alembic import op

revision: str = 'd9e1f3a5c7b2'
down_revision: str | Sequence[str] | None = 'c3d8f0a2e5b7'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _constraint(statuses: str) -> None:
    op.drop_constraint('ck_resumes_extraction_status', 'resumes', type_='check')
    op.create_check_constraint('ck_resumes_extraction_status', 'resumes', f'extraction_status IN ({statuses})')


def upgrade() -> None:
    _constraint("'pending', 'filling', 'done', 'failed', 'limit_reached'")


def downgrade() -> None:
    op.execute("UPDATE resumes SET extraction_status = 'pending' WHERE extraction_status = 'filling'")
    _constraint("'pending', 'done', 'failed', 'limit_reached'")
