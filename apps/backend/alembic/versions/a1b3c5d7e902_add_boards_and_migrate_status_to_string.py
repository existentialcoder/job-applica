"""add boards table, board_id on jobs, migrate status enum to string

Revision ID: a1b3c5d7e902
Revises: f2a9c3e7b016
Create Date: 2026-04-24

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = 'a1b3c5d7e902'
down_revision: Union[str, Sequence[str], None] = 'f2a9c3e7b016'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEFAULT_STAGES = [
    {"key": "Saved", "label": "Saved", "color": "bg-slate-500"},
    {"key": "Applied", "label": "Applied", "color": "bg-blue-500"},
    {"key": "Phone Screen", "label": "Phone Screen", "color": "bg-amber-500"},
    {"key": "Interview", "label": "Interview", "color": "bg-amber-500"},
    {"key": "Technical", "label": "Technical", "color": "bg-orange-500"},
    {"key": "Offer", "label": "Offer", "color": "bg-emerald-500"},
    {"key": "Rejected", "label": "Rejected", "color": "bg-red-500"},
    {"key": "Withdrawn", "label": "Withdrawn", "color": "bg-zinc-400"},
]


def upgrade() -> None:
    import json
    from sqlalchemy import inspect

    conn = op.get_bind()
    insp = inspect(conn)
    existing_tables = insp.get_table_names()
    existing_jobs_cols = [c['name'] for c in insp.get_columns('jobs')]

    # 1. Create boards table only if it doesn't already exist
    if 'boards' not in existing_tables:
        op.create_table(
            'boards',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('color', sa.String(30), nullable=True),
            sa.Column('description', sa.String(500), nullable=True),
            sa.Column('stages', JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
            sa.Column('is_default', sa.Boolean(), nullable=False, server_default=sa.text('false')),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_boards_user_id', 'boards', ['user_id'])

    # 2. Add board_id column to jobs if not already present
    if 'board_id' not in existing_jobs_cols:
        op.add_column('jobs', sa.Column('board_id', sa.Integer(), nullable=True))

    # 3. Migrate status column from PostgreSQL enum to varchar if still an enum
    status_type_row = conn.execute(
        sa.text("SELECT udt_name FROM information_schema.columns WHERE table_name='jobs' AND column_name='status'")
    ).fetchone()
    if status_type_row and status_type_row[0] == 'applicationstatus':
        op.execute('ALTER TABLE jobs ALTER COLUMN status TYPE VARCHAR(100) USING status::text')
        op.execute("DROP TYPE IF EXISTS applicationstatus")

    # 4. Seed: create one default board per user and assign their jobs to it
    stages_json = json.dumps(DEFAULT_STAGES)
    users = conn.execute(sa.text('SELECT id FROM users')).fetchall()
    for (user_id,) in users:
        existing = conn.execute(
            sa.text('SELECT id FROM boards WHERE user_id = :uid AND is_default = true'),
            {'uid': user_id},
        ).fetchone()
        if existing:
            board_id = existing[0]
        else:
            result = conn.execute(
                sa.text(
                    "INSERT INTO boards (name, color, stages, is_default, user_id, created_at, updated_at) "
                    "VALUES ('My Board', 'bg-blue-500', CAST(:stages AS jsonb), true, :user_id, now(), now()) "
                    "RETURNING id"
                ),
                {"stages": stages_json, "user_id": user_id},
            )
            board_id = result.fetchone()[0]
        conn.execute(
            sa.text('UPDATE jobs SET board_id = :board_id WHERE user_id = :user_id AND board_id IS NULL'),
            {"board_id": board_id, "user_id": user_id},
        )

    # 5. Add FK constraint (skip if already exists)
    existing_fks = [fk['name'] for fk in insp.get_foreign_keys('jobs')]
    if 'fk_jobs_board_id' not in existing_fks:
        op.create_foreign_key('fk_jobs_board_id', 'jobs', 'boards', ['board_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    op.drop_constraint('fk_jobs_board_id', 'jobs', type_='foreignkey')
    op.drop_column('jobs', 'board_id')

    # Recreate the enum and restore the column type
    op.execute(
        "CREATE TYPE applicationstatus AS ENUM "
        "('Saved','Applied','Phone Screen','Interview','Technical','Offer','Rejected','Withdrawn')"
    )
    op.execute(
        "ALTER TABLE jobs ALTER COLUMN status TYPE applicationstatus "
        "USING status::applicationstatus"
    )

    op.drop_index('ix_boards_user_id', table_name='boards')
    op.drop_table('boards')
