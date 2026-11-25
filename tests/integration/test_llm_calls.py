"""Integration test verifying LlmCallRepository against PostgreSQL."""

import pytest

from securecodecoach.db.llm_calls import LlmCallRepository


@pytest.mark.asyncio
async def test_llm_call_repository_records_and_aggregates(db_session_factory):
    repo = LlmCallRepository(db_session_factory)
    await repo.record(
        {
            "request_id": "req-int-1",
            "provider": "gemini",
            "model": "gemini-3.8-flash",
            "purpose": "chat",
            "prompt_version": "chat_system_v1",
            "status": "ok",
            "tokens_in": 100,
            "tokens_out": 50,
            "latency_ms": 420,
            "cost_inr": 0.024938,
            "fallback_used": False,
        }
    )
    days = await repo.by_day(days=1)
    assert len(days) >= 1
    assert days[0]["calls"] >= 1
    assert days[0]["tokens_in"] >= 100
