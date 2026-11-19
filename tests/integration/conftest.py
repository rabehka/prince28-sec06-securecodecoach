import os

import asyncpg
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

import securecodecoach.api.deps as deps
from securecodecoach.api.deps import get_session
from securecodecoach.api.main import create_app
from securecodecoach.config import get_settings
from securecodecoach.db.models import Base
from securecodecoach.db.url import get_connect_args

TEST_DB = os.getenv("TEST_DB_NAME", "securecodecoach_test")
_DB_CFG = dict(
    user=os.getenv("TEST_DB_USER", "postgres"),
    password=os.getenv("TEST_DB_PASSWORD", "postgres"),
    host=os.getenv("TEST_DB_HOST", "127.0.0.1"),
    port=int(os.getenv("TEST_DB_PORT", "5432")),
)
TEST_URL = URL.create(
    "postgresql+asyncpg",
    username=_DB_CFG["user"],
    password=_DB_CFG["password"],
    host=_DB_CFG["host"],
    port=_DB_CFG["port"],
    database=TEST_DB,
)


async def _recreate_db(drop_only=False):
    conn = await asyncpg.connect(database="postgres", **_DB_CFG)
    try:
        await conn.execute(
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
            "WHERE datname = $1 AND pid != pg_backend_pid()",
            TEST_DB,
        )
        await conn.execute(f'DROP DATABASE IF EXISTS "{TEST_DB}"')
        if not drop_only:
            await conn.execute(f'CREATE DATABASE "{TEST_DB}"')
    finally:
        await conn.close()


@pytest_asyncio.fixture
async def test_engine():
    await _recreate_db(False)
    eng = create_async_engine(
        TEST_URL, poolclass=NullPool, connect_args=get_connect_args(str(TEST_URL))
    )
    async with eng.begin() as c:
        await c.run_sync(Base.metadata.create_all)
    try:
        yield eng
    finally:
        await eng.dispose()
        await _recreate_db(True)


@pytest_asyncio.fixture
async def db_session(test_engine):
    sf = async_sessionmaker(bind=test_engine, expire_on_commit=False)
    async with sf() as s:
        yield s
        await s.rollback()


@pytest_asyncio.fixture
async def integration_client(test_engine, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", TEST_URL.render_as_string(hide_password=False))
    get_settings.cache_clear()
    monkeypatch.setattr(deps, "engine", test_engine)
    sf = async_sessionmaker(bind=test_engine, expire_on_commit=False)

    async def _get_session():
        async with sf() as s:
            yield s

    app = create_app()
    app.dependency_overrides[get_session] = _get_session
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client
    app.dependency_overrides.clear()
    get_settings.cache_clear()
