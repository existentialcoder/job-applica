"""Add connected_accounts table, migrate google_id/linkedin_id, drop old columns

Revision ID: g4h8j2k5m9n1
Revises: f2a9c3e7b016
Create Date: 2026-05-10
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = 'g4h8j2k5m9n1'
down_revision: Union[str, Sequence[str], None] = 'a1b3c5d7e902'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    from sqlalchemy import inspect
    insp = inspect(conn)
    tables = set(insp.get_table_names())

    if 'connected_accounts' not in tables:
        op.create_table(
            'connected_accounts',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('provider', sa.String(50), nullable=False),
            sa.Column('provider_user_id', sa.String(255), nullable=False),
            sa.Column('provider_email', sa.String(255), nullable=True),
            sa.Column('display_name', sa.String(255), nullable=True),
            sa.Column('avatar_url', sa.String(500), nullable=True),
            sa.Column('access_token', sa.Text(), nullable=True),
            sa.Column('refresh_token', sa.Text(), nullable=True),
            sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('scopes', JSONB(), nullable=False, server_default='[]'),
            sa.Column('connected_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id', 'provider', name='uq_connected_accounts_user_provider'),
        )
        op.create_index(
            'ix_connected_accounts_provider_uid',
            'connected_accounts',
            ['provider', 'provider_user_id'],
            unique=True,
        )
        op.create_index('ix_connected_accounts_user_id', 'connected_accounts', ['user_id'])

    # Migrate existing google_id rows → connected_accounts
    cols = {c['name'] for c in insp.get_columns('users')}

    if 'google_id' in cols:
        conn.execute(sa.text("""
            INSERT INTO connected_accounts
                (user_id, provider, provider_user_id, provider_email, scopes, connected_at, last_used_at, created_at, updated_at)
            SELECT
                u.id,
                'google',
                u.google_id,
                u.email,
                '["openid","email","profile"]'::jsonb,
                now(), now(), now(), now()
            FROM users u
            WHERE u.google_id IS NOT NULL
            ON CONFLICT (user_id, provider) DO NOTHING
        """))

    if 'linkedin_id' in cols:
        conn.execute(sa.text("""
            INSERT INTO connected_accounts
                (user_id, provider, provider_user_id, provider_email, scopes, connected_at, last_used_at, created_at, updated_at)
            SELECT
                u.id,
                'linkedin',
                u.linkedin_id,
                u.email,
                '["openid","email","profile"]'::jsonb,
                now(), now(), now(), now()
            FROM users u
            WHERE u.linkedin_id IS NOT NULL
            ON CONFLICT (user_id, provider) DO NOTHING
        """))

    # Drop deprecated columns from users
    if 'google_id' in cols:
        op.drop_index('ix_users_google_id', table_name='users', if_exists=True)
        op.drop_column('users', 'google_id')

    if 'linkedin_id' in cols:
        op.drop_index('ix_users_linkedin_id', table_name='users', if_exists=True)
        op.drop_column('users', 'linkedin_id')


def downgrade() -> None:
    # Re-add columns to users
    op.add_column('users', sa.Column('google_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('linkedin_id', sa.String(255), nullable=True))
    op.create_index('ix_users_google_id', 'users', ['google_id'], unique=True)
    op.create_index('ix_users_linkedin_id', 'users', ['linkedin_id'], unique=True)

    # Migrate data back
    conn = op.get_bind()
    conn.execute(sa.text("""
        UPDATE users u
        SET google_id = ca.provider_user_id
        FROM connected_accounts ca
        WHERE ca.user_id = u.id AND ca.provider = 'google'
    """))
    conn.execute(sa.text("""
        UPDATE users u
        SET linkedin_id = ca.provider_user_id
        FROM connected_accounts ca
        WHERE ca.user_id = u.id AND ca.provider = 'linkedin'
    """))

    op.drop_index('ix_connected_accounts_provider_uid', table_name='connected_accounts')
    op.drop_index('ix_connected_accounts_user_id', table_name='connected_accounts')
    op.drop_table('connected_accounts')
