"""Add OAuth fields to users

Revision ID: c1d5f9a2b347
Revises: b2c4e8f1a390
Create Date: 2026-04-23 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c1d5f9a2b347'
down_revision: Union[str, Sequence[str], None] = 'b2c4e8f1a390'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('users', 'hashed_password', existing_type=sa.String(255), nullable=True)
    op.add_column('users', sa.Column('google_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('linkedin_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('avatar_url', sa.String(500), nullable=True))
    op.create_unique_constraint('uq_users_google_id', 'users', ['google_id'])
    op.create_unique_constraint('uq_users_linkedin_id', 'users', ['linkedin_id'])
    op.create_index('ix_users_google_id', 'users', ['google_id'], unique=True)
    op.create_index('ix_users_linkedin_id', 'users', ['linkedin_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_users_linkedin_id', table_name='users')
    op.drop_index('ix_users_google_id', table_name='users')
    op.drop_constraint('uq_users_linkedin_id', 'users', type_='unique')
    op.drop_constraint('uq_users_google_id', 'users', type_='unique')
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'linkedin_id')
    op.drop_column('users', 'google_id')
    op.alter_column('users', 'hashed_password', existing_type=sa.String(255), nullable=False)
