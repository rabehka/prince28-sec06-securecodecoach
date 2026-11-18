"""Document API endpoints, backed by PostgreSQL."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from securecodecoach.api.deps import get_repo
from securecodecoach.db.repository import FILTER_KEY, DocumentRepository

router = APIRouter(prefix="/v1/documents", tags=["Documents"])

RESERVED = {"q", "limit", "offset"}


@router.get("")
async def list_documents(
    request: Request,
    repo: DocumentRepository = Depends(get_repo),
    q: str | None = Query(None, max_length=200),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List documents. Every extra query parameter becomes a metadata filter."""
    filters: dict[str, str] = {}
    for key, value in request.query_params.items():
        if key in RESERVED:
            continue
        if not FILTER_KEY.match(key):
            raise HTTPException(status_code=400, detail=f"Invalid filter name: {key}")
        filters[key] = value

    total, items = await repo.list(q=q, filters=filters, limit=limit, offset=offset)
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "filters": filters,
        "items": items,
    }


@router.get("/{document_id}")
async def get_document(document_id: str, repo: DocumentRepository = Depends(get_repo)):
    """Return one document by its external id."""
    doc = await repo.get(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc
