"""widen company description and logo_url to Text

Revision ID: i2j6k0l4m8n2
Revises: h1i5j9k3l7m2
Create Date: 2026-07-16

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'i2j6k0l4m8n2'
down_revision: Union[str, Sequence[str], None] = 'c2d4e6f8a123'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('companies', 'description', type_=sa.Text(), existing_nullable=True)
    op.alter_column('companies', 'logo_url', type_=sa.Text(), existing_nullable=True)


def downgrade() -> None:
    op.alter_column('companies', 'description', type_=sa.String(500), existing_nullable=True)
    op.alter_column('companies', 'logo_url', type_=sa.String(500), existing_nullable=True)
