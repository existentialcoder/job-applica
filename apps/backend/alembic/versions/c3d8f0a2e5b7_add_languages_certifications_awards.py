"""add languages, certifications and awards

Three more extracted lists on user_profiles and resume_snapshots, so match scoring can check language
and certification requirements. Existing rows get empty lists.

Revision ID: c3d8f0a2e5b7
Revises: a7c2e9f41b6d
Create Date: 2026-10-13

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = 'c3d8f0a2e5b7'
down_revision: str | Sequence[str] | None = 'a7c2e9f41b6d'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLES = ('user_profiles', 'resume_snapshots')
COLUMNS = ('languages', 'certifications', 'awards')


def upgrade() -> None:
    for table in TABLES:
        for column in COLUMNS:
            op.add_column(table, sa.Column(column, JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=False))


def downgrade() -> None:
    for table in TABLES:
        for column in COLUMNS:
            op.drop_column(table, column)
