"""Main FastAPI application."""

from fastapi import FastAPI

from securecodecoach.api.routes.health import router as health_router
from securecodecoach.config import get_settings
from securecodecoach.logging_setup import setup_logging

settings = get_settings()

setup_logging(settings.log_level)

app = FastAPI(
    title="SecureCodeCoach",
    description="AI-powered secure coding mentor",
    version="0.1.0",
)

app.include_router(health_router)


@app.get("/")
async def home():
    return {
        "message": "Welcome to SecureCodeCoach!",
        "app_name": settings.app_name,
    }
