import asyncio
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.user import UserService


# Create test database engine
test_engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI).replace("app", "test_app"),
    echo=False,
    future=True,
)

# Create test session factory
TestAsyncSession = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestAsyncSession() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await test_engine.dispose()


@pytest.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[TestClient, None]:
    """Create a test client."""
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def test_user(db: AsyncSession) -> User:
    """Create a test user."""
    service = UserService(db)
    user = await service.create(
        UserCreate(
            email="test@example.com",
            password="password123",
            full_name="Test User",
        )
    )
    return user