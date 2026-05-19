import os
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text, Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from src.main import app

TestBase = declarative_base()

class TestUser(TestBase):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")

test_engine = create_async_engine(DATABASE_URL, echo=False)
TestAsyncSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.drop_all)


@pytest_asyncio.fixture(scope='function')
async def db() -> AsyncSession:
    async with TestAsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def test_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(autouse=True)
async def clear_table(db: AsyncSession) -> None:
    await db.execute(text("DELETE FROM users;"))
    await db.commit()


@pytest_asyncio.fixture
async def user(db: AsyncSession) -> TestUser:
    user = TestUser(name="John Doe")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
