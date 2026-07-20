"""
Container startup: initialise DB schema.

Fresh DB  → create all tables from models + stamp alembic at head
Existing DB → run pending alembic migrations only
"""
import asyncio
import os
import sys
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine
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


async def main() -> None:
    url = settings.DATABASE_URL
    if url.startswith('postgresql://') or url.startswith('postgres://'):
        url = url.replace('://', '+asyncpg://', 1)

    engine = create_async_engine(url)

    async with engine.connect() as conn:
        is_fresh = not await conn.run_sync(
            lambda c: inspect(c).has_table("alembic_version")
        )

    await engine.dispose()

    if is_fresh:
        print("Fresh database — creating schema from models...")
        engine = create_async_engine(url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()
        print("Schema created. Stamping alembic at head...")
        run(["alembic", "stamp", "head"])
        print("Done.")
    else:
        print("Existing database — running pending migrations...")
        run(["alembic", "upgrade", "head"])
        print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
