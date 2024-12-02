import asyncio
import importlib
import os
import pkgutil
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy.schema import CreateSchema

from mdp2mailservice.common.bases.models import Base
from mdp2mailservice.core.config import settings

for _, pkg, is_pkg in pkgutil.iter_modules([os.path.normpath(os.path.dirname(__file__) + "/../mdp2mailservice/")]):
    try:
        if is_pkg and (pkg != "common"):
            importlib.import_module(f"mdp2mailservice.{pkg}.models")
    except ModuleNotFoundError:
        pass


config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.get_secret_value())

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def include_name(name, type_, parent_names):  # type: ignore
    if type_ == "schema":
        return name in ["mdp2mailservice"]
    else:
        return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_name=include_name,  # type: ignore
    )

    with context.begin_transaction():
        context.run_migrations()


def include_object(object, name, type_, reflected, compare_to):  # type: ignore
    if type_ == "table" and name == "alembic_version":  # type: ignore
        return False
    else:
        return True


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table_schema="mdp2mailservice",
        include_object=include_object,  # type: ignore
        include_schemas=True,
        include_name=include_name,
    )

    with context.begin_transaction():
        connection.execute(CreateSchema("mdp2mailservice", if_not_exists=True))
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
