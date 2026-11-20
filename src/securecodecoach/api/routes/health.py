"""Health check endpoints."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from securecodecoach.api.deps import check_db
from securecodecoach.config import get_settings

router = APIRouter()


@router.api_route("/health", methods=["GET", "HEAD"])
async def health_check():
    settings = get_settings()
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env,
        "version": settings.git_sha,
    }


@router.get("/ready")
async def readiness_check(db_ok: bool = Depends(check_db)):
    body = {"status": "ready" if db_ok else "not_ready", "checks": {"database": db_ok}}
    return JSONResponse(status_code=200 if db_ok else 503, content=body)
