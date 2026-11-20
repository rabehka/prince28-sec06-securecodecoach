def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["app"] == "securecodecoach"
    assert "version" in body


def test_health_reports_configured_version(client, monkeypatch):
    monkeypatch.setenv("GIT_SHA", "abc1234")
    from securecodecoach.config import get_settings

    get_settings.cache_clear()
    try:
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["version"] == "abc1234"
    finally:
        get_settings.cache_clear()


def test_ready_up(client):
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json() == {"status": "ready", "checks": {"database": True}}


def test_ready_down(client, db_state):
    db_state["up"] = False
    r = client.get("/ready")
    assert r.status_code == 503
    assert r.json()["checks"]["database"] is False


def test_home(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "message" in r.json()


def test_request_id_header(client):
    r = client.get("/health")
    assert r.headers.get("x-request-id")


def test_request_id_echoed(client):
    r = client.get("/health", headers={"X-Request-ID": "abc-123"})
    assert r.headers["x-request-id"] == "abc-123"


def test_list_all(client):
    body = client.get("/v1/documents").json()
    assert body["total"] == 3
    assert len(body["items"]) == 3
    assert body["filters"] == {}


def test_list_limit(client):
    body = client.get("/v1/documents?limit=2").json()
    assert body["total"] == 3
    assert len(body["items"]) == 2
    assert body["limit"] == 2


def test_list_offset(client):
    body = client.get("/v1/documents?limit=2&offset=2").json()
    assert len(body["items"]) == 1
    assert body["offset"] == 2


def test_filter(client):
    body = client.get("/v1/documents?kind=circular").json()
    assert body["total"] == 2
    assert body["filters"] == {"kind": "circular"}


def test_filter_no_match(client):
    body = client.get("/v1/documents?kind=nothing").json()
    assert body["total"] == 0
    assert body["items"] == []


def test_search_q(client):
    body = client.get("/v1/documents?q=alpha").json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == "001"


def test_bad_filter_name(client):
    r = client.get("/v1/documents?Bad-Name=1")
    assert r.status_code == 400
    assert r.headers["content-type"].startswith("application/problem+json")
    assert r.json()["status"] == 400


def test_limit_too_high(client):
    r = client.get("/v1/documents?limit=1000")
    assert r.status_code == 422
    assert r.json()["title"] == "Unprocessable Content"


def test_get_one(client):
    r = client.get("/v1/documents/002")
    assert r.status_code == 200
    assert r.json()["title"] == "Beta circular"


def test_get_missing(client):
    r = client.get("/v1/documents/999")
    assert r.status_code == 404
    assert r.json()["title"] == "Not Found"
