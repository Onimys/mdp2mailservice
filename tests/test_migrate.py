import inspect

from sqlalchemy import Connection, inspect
from sqlalchemy.ext.asyncio import AsyncSession

from mdp2mailservice.core.db import Base

_SCHEMA = "mdp2mailservice"


async def test_alembic_migrate_schema_exists(async_session: AsyncSession):
    def get_schemas(conn: Connection) -> list[str]:
        return inspector.get_schema_names() if (inspector := inspect(conn)) else []

    async with async_session.bind.connect() as connection:  # type: ignore
        db_schemas = await connection.run_sync(get_schemas)
        assert _SCHEMA in db_schemas


async def test_alembic_migrate_table_exists(async_session: AsyncSession):
    expected = Base.metadata.tables.keys()

    def get_tables(conn: Connection) -> set[str]:
        tables = inspector.get_table_names(_SCHEMA) if (inspector := inspect(conn)) else []
        return {f"{_SCHEMA}.{table}" for table in tables}

    async with async_session.bind.connect() as connection:  # type: ignore
        db_tables = await connection.run_sync(get_tables)
        for table in expected:
            assert table in db_tables
