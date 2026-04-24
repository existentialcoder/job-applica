"""widen source_url to text

Revision ID: f2a9c3e7b016
Revises: d3e7a1b4c852
Create Date: 2026-04-23

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'f2a9c3e7b016'
down_revision: Union[str, Sequence[str], None] = 'd3e7a1b4c852'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('jobs', 'source_url', type_=sa.Text(), existing_nullable=True)


def downgrade() -> None:
    op.alter_column('jobs', 'source_url', type_=sa.String(500), existing_nullable=True)
