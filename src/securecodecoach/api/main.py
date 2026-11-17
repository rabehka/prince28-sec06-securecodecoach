"""Main FastAPI application."""

import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from securecodecoach.api.routes.documents import router as documents_router
from securecodecoach.api.routes.health import router as health_router
from securecodecoach.config import get_settings
from securecodecoach.logging_setup import request_id_var, setup_logging

settings = get_settings()

setup_logging(settings.log_level)

logger = logging.getLogger("securecodecoach")

app = FastAPI(
    title="SecureCodeCoach",
    description="AI-powered secure coding mentor",
    version="0.1.0",
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Attach a unique request ID to every request."""
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    token = request_id_var.set(request_id)

    try:
        response = await call_next(request)

        logger.info(
            "%s %s %s",
            request.method,
            request.url.path,
            response.status_code,
        )

        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        request_id_var.reset(token)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Return HTTP errors in Problem Details format."""
    titles = {
        404: "Not Found",
    }

    return JSONResponse(
        status_code=exc.status_code,
        media_type="application/problem+json",
        content={
            "type": "about:blank",
            "title": titles.get(exc.status_code, "HTTP Error"),
            "status": exc.status_code,
            "detail": str(exc.detail),
            "instance": request.url.path,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return validation errors in Problem Details format."""
    return JSONResponse(
        status_code=422,
        media_type="application/problem+json",
        content={
            "type": "about:blank",
            "title": "Unprocessable Content",
            "status": 422,
            "detail": "Request validation failed",
            "instance": request.url.path,
        },
    )


app.include_router(health_router)
app.include_router(documents_router)


@app.get("/")
async def home():
    return {
        "message": "Welcome to SecureCodeCoach!",
        "app_name": settings.app_name,
    }
