import os
from typing import AsyncGenerator, Generator, TypeAlias

import pytest
from alembic.command import downgrade, upgrade
from alembic.config import Config as AlembicConfig
from dotenv import load_dotenv
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import DbContainer, PostgresContainer

from mdp2mailservice.common.utils.security import SecretUrl
from mdp2mailservice.core.config import Config, TestConfig
from mdp2mailservice.core.loader import get_application
from mdp2mailservice.main import app

SetupFixture: TypeAlias = None

load_dotenv(".env.test", override=True)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
def settings() -> Config:
    return TestConfig()  # type: ignore


@pytest.fixture(autouse=True)
def check_app_env_mode_enabled() -> None:
    assert os.getenv("ENVIRONMENT") == "test"


@pytest.fixture(scope="session")
def db_container() -> DbContainer:
    return PostgresContainer(image="postgres:16.4", dbname="mdp2mailservice_test").start()


@pytest.fixture(scope="session")
def create_test_db(settings: Config, db_container: PostgresContainer) -> Generator[PostgresContainer, None, None]:
    db_url = db_container.get_connection_url(driver="asyncpg")
    settings.DATABASE_URL = SecretUrl(secret_value=db_url)

    yield db_container

    db_container.stop()


@pytest.fixture(scope="session")
async def async_db_engine(create_test_db: PostgresContainer) -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(
        url=create_test_db.get_connection_url(driver="asyncpg"),
        echo=True,
        poolclass=NullPool,
    )
    yield engine


@pytest.fixture(scope="function")
async def async_session(async_db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        async_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    async with async_session() as session:
        await session.begin()

        yield session

        await session.rollback()


@pytest.fixture(scope="session")
def application(settings: Config, create_test_db: PostgresContainer) -> FastAPI:
    from mdp2mailservice.core.config import settings as app_settings  # type: ignore

    app_settings = settings  # type: ignore
    return get_application()


@pytest.fixture
def alembic_config(settings: Config, async_db_engine: AsyncEngine):
    alembic_config = AlembicConfig()
    alembic_config.set_main_option("script_location", "migrations")
    alembic_config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.get_secret_value())
    return alembic_config


@pytest.fixture(autouse=True)
async def create_tables(async_db_engine: AsyncEngine, alembic_config: AlembicConfig):
    async with async_db_engine.begin() as conn:
        await conn.run_sync(lambda _: upgrade(alembic_config, "head"))

    yield

    async with async_db_engine.connect() as c:
        await c.run_sync(lambda _: downgrade(alembic_config, "base"))


@pytest.fixture(scope="session")
async def test_client(settings: Config, application: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        client.base_url = client.base_url.join(settings.API_PREFIX)
        yield client
