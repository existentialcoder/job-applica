"""move location from locations table into jobs

Revision ID: 83c1ba4c87e9
Revises: m6n0o4p8q2r6
Create Date: 2026-08-05 13:17:37.428744

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '83c1ba4c87e9'
down_revision: Union[str, Sequence[str], None] = 'm6n0o4p8q2r6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create location column in jobs table
    op.add_column('jobs', sa.Column('location', JSONB(), nullable=True))

    # Migrate data from locations table to jobs table
    op.execute(
        """
        UPDATE jobs
        SET location = (
            SELECT json_build_object(
                'city', locations.city,
                'state', locations.state,
                'country', locations.country
            )
            FROM locations
            WHERE jobs.location_id = locations.id
        )
        """
    )

    # Drop the location_id column
    op.drop_column('jobs', 'location_id')

    # Drop the locations table
    op.drop_table('locations')



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('jobs', 'location')

    op.create_table(
        'locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('state', sa.String(), nullable=True),
        sa.Column('country', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    op.add_column('jobs', sa.Column('location_id', sa.Integer(), nullable=True))

    op.execute(
        """
        INSERT INTO locations (city, state, country)
        SELECT DISTINCT
            (location->>'city') AS city,
            (location->>'state') AS state,
            (location->>'country') AS country
        FROM jobs
        WHERE location IS NOT NULL
        """
    )

