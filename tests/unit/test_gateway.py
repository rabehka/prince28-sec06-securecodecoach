"""Unit tests for LLMGateway, CircuitBreaker, OpenAICompatProvider, and FakeLLM."""

import httpx
import pytest

from securecodecoach.config import Settings
from securecodecoach.llm.gateway import (
    CircuitBreaker,
    FakeLLM,
    LLMError,
    LLMGateway,
    LLMResult,
    LLMUnavailable,
    OpenAICompatProvider,
    build_gateway,
    cost_inr,
    estimate_tokens,
)


def test_cost_inr_known_and_unknown_model():
    assert cost_inr("gemini-3.8-flash", 1_000_000, 0, 95.0) == 71.25
    assert cost_inr("unknown-model", 1000, 1000, 95.0) == 0.0
    assert estimate_tokens("abcd" * 5) == 5


def test_circuit_breaker_transitions():
    now = [100.0]
    cb = CircuitBreaker(threshold=2, cooldown=30.0, clock=lambda: now[0])
    assert cb.state == "closed"
    assert cb.allow() is True

    cb.failure()
    assert cb.state == "closed"
    cb.failure()
    assert cb.state == "open"
    assert cb.allow() is False

    now[0] = 130.0
    assert cb.state == "half-open"
    assert cb.allow() is True

    cb.failure()
    assert cb.state == "open"

    now[0] = 160.0
    cb.success()
    assert cb.state == "closed"


@pytest.mark.asyncio
async def test_generate_primary_success_and_records():
    recorded = []

    async def rec(row):
        recorded.append(row)

    primary = FakeLLM("gemini", "gemini-3.8-flash", ["Use Argon2id."])
    fallback = FakeLLM("groq", "openai/gpt-oss-20b", ["Fallback"])
    gw = LLMGateway([primary, fallback], recorder=rec)

    res = await gw.generate([{"role": "user", "content": "How to hash passwords?"}])
    assert res.text == "Use Argon2id."
    assert res.provider == "gemini"
    assert res.fallback_used is False
    assert fallback.calls == 0
    assert len(recorded) == 1
    assert recorded[0]["status"] == "ok"


@pytest.mark.asyncio
async def test_generate_retries_retryable_error_then_succeeds():
    sleeps = []

    async def fake_sleep(sec):
        sleeps.append(sec)

    primary = FakeLLM(
        "gemini",
        "gemini-3.8-flash",
        [LLMError("HTTP 429", retryable=True, retry_after=1.5), "Recovered!"],
    )
    gw = LLMGateway([primary], max_attempts=2, sleep=fake_sleep)
    res = await gw.generate([{"role": "user", "content": "hi"}])
    assert res.text == "Recovered!"
    assert res.attempts == 2
    assert len(sleeps) == 1
    assert sleeps[0] >= 1.5


@pytest.mark.asyncio
async def test_generate_non_retryable_falls_back_immediately():
    primary = FakeLLM("gemini", "gemini-3.8-flash", [LLMError("HTTP 401", retryable=False)])
    fallback = FakeLLM("groq", "openai/gpt-oss-20b", ["Groq answer"])
    gw = LLMGateway([primary, fallback], max_attempts=3)

    res = await gw.generate([{"role": "user", "content": "hi"}])
    assert primary.calls == 1
    assert res.provider == "groq"
    assert res.fallback_used is True


@pytest.mark.asyncio
async def test_generate_open_circuit_skips_primary():
    primary = FakeLLM("gemini", "gemini-3.8-flash", [LLMError("500", retryable=False)])
    fallback = FakeLLM("groq", "openai/gpt-oss-20b", ["From Groq", "From Groq 2"])
    gw = LLMGateway([primary, fallback], breaker_threshold=1)

    await gw.generate([{"role": "user", "content": "q1"}])
    assert primary.calls == 1

    res2 = await gw.generate([{"role": "user", "content": "q2"}])
    assert primary.calls == 1
    assert res2.provider == "groq"


