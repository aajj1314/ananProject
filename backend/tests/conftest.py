"""Pytest fixtures for backend API tests."""

import os
from collections.abc import AsyncIterator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_elderly_insole.db"
os.environ["REDIS_URL"] = "redis://localhost:6399/15"

from app.main import app  # noqa: E402
from app.models.base import Base  # noqa: E402
from app.utils.database import get_db_session  # noqa: E402


test_engine = create_async_engine(os.environ["DATABASE_URL"], future=True)
TestingSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_db() -> AsyncIterator[AsyncSession]:
    """Provide a test database session."""

    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db_session] = override_db


@pytest_asyncio.fixture(autouse=True)
async def prepare_database() -> AsyncIterator[None]:
    """Reset the test database before each test."""

    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """Build a test HTTP client."""

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client
