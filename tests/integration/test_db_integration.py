import pytest
from sqlalchemy import func, select

import scripts.load_db as load_db
from securecodecoach.db.models import Document, Page
from securecodecoach.db.repository import DocumentRepository

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_repository_crud_and_jsonb_filters(db_session):
    d1 = Document(
        external_id="101",
        title="SQL Injection",
        doc_type="Injection",
        source_url="https://owasp.org",
        sha256="h1",
        metadata_={"severity": "Critical", "recommendation": "Use parameterized queries"},
    )
    d2 = Document(
        external_id="102",
        title="XSS",
        doc_type="XSS",
        source_url="https://owasp.org",
        sha256="h2",
        metadata_={"severity": "High", "recommendation": "Escape output"},
    )
    db_session.add_all([d1, d2])
    await db_session.flush()
    db_session.add(Page(document_id=d1.id, page_no=1, text="SQLi details"))
    await db_session.commit()

    repo = DocumentRepository(db_session)
    total, items = await repo.list(q="sql", filters={"severity": "Critical"}, limit=10, offset=0)
    assert total == 1 and items[0]["id"] == "101"
    fetched = await repo.get("102")
    assert fetched is not None and fetched["title"] == "XSS"
    assert await repo.get("999") is None


@pytest.mark.asyncio
async def test_api_endpoints_with_postgres(integration_client):
    r = await integration_client.get("/ready")
    assert r.status_code == 200 and r.json()["status"] == "ready"
    r2 = await integration_client.get("/v1/documents")
    assert r2.status_code == 200 and r2.json()["total"] == 0
    r3 = await integration_client.get("/v1/documents/nonexistent")
    assert r3.status_code == 404


@pytest.mark.asyncio
async def test_load_records_is_idempotent(test_engine, monkeypatch):
    from sqlalchemy.ext.asyncio import async_sessionmaker

    sf = async_sessionmaker(bind=test_engine, expire_on_commit=False)
    monkeypatch.setattr(load_db, "AsyncSessionLocal", sf)
    await load_db.load_records()
    async with sf() as s:
        count1 = await s.scalar(select(func.count()).select_from(Document))
    assert count1 == 20
    await load_db.load_records()
    async with sf() as s:
        count2 = await s.scalar(select(func.count()).select_from(Document))
    assert count2 == 20
