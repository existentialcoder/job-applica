"""fix jobs.board_id FK to ON DELETE SET NULL

Revision ID: h1i5j9k3l7m2
Revises: g4h8j2k5m9n1
Create Date: 2026-05-25

"""
from alembic import op
import sqlalchemy as sa

revision = 'h1i5j9k3l7m2'
down_revision = 'g4h8j2k5m9n1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # IF EXISTS avoids aborting the transaction when a constraint doesn't exist
    op.execute('ALTER TABLE jobs DROP CONSTRAINT IF EXISTS jobs_board_id_fkey')
    op.execute('ALTER TABLE jobs DROP CONSTRAINT IF EXISTS fk_jobs_board_id')
    op.create_foreign_key(
        'fk_jobs_board_id', 'jobs', 'boards', ['board_id'], ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.execute('ALTER TABLE jobs DROP CONSTRAINT IF EXISTS fk_jobs_board_id')
    op.create_foreign_key(
        'fk_jobs_board_id', 'jobs', 'boards', ['board_id'], ['id'],
    )
