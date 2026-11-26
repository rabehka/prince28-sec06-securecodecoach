"""Write LLM call logs and aggregate daily usage from llm_calls."""

from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from securecodecoach.db.models import LlmCall


class LlmCallRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def record(self, row: dict) -> None:
        async with self._session_factory() as session:
            session.add(LlmCall(**row))
            await session.commit()

    async def by_day(self, days: int = 7) -> list[dict]:
        cutoff = datetime.now(UTC) - timedelta(days=days)
        day_col = func.date(LlmCall.created_at).label("day")
        stmt = (
            select(
                day_col,
                func.count(LlmCall.id).label("calls"),
                func.sum(case((LlmCall.status == "error", 1), else_=0)).label("errors"),
                func.sum(case((LlmCall.fallback_used.is_(True), 1), else_=0)).label("fallbacks"),
                func.coalesce(func.sum(LlmCall.tokens_in), 0).label("tokens_in"),
                func.coalesce(func.sum(LlmCall.tokens_out), 0).label("tokens_out"),
                func.coalesce(func.sum(LlmCall.cost_inr), 0).label("cost_inr"),
            )
            .where(LlmCall.created_at >= cutoff)
            .group_by(day_col)
            .order_by(day_col.desc())
        )
        async with self._session_factory() as session:
            rows = (await session.execute(stmt)).all()

        return [
            {
                "day": str(r.day),
                "calls": int(r.calls or 0),
                "errors": int(r.errors or 0),
                "fallbacks": int(r.fallbacks or 0),
                "tokens_in": int(r.tokens_in or 0),
                "tokens_out": int(r.tokens_out or 0),
                "cost_inr": round(float(r.cost_inr or 0), 6),
            }
            for r in rows
        ]


def make_recorder(
    session_factory: async_sessionmaker[AsyncSession],
) -> Callable[[dict], Awaitable[None]]:
    repo = LlmCallRepository(session_factory)
    return repo.record
