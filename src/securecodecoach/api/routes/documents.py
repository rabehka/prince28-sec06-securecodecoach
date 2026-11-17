"""Document API endpoints."""

from fastapi import APIRouter, HTTPException

from securecodecoach.config import get_settings
from securecodecoach.data_loader import load_security_records

router = APIRouter(prefix="/v1/documents", tags=["Documents"])


@router.get("")
async def get_documents():
    """Return all security documents."""
    settings = get_settings()
    return load_security_records(settings.data_file)


@router.get("/{document_id}")
async def get_document(document_id: int):
    """Return one security document by ID."""
    settings = get_settings()
    records = load_security_records(settings.data_file)

    for record in records:
        if record.get("id") == document_id:
            return record

    raise HTTPException(status_code=404, detail="Document not found")
