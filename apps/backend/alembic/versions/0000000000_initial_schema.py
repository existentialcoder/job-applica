"""Initial schema

Revision ID: 0000000000
Revises: None
Create Date: 2025-11-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = '0000000000'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _existing_types(conn) -> set:
    return {r[0] for r in conn.execute(
        sa.text("SELECT typname FROM pg_type WHERE typtype = 'e'")
    ).fetchall()}


def upgrade() -> None:
    conn = op.get_bind()
    insp = inspect(conn)
    tables = set(insp.get_table_names())
    indexes = {(i['name'], t) for t in tables for i in insp.get_indexes(t)}

    if 'users' not in tables:
        op.create_table(
            'users',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('first_name', sa.String(100), nullable=False),
            sa.Column('last_name', sa.String(100), nullable=False),
            sa.Column('user_name', sa.String(100), nullable=False),
            sa.Column('email', sa.String(255), nullable=True),
            sa.Column('signup_key', sa.String(255), nullable=False),
            sa.Column('hashed_password', sa.String(255), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_name'),
        )
        op.create_index('ix_users_email', 'users', ['email'], unique=True)

    if 'companies' not in tables:
        op.create_table(
            'companies',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('website', sa.String(255), nullable=True),
            sa.Column('email', sa.String(255), nullable=True),
            sa.Column('size', sa.Integer(), nullable=True),
            sa.Column('industry', sa.String(255), nullable=True),
            sa.Column('description', sa.String(500), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name'),
        )

    if 'skills' not in tables:
        op.create_table(
            'skills',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('name', sa.String(255), nullable=False),
            sa.Column('label', sa.String(255), nullable=False),
            sa.Column('description', sa.String(500), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name'),
        )

    if 'user_skill' not in tables:
        op.create_table(
            'user_skill',
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('skill_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('user_id', 'skill_id'),
        )

    if 'locations' not in tables:
        op.create_table(
            'locations',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
            sa.Column('city', sa.String(), nullable=True),
            sa.Column('state', sa.String(), nullable=True),
            sa.Column('country', sa.String(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_locations_city', 'locations', ['city'])
        op.create_index('ix_locations_state', 'locations', ['state'])
        op.create_index('ix_locations_country', 'locations', ['country'])

    existing_types = _existing_types(conn)
    if 'jobstatus' not in existing_types:
        op.execute("CREATE TYPE jobstatus AS ENUM ('Open', 'Closed', 'Pending')")
    if 'jobposition' not in existing_types:
        op.execute("CREATE TYPE jobposition AS ENUM ('Intern', 'Junior', 'Mid', 'Senior', 'Lead', 'Manager')")
    if 'jobworkmodel' not in existing_types:
        op.execute("CREATE TYPE jobworkmodel AS ENUM ('On-site', 'Remote', 'Hybrid')")

    if 'jobs' not in tables:
        op.create_table(
            'jobs',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('title', sa.String(255), nullable=False),
            sa.Column('status', sa.Enum('Open', 'Closed', 'Pending', name='jobstatus', create_type=False), nullable=False),
            sa.Column('position', sa.Enum('Intern', 'Junior', 'Mid', 'Senior', 'Lead', 'Manager', name='jobposition', create_type=False), nullable=True),
            sa.Column('category', sa.String(100), nullable=True),
            sa.Column('salary_range', sa.String(100), nullable=True),
            sa.Column('description', sa.String(500), nullable=True),
            sa.Column('years_of_experience', sa.JSON(), nullable=True),
            sa.Column('source_url', sa.String(500), nullable=True),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('company_id', sa.Integer(), nullable=True),
            sa.Column('work_model', sa.Enum('On-site', 'Remote', 'Hybrid', name='jobworkmodel', create_type=False), nullable=False),
            sa.Column('location_id', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
            sa.ForeignKeyConstraint(['location_id'], ['locations.id']),
            sa.PrimaryKeyConstraint('id'),
        )

    if 'job_skill' not in tables:
        op.create_table(
            'job_skill',
            sa.Column('job_id', sa.Integer(), nullable=False),
            sa.Column('skill_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('job_id', 'skill_id'),
        )

    if 'resumes' not in tables:
        op.create_table(
            'resumes',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('original_name', sa.String(255), nullable=False),
            sa.Column('stored_name', sa.String(255), nullable=False),
            sa.Column('file_path', sa.String(500), nullable=False),
            sa.Column('file_size', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_resumes_user_id', 'resumes', ['user_id'])


def downgrade() -> None:
    op.drop_table('resumes')
    op.drop_table('job_skill')
    op.drop_table('jobs')
    op.drop_table('locations')
    op.drop_table('user_skill')
    op.drop_table('skills')
    op.drop_table('companies')
    op.drop_table('users')
    op.execute('DROP TYPE IF EXISTS jobstatus')
    op.execute('DROP TYPE IF EXISTS jobposition')
    op.execute('DROP TYPE IF EXISTS jobworkmodel')
