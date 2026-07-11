"""add_ats_report_to_jobs

Revision ID: c2d4e6f8a123
Revises: a9f3e2c1b874
Create Date: 2026-07-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c2d4e6f8a123'
down_revision: Union[str, Sequence[str], None] = 'a9f3e2c1b874'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('jobs', sa.Column('ats_report', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('jobs', 'ats_report')
