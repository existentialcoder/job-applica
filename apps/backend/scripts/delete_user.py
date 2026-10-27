"""
Delete a user, everything they own (Postgres cascades from users.id) and their uploaded files. Local only.

Run from apps/backend:
api-backend-env/bin/python scripts/delete_user.py --user you@example.com
"""

import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import delete, select

from src.core.config import settings
from src.db.session import AsyncSessionLocal
from src.models.user import User
from src.utils.file_storage import get_file_storage_factory


async def main(identifier: str) -> None:
    async with AsyncSessionLocal() as db:
        user = await db.scalar(select(User).where((User.email == identifier) | (User.user_name == identifier)))
        if user is None:
            sys.exit(f'No user with email or username {identifier!r}')
        user_id = user.id
        await get_file_storage_factory()().delete_prefix(f'{user_id}/')
        await db.execute(delete(User).where(User.id == user_id))
        await db.commit()
    print(f'Deleted user {user_id} ({identifier})')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--user', required=True, help="The user's email or username")
    args = parser.parse_args()
    if settings.APP_ENV != 'local':
        sys.exit(f'Refusing to run with APP_ENV={settings.APP_ENV!r}; this script is for local databases only.')
    asyncio.run(main(args.user))
