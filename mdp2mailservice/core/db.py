from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from mdp2mailservice.common.bases.models import Base

from .config import settings
from .logging import get_logger

logger = get_logger(__name__)

engine = create_async_engine(
    settings.DATABASE_URL.get_secret_value(),
    echo=settings.ENVIRONMENT == "development",
    future=True,
    pool_pre_ping=True,
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        except Exception:
            logger.error("SQL Error in transaction", exc_info=True)
            await session.rollback()
            raise
        finally:
            await session.close()
