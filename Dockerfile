FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

ENV UV_HTTP_TIMEOUT=120
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY README.md ./
COPY src ./src
RUN uv sync --frozen --no-dev --no-editable


FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

ENV UV_HTTP_TIMEOUT=120
WORKDIR /app

RUN groupadd --system --gid 1001 appgroup && \
    useradd --system --uid 1001 --gid appgroup --create-home appuser

COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv
COPY --chown=appuser:appgroup alembic.ini ./
COPY --chown=appuser:appgroup migrations ./migrations
COPY --chown=appuser:appgroup data ./data
COPY --chown=appuser:appgroup scripts ./scripts

USER appuser

ARG GIT_SHA=dev
ENV GIT_SHA=${GIT_SHA}

EXPOSE 8000

CMD ["uvicorn", "securecodecoach.api.main:create_app --factory", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
