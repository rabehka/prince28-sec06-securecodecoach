"""Tests for the document API."""

from fastapi.testclient import TestClient

from securecodecoach.api.main import app

client = TestClient(app)


def test_get_all_documents():
    response = client.get("/v1/documents")
    assert response.status_code == 200
    assert len(response.json()) >= 5


def test_get_single_document():
    response = client.get("/v1/documents/1")
    assert response.status_code == 200
    assert response.json()["name"] == "SQL Injection"


def test_document_not_found():
    response = client.get("/v1/documents/999")
    assert response.status_code == 404
    assert response.json()["title"] == "Not Found"


def test_invalid_document_id():
    response = client.get("/v1/documents/abc")
    assert response.status_code == 422
    assert response.json()["title"] == "Unprocessable Content"


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_readiness_check():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