@pytest.mark.asyncio
async def test_generate_all_fail_raises_unavailable():
    primary = FakeLLM("gemini", "gemini-3.8-flash", [LLMError("down", retryable=False)])
    fallback = FakeLLM("groq", "openai/gpt-oss-20b", [LLMError("down too", retryable=False)])
    gw = LLMGateway([primary, fallback])

    with pytest.raises(LLMUnavailable):
        await gw.generate([{"role": "user", "content": "hi"}])


@pytest.mark.asyncio
async def test_stream_success_and_fallback_before_first_piece():
    primary = FakeLLM("gemini", "gemini-3.8-flash", [LLMError("503", retryable=False)])
    fallback = FakeLLM("groq", "openai/gpt-oss-20b", ["Hello world"])
    gw = LLMGateway([primary, fallback])

    items = [item async for item in gw.stream([{"role": "user", "content": "hi"}])]
    pieces = [x for x in items if isinstance(x, str)]
    summary = [x for x in items if isinstance(x, LLMResult)][0]
    assert "".join(pieces).strip() == "Hello world"
    assert summary.provider == "groq"
    assert summary.fallback_used is True


@pytest.mark.asyncio
async def test_stream_mid_answer_failure_does_not_switch_model():
    primary = FakeLLM(
        "gemini",
        "gemini-3.8-flash",
        [("partial", LLMError("stream died", retryable=True))],
    )
    fallback = FakeLLM("groq", "openai/gpt-oss-20b", ["Should not run"])
    gw = LLMGateway([primary, fallback])

    seen = []
    with pytest.raises(LLMUnavailable, match="failed mid-answer"):
        async for item in gw.stream([{"role": "user", "content": "hi"}]):
            seen.append(item)

    assert len(seen) > 0
    assert fallback.calls == 0


@pytest.mark.asyncio
async def test_recorder_error_does_not_break_response():
    async def broken_recorder(_row):
        raise RuntimeError("DB down")

    primary = FakeLLM("gemini", "gemini-3.8-flash", ["Still works"])
    gw = LLMGateway([primary], recorder=broken_recorder)
    res = await gw.generate([{"role": "user", "content": "hi"}])
    assert res.text == "Still works"


@pytest.mark.asyncio
async def test_openai_compat_provider_generate_and_stream():
    def handler(request: httpx.Request) -> httpx.Response:
        if b'"stream":true' in request.content or b'"stream": true' in request.content:
            sse_body = (
                'data: {"choices":[{"delta":{"content":"Safe "}}]}\n\n'
                'data: {"choices":[{"delta":{"content":"code"},"finish_reason":"stop"}],'
                '"usage":{"prompt_tokens":10,"completion_tokens":2}}\n\n'
                "data: [DONE]\n\n"
            )
            return httpx.Response(200, text=sse_body)
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": "Parameterized query"}}],
                "usage": {"prompt_tokens": 15, "completion_tokens": 3},
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = OpenAICompatProvider("gemini", "https://example.test/v1", "key", "m1", client=client)

    rep = await provider.generate([{"role": "user", "content": "SQLi"}])
    assert rep.text == "Parameterized query"
    assert rep.tokens_in == 15

    from securecodecoach.llm.gateway import Reply

    r_usage = Reply()
    chunks = [c async for c in provider.stream([{"role": "user", "content": "SQLi"}], r_usage)]
    assert "".join(chunks) == "Safe code"
    assert r_usage.tokens_in == 10
    assert r_usage.tokens_out == 2
    await client.aclose()


def test_build_gateway_skips_unconfigured_keys():
    gw_empty = build_gateway(Settings(gemini_api_key="", groq_api_key=""))
    assert gw_empty.providers == []

    gw_both = build_gateway(Settings(gemini_api_key="g-key", groq_api_key="q-key"))
    assert [p.name for p in gw_both.providers] == ["gemini", "groq"]
