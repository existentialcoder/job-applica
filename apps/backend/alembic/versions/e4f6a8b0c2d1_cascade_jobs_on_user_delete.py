"""cascade jobs on user delete

Every other user-owned table already cascades from users.id; jobs was created without it, so deleting a
user with applications failed on jobs_user_id_fkey.

Revision ID: e4f6a8b0c2d1
Revises: d9e1f3a5c7b2
Create Date: 2026-10-14

"""

from collections.abc import Sequence

from alembic import op

revision: str = 'e4f6a8b0c2d1'
down_revision: str | Sequence[str] | None = 'd9e1f3a5c7b2'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint('jobs_user_id_fkey', 'jobs', type_='foreignkey')
    op.create_foreign_key('jobs_user_id_fkey', 'jobs', 'users', ['user_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    op.drop_constraint('jobs_user_id_fkey', 'jobs', type_='foreignkey')
    op.create_foreign_key('jobs_user_id_fkey', 'jobs', 'users', ['user_id'], ['id'])
