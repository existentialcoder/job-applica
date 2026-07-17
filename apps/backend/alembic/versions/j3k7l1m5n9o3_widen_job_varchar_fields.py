"""widen job salary_range and category to avoid LLM truncation

Revision ID: j3k7l1m5n9o3
Revises: i2j6k0l4m8n2
Create Date: 2026-07-17

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'j3k7l1m5n9o3'
down_revision: Union[str, None] = 'i2j6k0l4m8n2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('jobs', 'salary_range',
                    existing_type=sa.String(100),
                    type_=sa.String(500),
                    existing_nullable=True)
    op.alter_column('jobs', 'category',
                    existing_type=sa.String(100),
                    type_=sa.String(255),
                    existing_nullable=True)
    op.alter_column('jobs', 'status',
                    existing_type=sa.String(100),
                    type_=sa.String(255),
                    existing_nullable=False)


def downgrade() -> None:
    op.alter_column('jobs', 'status',
                    existing_type=sa.String(255),
                    type_=sa.String(100),
                    existing_nullable=False)
    op.alter_column('jobs', 'category',
                    existing_type=sa.String(255),
                    type_=sa.String(100),
                    existing_nullable=True)
    op.alter_column('jobs', 'salary_range',
                    existing_type=sa.String(500),
                    type_=sa.String(100),
                    existing_nullable=True)
