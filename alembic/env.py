import asyncio
import os
import sys
from pathlib import Path

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from infrastructure.database.models import (  # noqa: F401
    launcher_model,
    login_history_model,
    minecraft_profile_model,
    session_model,
    user_model,
    wardrobe_model,
)
from infrastructure.database.models.base import Base

target_metadata = Base.metadata


def _get_db_url() -> str:
    if url := os.environ.get("DATABASE__URL"):
        return url
    env_file = Path(__file__).resolve().parents[1] / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("DATABASE__URL=") and not line.startswith("#"):
                return line.split("=", 1)[1].strip().strip("\"'")
    raise RuntimeError("DATABASE__URL is not set")


_db_url = _get_db_url()


def run_migrations_offline() -> None:
    context.configure(
        url=_db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = create_async_engine(_db_url)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
