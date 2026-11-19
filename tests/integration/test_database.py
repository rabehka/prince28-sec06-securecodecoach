# ruff: noqa: E501
import inspect
import json
import os
import subprocess
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from securecodecoach.api.main import create_app
from securecodecoach.config import Settings
from securecodecoach.db.models import Document
from securecodecoach.db.repository import DocumentRepository

ROWS = [
    {"id": "001", "title": "Alpha", "kind": "circular", "year": 2024, "tags": ["a", "b"]},
    {"id": "002", "title": "Beta", "kind": "guideline", "year": 2025, "tags": ["b"]},
    {"id": "003", "title": "Gamma", "kind": "circular", "year": 2025, "tags": []},
]


@pytest.fixture
def settings(database_url):
    return Settings(app_env="ci", database_url=database_url, _env_file=None)


@pytest.fixture
async def seeded(settings):
    engine = create_async_engine(settings.database_url)
    async with (
        async_sessionmaker(bind=engine, expire_on_commit=False)() as session,
        session.begin(),
    ):
        await session.execute(text("DELETE FROM documents"))
        for r in ROWS:
            meta = {k: v for k, v in r.items() if k not in ("id", "title")}
            session.add(
                Document(external_id=r["id"], title=r["title"], sha256=r["id"] * 21, metadata_=meta)
            )
    await engine.dispose()
    return settings


async def test_migrations_created_the_tables(settings):
    engine = create_async_engine(settings.database_url)
    async with engine.connect() as conn:
        tables = set(
            await conn.scalars(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            )
        )
        version = await conn.scalar(text("SELECT version_num FROM alembic_version"))
    await engine.dispose()
    assert {"documents", "pages", "alembic_version"} <= tables
    assert version


@pytest.mark.parametrize(
    ("filters", "expected"),
    [
        ({"kind": "circular"}, ["001", "003"]),
        ({"year": "2025"}, ["002", "003"]),
        ({"tags": "b"}, ["001", "002"]),
        ({"kind": "circular", "year": "2025"}, ["003"]),
    ],
)
async def test_repository_filters(seeded, filters, expected):
    engine = create_async_engine(seeded.database_url)
    async with async_sessionmaker(bind=engine, expire_on_commit=False)() as session:
        total, items = await DocumentRepository(session).list(
            q=None, filters=filters, limit=10, offset=0
        )
    await engine.dispose()
    assert [i["id"] for i in items] == expected
    assert total == len(expected)


def test_api_against_real_database(seeded):
    from securecodecoach.api.deps import get_repo

    app = create_app(seeded) if inspect.signature(create_app).parameters else create_app()
    eng = create_async_engine(seeded.database_url)

    async def override_repo():
        async with async_sessionmaker(bind=eng, expire_on_commit=False)() as s:
            yield DocumentRepository(s)

    app.dependency_overrides[get_repo] = override_repo
    with TestClient(app) as client:
        assert client.get("/ready").json()["checks"]["database"] is True
        assert client.get("/v1/documents/002").json()["title"] == "Beta"
        assert client.get("/v1/documents", params={"q": "gamm"}).json()["total"] == 1


def test_loader_is_idempotent(database_url, tmp_path):
    data = tmp_path / "records.json"
    data.write_text(json.dumps([{"id": "L1", "x": 1}, {"id": "L2", "x": 2}]), encoding="utf-8")
    env = {**os.environ, "APP_ENV": "ci", "DATABASE_URL": database_url, "DATA_FILE": str(data)}

    def run() -> str:
        return subprocess.run(
            [sys.executable, "scripts/load_db.py"],
            env=env,
            check=True,
            capture_output=True,
            text=True,
        ).stdout

    assert "Inserted: 20" in run()
    assert "Unchanged: 20" in run()
