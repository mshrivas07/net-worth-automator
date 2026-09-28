# app/services/document_processing_service.py
import json
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

from app.database import AsyncSessionLocal
from app.models.document import Document
from app.models.extraction_result import ExtractionResult
from app.repositories.document_repository import DocumentRepository
from app.repositories.extraction_result_repository import ExtractionResultRepository
from app.services.extraction_service import ExtractionService
from app.services.storage_service import StorageService


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _to_decimal(value) -> Decimal | None:
    return None if value is None else Decimal(str(value))


def _json_safe(value: dict) -> dict:
    # Converts Decimal (and anything else json can't handle) to strings
    # so the dict can be stored in a JSONB column.
    return json.loads(json.dumps(value, default=str))


async def run_extraction(document_id: UUID) -> None:
    """
    Background task entrypoint. Guarantees the document always ends in a
    terminal status (PROCESSED, REVIEW_REQUIRED or FAILED), never stuck
    in PROCESSING, no matter where the pipeline breaks.
    """
    async with AsyncSessionLocal() as db:
        document = await DocumentRepository.get_by_id(db, document_id)
        if document is None:
            return

        await DocumentRepository.update_status(db, document, status="PROCESSING")

        try:
            await _process(db, document)
        except Exception as exc:
            await db.rollback()
            # After a rollback the old instance is expired, so re-fetch it
            # before updating the status.
            document = await DocumentRepository.get_by_id(db, document_id)
            if document is not None:
                await DocumentRepository.update_status(
                    db,
                    document,
                    status="FAILED",
                    error_message=f"{type(exc).__name__}: {exc}"[:2000],
                )


async def _process(db, document: Document) -> None:
    file_bytes = await StorageService.load(document.storage_path)
    extraction_data = await ExtractionService().extract(file_bytes, document.mime_type)

    if extraction_data.get("parse_failed"):
        raise ValueError("Extraction response could not be parsed as JSON")

    accounts = extraction_data.get("accounts", [])
    if not accounts:
        raise ValueError("No accounts were extracted from this document")

    extraction_results = [
        ExtractionResult(
            document_id=document.id,
            extracted_institution=account["institution_name"],
            extracted_account_name=account["account_name"],
            extracted_account_last4=account["account_last4"],
            extracted_statement_date=_parse_date(account["statement_date"]),
            extracted_balance=_to_decimal(account["balance"]),
            extracted_currency=account["currency"],
            extraction_method="AI",
            confidence_score=account["overall_confidence"],
            raw_json=_json_safe(account),
            requires_review=account["requires_review"],
            created_at=datetime.now(timezone.utc),
        )
        for account in accounts
    ]
    await ExtractionResultRepository.create_many(db, extraction_results)

    final_status = "REVIEW_REQUIRED" if any(a["requires_review"] for a in accounts) else "PROCESSED"
    document.processed_at = datetime.now(timezone.utc)
    await DocumentRepository.update_status(db, document, status=final_status)