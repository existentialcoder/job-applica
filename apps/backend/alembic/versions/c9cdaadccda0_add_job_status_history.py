"""add job_status_history

Revision ID: c9cdaadccda0
Revises: n7o1p5q9r3s7
Create Date: 2026-09-01 17:52:20.864760

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c9cdaadccda0'
down_revision: str | Sequence[str] | None = 'n7o1p5q9r3s7'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'job_status_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('from_status', sa.Text(), nullable=True),
        sa.Column('to_status', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_job_status_history_job_id', 'job_status_history', ['job_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_job_status_history_job_id', table_name='job_status_history')
    op.drop_table('job_status_history')
