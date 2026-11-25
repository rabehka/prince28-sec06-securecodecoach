"""Shared FastAPI dependencies: DB session, repository, readiness check, LLM gateway."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from securecodecoach.db.llm_calls import LlmCallRepository
from securecodecoach.db.repository import DocumentRepository
from securecodecoach.db.session import AsyncSessionLocal, engine
from securecodecoach.llm.gateway import LLMGateway


async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_repo(session: AsyncSession = Depends(get_session)) -> DocumentRepository:
    return DocumentRepository(session)


async def check_db() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def get_gateway(request: Request) -> LLMGateway:
    return request.app.state.gateway


def get_usage_repo(request: Request) -> LlmCallRepository:
    return request.app.state.usage_repo


GatewayDep = Annotated[LLMGateway, Depends(get_gateway)]
UsageDep = Annotated[LlmCallRepository, Depends(get_usage_repo)]
