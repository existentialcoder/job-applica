"""move server data out of users

account_recovery.otp_attempts becomes reset_attempts (it counts security-answer tries too) and
reset_locked_until is added, so repeated wrong password-reset answers lock the account for a while.

Moves the server-owned data that 5d6a388158d8 deferred out of users:
users.security_question / hashed_security_answer -> account_recovery (columns dropped),
users.settings['ext_extractions'] -> usage_counters, and the 'otp' / 'ext_extractions' keys are
stripped from users.settings. In-flight OTPs are not carried over; users just request a new code.

Each job's current score (jobs.ats_score / ats_report) becomes its first job_ats_scores row, skipping
jobs that already have history, then jobs.ats_report and jobs.ats_resume_id are dropped; jobs.ats_score
stays as a copy of the latest score for sorting/filtering. input_hash takes the app's '<version>:<hash>'
cache-key format, so reports cached at the current version (6) stay cache hits. Downgrade rebuilds the
two columns from each job's latest row but leaves job_ats_scores alone: the app writes to it from here
on, so backfilled and real rows can't be told apart.

Revision ID: 609f6013449d
Revises: 5d6a388158d8
Create Date: 2026-10-03

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = '609f6013449d'
down_revision: str | Sequence[str] | None = '5d6a388158d8'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column('account_recovery', 'otp_attempts', new_column_name='reset_attempts')
    op.add_column('account_recovery', sa.Column('reset_locked_until', sa.DateTime(timezone=True), nullable=True))

    op.execute(
        """
        INSERT INTO account_recovery (user_id, security_question, hashed_security_answer)
        SELECT id, security_question, hashed_security_answer FROM users
        WHERE security_question IS NOT NULL OR hashed_security_answer IS NOT NULL
        ON CONFLICT (user_id) DO UPDATE
        SET security_question = EXCLUDED.security_question,
            hashed_security_answer = EXCLUDED.hashed_security_answer
        """
    )
    op.drop_column('users', 'security_question')
    op.drop_column('users', 'hashed_security_answer')

    op.execute(
        """
        INSERT INTO usage_counters (user_id, resource, period, count)
        SELECT id, 'monthly_extractions', settings->'ext_extractions'->>'month',
               CAST(settings->'ext_extractions'->>'count' AS INTEGER)
        FROM users
        WHERE settings->'ext_extractions'->>'month' IS NOT NULL
          AND settings->'ext_extractions'->>'count' IS NOT NULL
        ON CONFLICT ON CONSTRAINT uq_usage_counters_user_resource_period DO UPDATE SET count = EXCLUDED.count
        """
    )
    op.execute("UPDATE users SET settings = settings - 'otp' - 'ext_extractions'")

    op.execute(
        """
        INSERT INTO job_ats_scores (job_id, resume_id, score, report, input_hash, created_at, updated_at)
        SELECT j.id, j.ats_resume_id, j.ats_score,
               COALESCE(CAST(j.ats_report AS JSONB), '{}'::jsonb) - '_hash' - '_version',
               CASE WHEN CAST(j.ats_report AS JSONB)->>'_version' = '6'
                         AND CAST(j.ats_report AS JSONB)->>'_hash' IS NOT NULL
                    THEN '6:' || (CAST(j.ats_report AS JSONB)->>'_hash')
                    ELSE '' END,
               j.updated_at, j.updated_at
        FROM jobs j
        WHERE j.ats_score IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM job_ats_scores s WHERE s.job_id = j.id)
        """
    )
    op.drop_column('jobs', 'ats_report')
    op.drop_column('jobs', 'ats_resume_id')


def downgrade() -> None:
    op.add_column(
        'jobs',
        sa.Column('ats_resume_id', sa.Integer(), sa.ForeignKey('resumes.id', ondelete='SET NULL'), nullable=True),
    )
    op.add_column('jobs', sa.Column('ats_report', sa.JSON(), nullable=True))
    op.execute(
        """
        UPDATE jobs j
        SET ats_resume_id = s.resume_id,
            ats_report = CAST(
                s.report || CASE WHEN s.input_hash LIKE '%:%'
                    THEN jsonb_build_object(
                        '_hash', split_part(s.input_hash, ':', 2),
                        '_version', CAST(split_part(s.input_hash, ':', 1) AS INTEGER)
                    )
                    ELSE '{}'::jsonb END
                AS JSON)
        FROM (
            SELECT DISTINCT ON (job_id) job_id, resume_id, report, input_hash FROM job_ats_scores
            ORDER BY job_id, created_at DESC
        ) s
        WHERE s.job_id = j.id
        """
    )

    op.execute(
        """
        UPDATE users u
        SET settings = u.settings || jsonb_build_object(
            'ext_extractions', jsonb_build_object('month', c.period, 'count', c.count)
        )
        FROM (
            SELECT DISTINCT ON (user_id) user_id, period, count FROM usage_counters
            WHERE resource = 'monthly_extractions'
            ORDER BY user_id, period DESC
        ) c
        WHERE c.user_id = u.id
        """
    )
    op.execute("DELETE FROM usage_counters WHERE resource = 'monthly_extractions'")

    op.add_column('users', sa.Column('security_question', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('hashed_security_answer', sa.Text(), nullable=True))
    op.execute(
        """
        UPDATE users u
        SET security_question = r.security_question, hashed_security_answer = r.hashed_security_answer
        FROM account_recovery r
        WHERE r.user_id = u.id
        """
    )
    op.execute('UPDATE account_recovery SET security_question = NULL, hashed_security_answer = NULL')

    op.drop_column('account_recovery', 'reset_locked_until')
    op.alter_column('account_recovery', 'reset_attempts', new_column_name='otp_attempts')
