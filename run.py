import asyncio
import os
import sys
from pathlib import Path

import uvicorn
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text

from app.core.settings import settings
from app.db.base import Base
from app.db.session import async_session_factory


async def init_db():
    """Initialize the database."""
    engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


async def check_db_connection():
    """Check database connection."""
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
            print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)


def main():
    """Main function to run the application."""
    # Check if .env file exists
    if not Path(".env").exists():
        print("❌ .env file not found. Please create one from .env.example")
        sys.exit(1)

    # Initialize database
    print("🔄 Initializing database...")
    asyncio.run(init_db())
    asyncio.run(check_db_connection())

    # Run the application
    print("🚀 Starting FastAPI application...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main() 