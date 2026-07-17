"""deduplicate locations and add unique constraint on (city, state, country)

Revision ID: l5m9n3o7p1q5
Revises: k4l8m2n6o0p4
Create Date: 2026-07-17

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'l5m9n3o7p1q5'
down_revision: Union[str, None] = 'k4l8m2n6o0p4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Re-point jobs that reference a duplicate location to the canonical (lowest id) row,
    # then delete the orphaned duplicates.
    op.execute("""
        UPDATE jobs
        SET location_id = canonical.id
        FROM (
            SELECT DISTINCT ON (LOWER(COALESCE(city,'')), LOWER(COALESCE(state,'')), LOWER(COALESCE(country,'')))
                id,
                LOWER(COALESCE(city,''))    AS city_key,
                LOWER(COALESCE(state,''))   AS state_key,
                LOWER(COALESCE(country,'')) AS country_key
            FROM locations
            ORDER BY
                LOWER(COALESCE(city,'')),
                LOWER(COALESCE(state,'')),
                LOWER(COALESCE(country,'')),
                id ASC
        ) AS canonical
        JOIN locations dup ON
            LOWER(COALESCE(dup.city,''))    = canonical.city_key AND
            LOWER(COALESCE(dup.state,''))   = canonical.state_key AND
            LOWER(COALESCE(dup.country,'')) = canonical.country_key
        WHERE jobs.location_id = dup.id
          AND dup.id != canonical.id
    """)

    op.execute("""
        DELETE FROM locations
        WHERE id NOT IN (
            SELECT DISTINCT ON (LOWER(COALESCE(city,'')), LOWER(COALESCE(state,'')), LOWER(COALESCE(country,'')))
                id
            FROM locations
            ORDER BY
                LOWER(COALESCE(city,'')),
                LOWER(COALESCE(state,'')),
                LOWER(COALESCE(country,'')),
                id ASC
        )
    """)

    op.create_unique_constraint(
        'uq_locations_city_state_country',
        'locations',
        ['city', 'state', 'country']
    )


def downgrade() -> None:
    op.drop_constraint('uq_locations_city_state_country', 'locations', type_='unique')
