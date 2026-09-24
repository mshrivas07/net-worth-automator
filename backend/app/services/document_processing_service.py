# app/services/document_processing_service.py
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.document import Document
from app.models.extraction_result import ExtractionResult
from app.services.extraction_service import ExtractionService
from app.services.storage_service import StorageService  # your Phase 2 blob/file loader


async def run_extraction(document_id: UUID) -> None:
    """
    Background task entrypoint — called via BackgroundTasks after upload.
    Owns its own DB session since it runs outside the request's session lifecycle.
    """
    async with AsyncSessionLocal() as db:
        document = await db.get(Document, document_id)
        if document is None:
            return  # shouldn't happen, but don't crash a background task on it

        document.status = "PROCESSING"
        await db.commit()

        try:
            file_bytes = await StorageService.load(document.storage_path)
            extraction_data = await ExtractionService().extract(file_bytes, document.mime_type)
        except Exception as exc:
            document.status = "FAILED"
            document.error_message = str(exc)
            await db.commit()
            return

        if extraction_data.get("parse_failed"):
            document.status = "FAILED"
            document.error_message = "Extraction response could not be parsed"
            await db.commit()
            return

        await _create_extraction_results(db, document, extraction_data)


async def _create_extraction_results(db: AsyncSession, document: Document, extraction_data: dict) -> None:
    accounts = extraction_data.get("accounts", [])

    created_results = []
    for account in accounts:
        result = ExtractionResult(
            document_id=document.id,
            extracted_institution=account["institution_name"],
            extracted_account_name=account["account_name"],
            extracted_account_last4=account["account_last4"],
            extracted_statement_date=account["statement_date"],
            extracted_balance=account["balance"],
            extracted_currency=account["currency"],
            extraction_method="AI",
            confidence_score=account["overall_confidence"],
            requires_review=account["requires_review"],
            raw_json=account,
            created_at=datetime.now(timezone.utc),
        )
        created_results.append(result)

    db.add_all(created_results)

    document.status = "REVIEW_REQUIRED" if any(a["requires_review"] for a in accounts) else "PROCESSED"
    document.processed_at = datetime.now(timezone.utc)

    await db.commit()