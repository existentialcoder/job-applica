"""Update skill table

Revision ID: ff74df21b6d8
Revises: 6e93a0e52542
Create Date: 2025-11-22 15:07:54.767274

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff74df21b6d8'
down_revision: Union[str, Sequence[str], None] = '6e93a0e52542'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
