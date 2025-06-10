import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from events_app.core.config import settings
except ImportError as e:
    print(f'Ошибка импорта {e}')
    sys.exit(1)
from events_app.db.models import Base

config = context.config

section = config.config_ini_section
config.set_section_option(section, "DB_HOST", settings.DB_HOST)
config.set_section_option(section, "DB_PORT", settings.DB_PORT)
config.set_section_option(section, "DB_USER", settings.DB_USER)
config.set_section_option(section, "DB_NAME", settings.DB_NAME)
config.set_section_option(section, "DB_PASS", settings.DB_PASS)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url():
    return settings.ASYNC_DATABASE_URL


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""

    configuration = context.config
    connectable = async_engine_from_config(
        configuration.get_section(configuration.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=get_url()
    )

    async def run_migrations():
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

    def do_run_migrations(connection: Connection):
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

    asyncio.run(run_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
