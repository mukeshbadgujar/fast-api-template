from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from tenacity import retry, stop_after_attempt, wait_exponential
import asyncio

from app.core.settings import settings
import logging

logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
async def create_engine():
    """Create database engine with retry logic."""
    try:
        engine = create_async_engine(
            str(settings.SQLALCHEMY_DATABASE_URI),
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            echo=settings.DEBUG,
        )
        logger.info("Successfully connected to primary database")
        return engine
    except Exception as e:
        logger.warning(f"Failed to connect to primary database: {e}")
        if settings.DB_FALLBACK:
            logger.info("Falling back to SQLite database")
            engine = create_async_engine(
                str(settings.SQLITE_DB_PATH),
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                echo=settings.DEBUG,
            )
            return engine
        raise

# Create async engine
engine = asyncio.run(create_engine())

# Create async session factory
async_session_factory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.
    Handles fallback to SQLite if primary database is unavailable.
    """
    async with async_session_factory() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            logger.error(f"Database session error: {e}")
            if settings.DB_FALLBACK:
                logger.info("Attempting to reconnect with fallback database")
                async with async_session_factory() as fallback_session:
                    yield fallback_session
            else:
                raise 