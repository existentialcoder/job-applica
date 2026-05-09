"""
Container startup: initialise DB schema.

Fresh DB  → create all tables from models + stamp alembic at head
Existing DB → run pending alembic migrations only
"""
import os
import sys
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, inspect
from src.core.config import settings
from src.db.base_class import Base
import src.models  # registers all ORM models with Base.metadata


def run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)


def main() -> None:
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        is_fresh = not inspect(conn).has_table("alembic_version")

    if is_fresh:
        print("Fresh database — creating schema from models...")
        Base.metadata.create_all(engine)
        print("Schema created. Stamping alembic at head...")
        run(["alembic", "stamp", "head"])
        print("Done.")
    else:
        print("Existing database — running pending migrations...")
        run(["alembic", "upgrade", "head"])
        print("Done.")


if __name__ == "__main__":
    main()
