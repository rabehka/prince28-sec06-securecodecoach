"""Unit tests for POST /v1/chat, GET /v1/usage, and prompts/chat_system_v1.md."""

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from securecodecoach.api.main import create_app
from securecodecoach.llm.gateway import FakeLLM, LLMError, LLMGateway


class FakeUsageRepo:
    def __init__(self) -> None:
        self.rows: list[dict] = []

    async def record(self, row: dict) -> None:
        self.rows.append(row)

    async def by_day(self, days: int = 7) -> list[dict]:
        return [
            {
                "day": "2026-11-25",
                "calls": len(self.rows),
                "errors": sum(1 for r in self.rows if r.get("status") == "error"),
                "fallbacks": sum(1 for r in self.rows if r.get("fallback_used")),
                "tokens_in": sum(r.get("tokens_in", 0) for r in self.rows),
                "tokens_out": sum(r.get("tokens_out", 0) for r in self.rows),
                "cost_inr": round(sum(r.get("cost_inr", 0.0) for r in self.rows), 6),
            }
        ]


def _make_test_app(primary_script=None, fallback_script=None):
    app = create_app()
    usage_repo = FakeUsageRepo()
    primary = FakeLLM("gemini", "gemini-3.8-flash", primary_script or ["Use parameterized SQL."])
    fallback = FakeLLM("groq", "openai/gpt-oss-20b", fallback_script or ["Fallback safe SQL."])
    app.state.usage_repo = usage_repo
    app.state.gateway = LLMGateway([primary, fallback], recorder=usage_repo.record)
    return app, usage_repo


def test_system_prompt_has_uncertainty_rule():
    prompt = Path("prompts/chat_system_v1.md").read_text(encoding="utf-8")
    assert "I am not sure" in prompt


@pytest.mark.asyncio
async def test_chat_non_streaming_json():
    app, repo = _make_test_app(["Hash with Argon2id."])
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/v1/chat", json={"message": "Password hashing?", "stream": False})
    assert resp.status_code == 200
    body = resp.json()
    assert body["answer"] == "Hash with Argon2id."
    assert body["provider"] == "gemini"
    assert len(repo.rows) == 1


@pytest.mark.asyncio
async def test_chat_streaming_sse():
    app, repo = _make_test_app(["Validate all inputs."])
    async with (
        AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client,
        client.stream("POST", "/v1/chat", json={"message": "Input check?"}) as resp,
    ):
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/event-stream")
        text = "".join([chunk async for chunk in resp.aiter_text()])
    assert '"delta":' in text
    assert "event: done" in text
    assert len(repo.rows) == 1


@pytest.mark.asyncio
async def test_chat_fallback_when_primary_fails():
    app, _ = _make_test_app([LLMError("500", retryable=False)], ["Groq backup answer."])
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/v1/chat", json={"message": "XSS?", "stream": False})
    assert resp.status_code == 200
    assert resp.json()["provider"] == "groq"
    assert resp.json()["fallback_used"] is True


@pytest.mark.asyncio
async def test_chat_returns_503_when_all_providers_fail():
    app, _ = _make_test_app(
        [LLMError("down", retryable=False)],
        [LLMError("also down", retryable=False)],
    )
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/v1/chat", json={"message": "CSRF?", "stream": False})
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_chat_mid_stream_error_emits_error_event():
    app, _ = _make_test_app([("partial", LLMError("dropped", retryable=True))])
    async with (
        AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client,
        client.stream("POST", "/v1/chat", json={"message": "CORS?"}) as resp,
    ):
        assert resp.status_code == 200
        text = "".join([chunk async for chunk in resp.aiter_text()])
    assert "event: error" in text


@pytest.mark.asyncio
async def test_usage_endpoint_returns_totals():
    app, _ = _make_test_app(["First answer."])
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/v1/chat", json={"message": "Hi", "stream": False})
        usage = await client.get("/v1/usage")
    assert usage.status_code == 200
    data = usage.json()
    assert data["calls"] == 1
    assert len(data["days"]) == 1
