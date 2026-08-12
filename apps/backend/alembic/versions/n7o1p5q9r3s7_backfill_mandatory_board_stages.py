"""backfill new mandatory board stages (Accepted, Ghosted, Archived) on existing boards

Revision ID: n7o1p5q9r3s7
Revises: 83c1ba4c87e9
Create Date: 2026-08-13

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = 'n7o1p5q9r3s7'
down_revision: str | Sequence[str] | None = '83c1ba4c87e9'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ACCEPTED_STAGE = {"key": "Accepted", "label": "Accepted", "color": "bg-emerald-600"}
GHOSTED_STAGE = {"key": "Ghosted", "label": "Ghosted", "color": "bg-purple-400"}
ARCHIVED_STAGE = {"key": "Archived", "label": "Archived", "color": "bg-zinc-300"}


def upgrade() -> None:
    import json

    conn = op.get_bind()
    boards = conn.execute(sa.text('SELECT id, stages FROM boards')).fetchall()

    for board_id, stages in boards:
        stages = stages or []
        keys = {s['key'] for s in stages}
        new_stages = list(stages)

        if 'Accepted' not in keys:
            offer_idx = next((i for i, s in enumerate(new_stages) if s['key'] == 'Offer'), None)
            insert_at = offer_idx + 1 if offer_idx is not None else len(new_stages)
            new_stages.insert(insert_at, ACCEPTED_STAGE)

        if 'Ghosted' not in keys:
            new_stages.append(GHOSTED_STAGE)

        if 'Archived' not in keys:
            new_stages.append(ARCHIVED_STAGE)

        if new_stages != stages:
            conn.execute(
                sa.text('UPDATE boards SET stages = CAST(:stages AS jsonb) WHERE id = :id'),
                {"stages": json.dumps(new_stages), "id": board_id},
            )


def downgrade() -> None:
    conn = op.get_bind()
    boards = conn.execute(sa.text('SELECT id, stages FROM boards')).fetchall()

    import json

    for board_id, stages in boards:
        stages = stages or []
        new_stages = [s for s in stages if s['key'] not in ('Accepted', 'Ghosted', 'Archived')]
        if new_stages != stages:
            conn.execute(
                sa.text('UPDATE boards SET stages = CAST(:stages AS jsonb) WHERE id = :id'),
                {"stages": json.dumps(new_stages), "id": board_id},
            )
