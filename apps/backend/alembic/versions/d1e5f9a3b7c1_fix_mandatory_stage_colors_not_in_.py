"""fix mandatory stage colors not in tailwind's scanned content

Revision ID: d1e5f9a3b7c1
Revises: c9cdaadccda0
Create Date: 2026-09-06

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = 'd1e5f9a3b7c1'
down_revision: str | Sequence[str] | None = 'c9cdaadccda0'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

COLOR_FIXES = {
    'Accepted': ('bg-emerald-600', 'bg-teal-500'),
    'Rejected': ('bg-red-500', 'bg-rose-500'),
    'Ghosted': ('bg-purple-400', 'bg-violet-500'),
    'Archived': ('bg-zinc-300', 'bg-pink-500'),
}


def _apply(colors_by_key: dict[str, str]) -> None:
    import json

    conn = op.get_bind()
    boards = conn.execute(sa.text('SELECT id, stages FROM boards')).fetchall()

    for board_id, stages in boards:
        stages = stages or []
        new_stages = [{**s, 'color': colors_by_key[s['key']]} if s['key'] in colors_by_key else s for s in stages]

        if new_stages != stages:
            conn.execute(
                sa.text('UPDATE boards SET stages = CAST(:stages AS jsonb) WHERE id = :id'),
                {'stages': json.dumps(new_stages), 'id': board_id},
            )


def upgrade() -> None:
    """Upgrade schema."""
    _apply({key: new for key, (_old, new) in COLOR_FIXES.items()})


def downgrade() -> None:
    """Downgrade schema."""
    _apply({key: old for key, (old, _new) in COLOR_FIXES.items()})
