"""
scripts/create_admin.py — create an admin user in the database.

Usage:
    python scripts/create_admin.py --username admin_name --password "StrongP@ss1"

Requires the app database to exist (run the app once first to create tables).
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def create_admin(username: str, password: str) -> None:
    """Create or promote a user to admin."""
    # Imports are deferred so config is loaded first
    from config import DATABASE_URL, PASSWORD_MIN_LEN, USERNAME_MIN_LEN, USERNAME_MAX_LEN
    from app.db.base import engine, Base
    from app.db.repo import UserRepo
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    if len(username) < USERNAME_MIN_LEN or len(username) > USERNAME_MAX_LEN:
        print(f"ERROR: username must be {USERNAME_MIN_LEN}-{USERNAME_MAX_LEN} chars.")
        sys.exit(1)
    if len(password) < PASSWORD_MIN_LEN:
        print(f"ERROR: password must be at least {PASSWORD_MIN_LEN} chars.")
        sys.exit(1)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with SessionLocal() as session:
        repo = UserRepo(session)
        user = await repo.get_by_username(username)
        if user:
            user.is_admin = True
            await session.commit()
            print(f"User '{username}' already exists — promoted to admin.")
        else:
            await repo.create(username=username, password=password, is_admin=True)
            print(f"Admin user '{username}' created.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an admin user.")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()
    asyncio.run(create_admin(args.username, args.password))


if __name__ == "__main__":
    main()
