"""Add application tracking fields to jobs

Revision ID: b2c4e8f1a390
Revises: ea3fb2d04124
Create Date: 2026-04-23 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b2c4e8f1a390'
down_revision: Union[str, Sequence[str], None] = 'ea3fb2d04124'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

APPLICATION_STATUSES = ['Saved', 'Applied', 'Phone Screen', 'Interview', 'Technical', 'Offer', 'Rejected', 'Withdrawn']
SOURCE_PLATFORMS = ['LinkedIn', 'Indeed', 'Glassdoor', 'Monster', 'ZipRecruiter', 'Jobscan', 'Other']


def upgrade() -> None:
    # 1. Add new columns first as VARCHAR so we can migrate data freely
    op.add_column('jobs', sa.Column('status_temp', sa.String(50), nullable=True))
    op.add_column('jobs', sa.Column('source_url', sa.String(500), nullable=True))
    op.add_column('jobs', sa.Column('applied_date', sa.Date(), nullable=True))
    op.add_column('jobs', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('jobs', sa.Column('source_platform_temp', sa.String(50), nullable=True))

    # 2. Migrate status values: Open/Pending → Saved, Closed → Applied
    op.execute("UPDATE jobs SET status_temp = 'Applied' WHERE status::text = 'Closed'")
    op.execute("UPDATE jobs SET status_temp = 'Saved' WHERE status::text IN ('Open', 'Pending')")
    op.execute("UPDATE jobs SET status_temp = 'Saved' WHERE status_temp IS NULL")

    # 3. Create the new PostgreSQL enum types
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE applicationstatus AS ENUM ('Saved', 'Applied', 'Phone Screen', 'Interview', 'Technical', 'Offer', 'Rejected', 'Withdrawn');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE sourceplatform AS ENUM ('LinkedIn', 'Indeed', 'Glassdoor', 'Monster', 'ZipRecruiter', 'Jobscan', 'Other');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$
    """)

    # 4. Drop old status column
    op.drop_column('jobs', 'status')

    # 5. Add new typed status column from temp
    op.add_column('jobs', sa.Column('status', sa.Enum(*APPLICATION_STATUSES, name='applicationstatus'), nullable=True))
    op.execute("UPDATE jobs SET status = status_temp::applicationstatus")
    op.alter_column('jobs', 'status', nullable=False)
    op.drop_column('jobs', 'status_temp')

    # 6. Add typed source_platform column from temp
    op.add_column('jobs', sa.Column('source_platform', sa.Enum(*SOURCE_PLATFORMS, name='sourceplatform'), nullable=True))
    op.drop_column('jobs', 'source_platform_temp')

    # 7. Drop old jobstatus enum if it exists
    op.execute("DROP TYPE IF EXISTS jobstatus")

    # 8. Expand description from VARCHAR(500) to Text
    op.alter_column('jobs', 'description',
                    existing_type=sa.String(500),
                    type_=sa.Text(),
                    existing_nullable=True)


def downgrade() -> None:
    op.add_column('jobs', sa.Column('status_temp', sa.String(50), nullable=True))
    op.execute("UPDATE jobs SET status_temp = 'Open'")

    op.execute("""
        DO $$ BEGIN
            CREATE TYPE jobstatus AS ENUM ('Open', 'Closed', 'Pending');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$
    """)

    op.drop_column('jobs', 'status')
    op.add_column('jobs', sa.Column('status', sa.Enum('Open', 'Closed', 'Pending', name='jobstatus'), nullable=True))
    op.execute("UPDATE jobs SET status = status_temp::jobstatus")
    op.alter_column('jobs', 'status', nullable=False)
    op.drop_column('jobs', 'status_temp')

    op.drop_column('jobs', 'notes')
    op.drop_column('jobs', 'applied_date')
    op.drop_column('jobs', 'source_url')
    op.drop_column('jobs', 'source_platform')

    op.execute("DROP TYPE IF EXISTS applicationstatus")
    op.execute("DROP TYPE IF EXISTS sourceplatform")
