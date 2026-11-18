"""Health check endpoints."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from securecodecoach.api.deps import check_db

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "healthy"}


@router.get("/ready")
async def readiness_check(db_ok: bool = Depends(check_db)):
    body = {"status": "ready" if db_ok else "not_ready", "checks": {"database": db_ok}}
    return JSONResponse(status_code=200 if db_ok else 503, content=body)
