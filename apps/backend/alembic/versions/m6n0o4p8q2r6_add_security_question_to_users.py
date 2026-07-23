"""add_security_question_to_users

Revision ID: m6n0o4p8q2r6
Revises: l5m9n3o7p1q5
Create Date: 2026-07-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'm6n0o4p8q2r6'
down_revision: Union[str, Sequence[str], None] = 'l5m9n3o7p1q5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('security_question', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('hashed_security_answer', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'hashed_security_answer')
    op.drop_column('users', 'security_question')
