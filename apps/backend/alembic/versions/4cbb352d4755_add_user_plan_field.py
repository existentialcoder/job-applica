"""add_user_plan_field

Revision ID: 4cbb352d4755
Revises: 552455dbe627
Create Date: 2026-06-26 18:15:06.496850

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '4cbb352d4755'
down_revision: Union[str, Sequence[str], None] = '552455dbe627'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('plan', sa.String(length=50), nullable=False, server_default='free'))


def downgrade() -> None:
    op.drop_column('users', 'plan')
