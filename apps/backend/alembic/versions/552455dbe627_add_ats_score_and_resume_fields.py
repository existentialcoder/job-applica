"""add_ats_score_and_resume_fields

Revision ID: 552455dbe627
Revises: h1i5j9k3l7m2
Create Date: 2026-06-26 10:07:38.132207

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '552455dbe627'
down_revision: Union[str, Sequence[str], None] = 'h1i5j9k3l7m2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('jobs', sa.Column('ats_score', sa.Float(), nullable=True))
    op.add_column('jobs', sa.Column('ats_resume_id', sa.Integer(), sa.ForeignKey('resumes.id', ondelete='SET NULL'), nullable=True))
    op.add_column('resumes', sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('resumes', sa.Column('parsed_text', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('resumes', 'parsed_text')
    op.drop_column('resumes', 'is_default')
    op.drop_column('jobs', 'ats_resume_id')
    op.drop_column('jobs', 'ats_score')
