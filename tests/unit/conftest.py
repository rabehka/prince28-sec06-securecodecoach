import pytest
from fastapi.testclient import TestClient

from securecodecoach.api.deps import check_db, get_repo
from securecodecoach.api.main import create_app

SAMPLE = [
    {"id": "001", "title": "Alpha guideline", "year": 2023, "kind": "guideline"},
    {"id": "002", "title": "Beta circular", "year": 2024, "kind": "circular"},
    {"id": "003", "title": "Gamma notice", "year": 2025, "kind": "circular"},
]


class FakeRepo:
    """Behaves like DocumentRepository, but keeps rows in a Python list."""

    def __init__(self, rows):
        self.rows = rows

    async def list(self, *, q, filters, limit, offset):
        rows = [
            r
            for r in self.rows
            if (not q or q.lower() in str(r).lower())
            and all(str(r.get(k)) == v for k, v in filters.items())
        ]
        return len(rows), rows[offset : offset + limit]

    async def get(self, external_id):
        return next((r for r in self.rows if r["id"] == external_id), None)


@pytest.fixture
def db_state():
    return {"up": True}


@pytest.fixture
def client(db_state):
    app = create_app()
    app.dependency_overrides[get_repo] = lambda: FakeRepo(SAMPLE)
    app.dependency_overrides[check_db] = lambda: db_state["up"]
    with TestClient(app) as c:
        yield c
