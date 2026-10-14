"""add resume extraction status

resumes.extraction_status tracks the background job that turns an uploaded CV into a snapshot:
'pending' | 'done' | 'failed' | 'limit_reached'. NULL for CVs uploaded before the job existed.

Revision ID: a7c2e9f41b6d
Revises: 609f6013449d
Create Date: 2026-10-13

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = 'a7c2e9f41b6d'
down_revision: str | Sequence[str] | None = '609f6013449d'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('resumes', sa.Column('extraction_status', sa.String(16), nullable=True))
    op.create_check_constraint(
        'ck_resumes_extraction_status',
        'resumes',
        "extraction_status IN ('pending', 'done', 'failed', 'limit_reached')",
    )


def downgrade() -> None:
    op.drop_constraint('ck_resumes_extraction_status', 'resumes', type_='check')
    op.drop_column('resumes', 'extraction_status')
