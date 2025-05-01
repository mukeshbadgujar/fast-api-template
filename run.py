import asyncio
import os
import sys
from pathlib import Path
import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

import uvicorn
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text

from app.core.settings import settings
from app.db.base import Base
from app.db.session import async_session_factory

logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
async def init_db():
    """Initialize the database with retry logic."""
    try:
        engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI))
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()
        logger.info("✅ Database initialization successful")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
async def check_db_connection():
    """Check database connection with retry logic."""
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise

def main():
    """Main function to run the application."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Check if .env file exists
    if not Path(".env").exists():
        logger.error("❌ .env file not found. Please create one from .env.example")
        sys.exit(1)

    # Initialize database
    logger.info("🔄 Initializing database...")
    try:
        asyncio.run(init_db())
        asyncio.run(check_db_connection())
    except Exception as e:
        if settings.DB_FALLBACK:
            logger.warning("⚠️ Using SQLite fallback database")
        else:
            logger.error("❌ Database initialization failed and fallback is disabled")
            sys.exit(1)

    # Run the application
    logger.info("🚀 Starting FastAPI application...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main() 