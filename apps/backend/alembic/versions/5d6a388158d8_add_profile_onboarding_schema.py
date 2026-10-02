"""add profile onboarding schema

New tables: user_profiles, profile_contacts, job_preferences, resume_snapshots, job_ats_scores,
user_onboarding, account_recovery, usage_counters. New columns: resumes.version + replaces_resume_id,
jobs.applied_resume_id, user_skill.source + resume_id.

Additive only. The default CV stays resumes.is_default (no is_master column). Existing rows get
version 1 and source 'manual' through server defaults; the data backfill (snapshots, draft profiles,
first score-history rows, moving data out of users.settings) ships in a later migration.

Revision ID: 5d6a388158d8
Revises: 27fb1b042a4e
Create Date: 2026-09-26

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

revision: str = '5d6a388158d8'
down_revision: str | Sequence[str] | None = '27fb1b042a4e'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

EMPTY_JSONB_LIST = sa.text("'[]'::jsonb")
EMPTY_JSONB_DICT = sa.text("'{}'::jsonb")
EMPTY_ARRAY = sa.text("'{}'")


def _base_columns() -> list[sa.Column]:
    return [
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    ]


def _user_fk(unique: bool) -> list:
    items: list = [
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    ]
    if unique:
        items.append(sa.UniqueConstraint('user_id'))
    return items


def _extracted_profile_columns() -> list[sa.Column]:
    return [
        sa.Column('headline', sa.Text(), nullable=True),
        sa.Column('current_title', sa.Text(), nullable=True),
        sa.Column('current_company', sa.Text(), nullable=True),
        sa.Column('years_experience', sa.Integer(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('experience', JSONB(), server_default=EMPTY_JSONB_LIST, nullable=False),
        sa.Column('education', JSONB(), server_default=EMPTY_JSONB_LIST, nullable=False),
    ]


def upgrade() -> None:
    # ── Existing tables ──────────────────────────────────────────────────────
    op.add_column('resumes', sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False))
    op.add_column('resumes', sa.Column('replaces_resume_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'resumes_replaces_resume_id_fkey', 'resumes', 'resumes', ['replaces_resume_id'], ['id'], ondelete='SET NULL'
    )

    op.add_column('jobs', sa.Column('applied_resume_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'jobs_applied_resume_id_fkey', 'jobs', 'resumes', ['applied_resume_id'], ['id'], ondelete='SET NULL'
    )

    op.add_column('user_skill', sa.Column('source', sa.String(10), server_default=sa.text("'manual'"), nullable=False))
    op.add_column('user_skill', sa.Column('resume_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'user_skill_resume_id_fkey', 'user_skill', 'resumes', ['resume_id'], ['id'], ondelete='SET NULL'
    )
    op.create_check_constraint('ck_user_skill_source', 'user_skill', "source IN ('cv', 'manual')")

    # ── Profile ──────────────────────────────────────────────────────────────
    op.create_table(
        'user_profiles',
        *_base_columns(),
        *_user_fk(unique=True),
        sa.Column('source_resume_id', sa.Integer(), nullable=True),
        *_extracted_profile_columns(),
        sa.Column('field_sources', JSONB(), server_default=EMPTY_JSONB_DICT, nullable=False),
        sa.Column('extracted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['source_resume_id'], ['resumes.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'profile_contacts',
        *_base_columns(),
        *_user_fk(unique=True),
        sa.Column('email', sa.Text(), nullable=True),
        sa.Column('secondary_email', sa.Text(), nullable=True),
        sa.Column('phone', sa.Text(), nullable=True),
        sa.Column('linkedin_url', sa.Text(), nullable=True),
        sa.Column('github_url', sa.Text(), nullable=True),
        sa.Column('portfolio_url', sa.Text(), nullable=True),
        sa.Column('city', sa.Text(), nullable=True),
        sa.Column('country', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'job_preferences',
        *_base_columns(),
        *_user_fk(unique=True),
        sa.Column('target_titles', ARRAY(sa.Text()), server_default=EMPTY_ARRAY, nullable=False),
        sa.Column('locations', JSONB(), server_default=EMPTY_JSONB_LIST, nullable=False),
        sa.Column('work_models', ARRAY(sa.Text()), server_default=EMPTY_ARRAY, nullable=False),
        sa.Column('seniority', ARRAY(sa.Text()), server_default=EMPTY_ARRAY, nullable=False),
        sa.Column('job_types', ARRAY(sa.Text()), server_default=EMPTY_ARRAY, nullable=False),
        sa.Column('salary_min', sa.BigInteger(), nullable=True),
        sa.Column('salary_max', sa.BigInteger(), nullable=True),
        sa.Column('salary_currency', sa.String(3), nullable=True),
        sa.Column('salary_period', sa.String(10), nullable=True),
        sa.Column('notice_period_days', sa.Integer(), nullable=True),
        sa.Column('open_to_relocation', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('needs_visa_sponsorship', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('industries_include', ARRAY(sa.Text()), server_default=EMPTY_ARRAY, nullable=False),
        sa.Column('industries_exclude', ARRAY(sa.Text()), server_default=EMPTY_ARRAY, nullable=False),
        sa.Column('weekly_job_suggestions', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.CheckConstraint("salary_period IN ('year', 'month', 'hour')", name='ck_job_preferences_salary_period'),
        sa.CheckConstraint('salary_max >= salary_min', name='ck_job_preferences_salary_range'),
        sa.PrimaryKeyConstraint('id'),
    )

    # ── CV snapshots and score history ───────────────────────────────────────
    op.create_table(
        'resume_snapshots',
        *_base_columns(),
        *_user_fk(unique=False),
        sa.Column('resume_id', sa.Integer(), nullable=False),
        *_extracted_profile_columns(),
        sa.Column('skills', ARRAY(sa.Text()), server_default=EMPTY_ARRAY, nullable=False),
        sa.Column('content_hash', sa.String(64), nullable=False),
        sa.Column('extracted_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('resume_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_resume_snapshots_user_id', 'resume_snapshots', ['user_id'])
    op.create_index('ix_resume_snapshots_content_hash', 'resume_snapshots', ['content_hash'])

    op.create_table(
        'job_ats_scores',
        *_base_columns(),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('resume_id', sa.Integer(), nullable=True),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('report', JSONB(), nullable=False),
        sa.Column('input_hash', sa.String(64), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_job_ats_scores_job_id_created_at', 'job_ats_scores', ['job_id', 'created_at'])

    # ── Server-owned user data (moved out of users / users.settings later) ───
    op.create_table(
        'user_onboarding',
        *_base_columns(),
        *_user_fk(unique=True),
        sa.Column('step', sa.String(32), server_default=sa.text("'welcome'"), nullable=False),
        sa.Column('skipped_steps', ARRAY(sa.Text()), server_default=EMPTY_ARRAY, nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('dismissed_cards', ARRAY(sa.Text()), server_default=EMPTY_ARRAY, nullable=False),
        sa.Column('first_import_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'account_recovery',
        *_base_columns(),
        *_user_fk(unique=True),
        sa.Column('security_question', sa.Text(), nullable=True),
        sa.Column('hashed_security_answer', sa.Text(), nullable=True),
        sa.Column('otp_hash', sa.Text(), nullable=True),
        sa.Column('otp_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('otp_attempts', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'usage_counters',
        *_base_columns(),
        *_user_fk(unique=False),
        sa.Column('resource', sa.String(50), nullable=False),
        sa.Column('period', sa.String(7), nullable=False),
        sa.Column('count', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.UniqueConstraint('user_id', 'resource', 'period', name='uq_usage_counters_user_resource_period'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('usage_counters')
    op.drop_table('account_recovery')
    op.drop_table('user_onboarding')
    op.drop_index('ix_job_ats_scores_job_id_created_at', table_name='job_ats_scores')
    op.drop_table('job_ats_scores')
    op.drop_index('ix_resume_snapshots_content_hash', table_name='resume_snapshots')
    op.drop_index('ix_resume_snapshots_user_id', table_name='resume_snapshots')
    op.drop_table('resume_snapshots')
    op.drop_table('job_preferences')
    op.drop_table('profile_contacts')
    op.drop_table('user_profiles')

    op.drop_constraint('ck_user_skill_source', 'user_skill', type_='check')
    op.drop_constraint('user_skill_resume_id_fkey', 'user_skill', type_='foreignkey')
    op.drop_column('user_skill', 'resume_id')
    op.drop_column('user_skill', 'source')

    op.drop_constraint('jobs_applied_resume_id_fkey', 'jobs', type_='foreignkey')
    op.drop_column('jobs', 'applied_resume_id')

    op.drop_constraint('resumes_replaces_resume_id_fkey', 'resumes', type_='foreignkey')
    op.drop_column('resumes', 'replaces_resume_id')
    op.drop_column('resumes', 'version')
