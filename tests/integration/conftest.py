# ruff: noqa: E501
import asyncio
import os
import uuid

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from securecodecoach.config import get_settings
from securecodecoach.db import session as db_session
from securecodecoach.db.url import to_async_database_url

BASE_URL = os.getenv("TEST_DATABASE_URL")


def pytest_collection_modifyitems(config, items):
    if BASE_URL:
        return
    skip = pytest.mark.skip(reason="set TEST_DATABASE_URL to run integration tests")
    for item in items:
        if "integration" in item.nodeid:
            item.add_marker(skip)


async def _admin(sql: str) -> None:
    engine = create_async_engine(to_async_database_url(BASE_URL), isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        await conn.execute(text(sql))
    await engine.dispose()


@pytest.fixture(scope="session")
def database_url():
    name = f"test_{uuid.uuid4().hex[:8]}"
    asyncio.run(_admin(f'CREATE DATABASE "{name}"'))
    url = make_url(to_async_database_url(BASE_URL)).set(database=name)
    url_str = url.render_as_string(hide_password=False)
    patch = pytest.MonkeyPatch()
    patch.setenv("APP_ENV", "ci")
    patch.setenv("DATABASE_URL", url_str)
    get_settings.cache_clear()
    test_engine = create_async_engine(url_str, pool_pre_ping=True)
    patch.setattr(db_session, "engine", test_engine)
    patch.setattr(
        db_session,
        "AsyncSessionLocal",
        async_sessionmaker(bind=test_engine, expire_on_commit=False),
    )
    command.upgrade(Config("alembic.ini"), "head")
    yield url_str
    asyncio.run(test_engine.dispose())
    get_settings.cache_clear()
    patch.undo()
    asyncio.run(_admin(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
