import asyncio
import hashlib
import json
from pathlib import Path

from sqlalchemy import select

from securecodecoach.db.models import Document, Page
from securecodecoach.db.session import AsyncSessionLocal, engine

DATA_FILE = Path("data/sample_records.json")


def calculate_sha256(record: dict) -> str:
    """Generate a unique hash based on record content."""
    content = json.dumps(
        record,
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


async def load_records() -> None:
    records = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    inserted = 0
    unchanged = 0
    updated = 0

    async with AsyncSessionLocal() as session:
        for record in records:
            external_id = str(record["id"])
            content_hash = calculate_sha256(record)
            source_url = record.get("source_url")

            result = await session.execute(
                select(Document).where(Document.external_id == external_id)
            )
            document = result.scalar_one_or_none()

            metadata = {
                "severity": record["severity"],
                "recommendation": record["recommendation"],
            }

            if document is None:
                document = Document(
                    external_id=external_id,
                    title=record["name"],
                    doc_type=record["category"],
                    source_url=source_url,
                    sha256=content_hash,
                    metadata_=metadata,
                )

                session.add(document)
                await session.flush()

                session.add(
                    Page(
                        document_id=document.id,
                        page_no=1,
                        text=record["description"],
                    )
                )

                inserted += 1

            elif document.sha256 == content_hash and document.source_url == source_url:
                unchanged += 1

            else:
                document.title = record["name"]
                document.doc_type = record["category"]
                document.source_url = source_url
                document.sha256 = content_hash
                document.metadata_ = metadata

                page_result = await session.execute(
                    select(Page).where(
                        Page.document_id == document.id,
                        Page.page_no == 1,
                    )
                )
                page = page_result.scalar_one_or_none()

                if page is not None:
                    page.text = record["description"]
                else:
                    session.add(
                        Page(
                            document_id=document.id,
                            page_no=1,
                            text=record["description"],
                        )
                    )

                updated += 1

        await session.commit()

    print(f"Inserted: {inserted}")
    print(f"Unchanged: {unchanged}")
    print(f"Updated: {updated}")


async def main():
    try:
        await load_records()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
