"""Add settings JSONB to users

Revision ID: d3e7a1b4c852
Revises: c1d5f9a2b347
Create Date: 2026-04-23 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'd3e7a1b4c852'
down_revision: Union[str, Sequence[str], None] = 'c1d5f9a2b347'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column(
            'settings',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )


def downgrade() -> None:
    op.drop_column('users', 'settings')
