"""strip persisted color from mandatory board stages

Revision ID: 27fb1b042a4e
Revises: d1e5f9a3b7c1
Create Date: 2026-09-12

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = '27fb1b042a4e'
down_revision: str | Sequence[str] | None = 'd1e5f9a3b7c1'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MANDATORY_STAGE_KEYS = [
    'Saved',
    'Applied',
    'Phone Screen',
    'Interview',
    'Offer',
    'Accepted',
    'Rejected',
    'Withdrawn',
    'Ghosted',
    'Archived',
]

# Colors as they stood right before this change — used only to restore them on downgrade.
DEFAULT_COLORS = {
    'Saved': 'bg-slate-500',
    'Applied': 'bg-blue-500',
    'Phone Screen': 'bg-amber-500',
    'Interview': 'bg-amber-500',
    'Offer': 'bg-emerald-500',
    'Accepted': 'bg-teal-500',
    'Rejected': 'bg-rose-500',
    'Withdrawn': 'bg-zinc-400',
    'Ghosted': 'bg-violet-500',
    'Archived': 'bg-pink-500',
}


def _apply(strip: bool) -> None:
    import json

    conn = op.get_bind()
    boards = conn.execute(sa.text('SELECT id, stages FROM boards')).fetchall()

    for board_id, stages in boards:
        stages = stages or []
        if strip:
            new_stages = [
                {k: v for k, v in s.items() if k != 'color'} if s['key'] in MANDATORY_STAGE_KEYS else s for s in stages
            ]
        else:
            new_stages = [
                {**s, 'color': DEFAULT_COLORS[s['key']]} if s['key'] in DEFAULT_COLORS and 'color' not in s else s
                for s in stages
            ]

        if new_stages != stages:
            conn.execute(
                sa.text('UPDATE boards SET stages = CAST(:stages AS jsonb) WHERE id = :id'),
                {'stages': json.dumps(new_stages), 'id': board_id},
            )


def upgrade() -> None:
    """Upgrade schema."""
    _apply(strip=True)


def downgrade() -> None:
    """Downgrade schema."""
    _apply(strip=False)
