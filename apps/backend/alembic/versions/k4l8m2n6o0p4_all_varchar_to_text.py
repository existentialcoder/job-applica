"""convert all user-data varchar columns to text

Revision ID: k4l8m2n6o0p4
Revises: j3k7l1m5n9o3
Create Date: 2026-07-17

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'k4l8m2n6o0p4'
down_revision: Union[str, None] = 'j3k7l1m5n9o3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # jobs
    op.alter_column('jobs', 'title',         existing_type=sa.String(255),  type_=sa.Text(), existing_nullable=False)
    op.alter_column('jobs', 'status',        existing_type=sa.String(255),  type_=sa.Text(), existing_nullable=False)
    op.alter_column('jobs', 'category',      existing_type=sa.String(255),  type_=sa.Text(), existing_nullable=True)
    op.alter_column('jobs', 'salary_range',  existing_type=sa.String(500),  type_=sa.Text(), existing_nullable=True)

    # boards
    op.alter_column('boards', 'name',        existing_type=sa.String(100),  type_=sa.Text(), existing_nullable=False)
    op.alter_column('boards', 'description', existing_type=sa.String(500),  type_=sa.Text(), existing_nullable=True)

    # companies
    op.alter_column('companies', 'name',     existing_type=sa.String(100),  type_=sa.Text(), existing_nullable=False)
    op.alter_column('companies', 'website',  existing_type=sa.String(255),  type_=sa.Text(), existing_nullable=True)
    op.alter_column('companies', 'email',    existing_type=sa.String(255),  type_=sa.Text(), existing_nullable=True)
    op.alter_column('companies', 'industry', existing_type=sa.String(255),  type_=sa.Text(), existing_nullable=True)

    # users
    op.alter_column('users', 'first_name',       existing_type=sa.String(100),  type_=sa.Text(), existing_nullable=False)
    op.alter_column('users', 'last_name',        existing_type=sa.String(100),  type_=sa.Text(), existing_nullable=False)
    op.alter_column('users', 'user_name',        existing_type=sa.String(100),  type_=sa.Text(), existing_nullable=False)
    op.alter_column('users', 'email',            existing_type=sa.String(255),  type_=sa.Text(), existing_nullable=True)
    op.alter_column('users', 'signup_key',       existing_type=sa.String(255),  type_=sa.Text(), existing_nullable=False)
    op.alter_column('users', 'hashed_password',  existing_type=sa.String(255),  type_=sa.Text(), existing_nullable=True)
    op.alter_column('users', 'avatar_url',       existing_type=sa.String(500),  type_=sa.Text(), existing_nullable=True)

    # connected_accounts
    op.alter_column('connected_accounts', 'provider_user_id', existing_type=sa.String(255), type_=sa.Text(), existing_nullable=False)
    op.alter_column('connected_accounts', 'provider_email',   existing_type=sa.String(255), type_=sa.Text(), existing_nullable=True)
    op.alter_column('connected_accounts', 'display_name',     existing_type=sa.String(255), type_=sa.Text(), existing_nullable=True)
    op.alter_column('connected_accounts', 'avatar_url',       existing_type=sa.String(500), type_=sa.Text(), existing_nullable=True)

    # resumes
    op.alter_column('resumes', 'original_name', existing_type=sa.String(255), type_=sa.Text(), existing_nullable=False)
    op.alter_column('resumes', 'stored_name',   existing_type=sa.String(255), type_=sa.Text(), existing_nullable=False)
    op.alter_column('resumes', 'file_path',     existing_type=sa.String(500), type_=sa.Text(), existing_nullable=False)

    # skills
    op.alter_column('skills', 'name',        existing_type=sa.String(255), type_=sa.Text(), existing_nullable=False)
    op.alter_column('skills', 'label',       existing_type=sa.String(255), type_=sa.Text(), existing_nullable=False)
    op.alter_column('skills', 'logo_url',    existing_type=sa.String(500), type_=sa.Text(), existing_nullable=True)
    op.alter_column('skills', 'description', existing_type=sa.String(500), type_=sa.Text(), existing_nullable=True)


def downgrade() -> None:
    op.alter_column('skills', 'description', existing_type=sa.Text(), type_=sa.String(500), existing_nullable=True)
    op.alter_column('skills', 'logo_url',    existing_type=sa.Text(), type_=sa.String(500), existing_nullable=True)
    op.alter_column('skills', 'label',       existing_type=sa.Text(), type_=sa.String(255), existing_nullable=False)
    op.alter_column('skills', 'name',        existing_type=sa.Text(), type_=sa.String(255), existing_nullable=False)

    op.alter_column('resumes', 'file_path',     existing_type=sa.Text(), type_=sa.String(500), existing_nullable=False)
    op.alter_column('resumes', 'stored_name',   existing_type=sa.Text(), type_=sa.String(255), existing_nullable=False)
    op.alter_column('resumes', 'original_name', existing_type=sa.Text(), type_=sa.String(255), existing_nullable=False)

    op.alter_column('connected_accounts', 'avatar_url',       existing_type=sa.Text(), type_=sa.String(500), existing_nullable=True)
    op.alter_column('connected_accounts', 'display_name',     existing_type=sa.Text(), type_=sa.String(255), existing_nullable=True)
    op.alter_column('connected_accounts', 'provider_email',   existing_type=sa.Text(), type_=sa.String(255), existing_nullable=True)
    op.alter_column('connected_accounts', 'provider_user_id', existing_type=sa.Text(), type_=sa.String(255), existing_nullable=False)

    op.alter_column('users', 'avatar_url',      existing_type=sa.Text(), type_=sa.String(500), existing_nullable=True)
    op.alter_column('users', 'hashed_password', existing_type=sa.Text(), type_=sa.String(255), existing_nullable=True)
    op.alter_column('users', 'signup_key',      existing_type=sa.Text(), type_=sa.String(255), existing_nullable=False)
    op.alter_column('users', 'email',           existing_type=sa.Text(), type_=sa.String(255), existing_nullable=True)
    op.alter_column('users', 'user_name',       existing_type=sa.Text(), type_=sa.String(100), existing_nullable=False)
    op.alter_column('users', 'last_name',       existing_type=sa.Text(), type_=sa.String(100), existing_nullable=False)
    op.alter_column('users', 'first_name',      existing_type=sa.Text(), type_=sa.String(100), existing_nullable=False)

    op.alter_column('companies', 'industry', existing_type=sa.Text(), type_=sa.String(255), existing_nullable=True)
    op.alter_column('companies', 'email',    existing_type=sa.Text(), type_=sa.String(255), existing_nullable=True)
    op.alter_column('companies', 'website',  existing_type=sa.Text(), type_=sa.String(255), existing_nullable=True)
    op.alter_column('companies', 'name',     existing_type=sa.Text(), type_=sa.String(100), existing_nullable=False)

    op.alter_column('boards', 'description', existing_type=sa.Text(), type_=sa.String(500), existing_nullable=True)
    op.alter_column('boards', 'name',        existing_type=sa.Text(), type_=sa.String(100), existing_nullable=False)

    op.alter_column('jobs', 'salary_range', existing_type=sa.Text(), type_=sa.String(500), existing_nullable=True)
    op.alter_column('jobs', 'category',     existing_type=sa.Text(), type_=sa.String(255), existing_nullable=True)
    op.alter_column('jobs', 'status',       existing_type=sa.Text(), type_=sa.String(255), existing_nullable=False)
    op.alter_column('jobs', 'title',        existing_type=sa.Text(), type_=sa.String(255), existing_nullable=False)
