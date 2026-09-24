# app/api/v1/extraction.py
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.snapshot import AccountSnapshot
from app.repositories.account_repository import AccountRepository
from app.repositories.extraction_result_repository import ExtractionResultRepository
from app.repositories.snapshot_repository import SnapshotRepository
from app.schemas.extraction import (
    ExtractionConfirm,
    ExtractionResultListResponse,
    ExtractionResultResponse,
)

router = APIRouter(prefix="/extraction-results", tags=["Extraction"])


@router.get("/document/{document_id}", response_model=ExtractionResultListResponse)
async def list_extraction_results_for_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Returns every extracted account for a document (a single-statement
    upload will have one row; a multi-account dashboard screenshot will
    have several) — this is what the review UI renders as a list.
    """
    results = await ExtractionResultRepository.list_by_document_id(db, document_id)
    return ExtractionResultListResponse(document_id=document_id, results=results)


@router.get("/{extraction_id}", response_model=ExtractionResultResponse)
async def get_extraction_result(extraction_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await ExtractionResultRepository.get_by_id(db, extraction_id)
    if result is None:
        raise HTTPException(404, "Extraction result not found")
    return result


@router.post("/{extraction_id}/confirm", response_model=ExtractionResultResponse)
async def confirm_extraction(
    extraction_id: UUID,
    request: ExtractionConfirm,
    db: AsyncSession = Depends(get_db),
):
    """
    User has reviewed (and possibly corrected) one extracted account.
    Writes a verified AccountSnapshot and links this extraction to the
    chosen account. Does NOT touch any other extraction rows from the
    same document — the review UI calls this once per confirmed account.
    """
    extraction = await ExtractionResultRepository.get_by_id(db, extraction_id)
    if extraction is None:
        raise HTTPException(404, "Extraction result not found")

    account = await AccountRepository.get_by_id(db, request.account_id)
    if account is None:
        raise HTTPException(404, "Account not found")

    snapshot = AccountSnapshot(
        account_id=request.account_id,
        snapshot_date=request.snapshot_date,
        balance=request.balance,
        currency=request.currency,
        extraction_method=extraction.extraction_method,
        confidence_score=extraction.confidence_score,
        is_verified=True,
        source_document_id=extraction.document_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    await SnapshotRepository.create(db, snapshot)

    await ExtractionResultRepository.assign_account(db, extraction, request.account_id)

    return extraction


@router.delete("/{extraction_id}", status_code=204)
async def dismiss_extraction(extraction_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    User reviewed this row and decided it's not worth keeping (e.g. a
    duplicate, a misread section subtotal, an account they don't track).
    Does not delete AccountSnapshot rows already created from a prior
    confirm — only relevant for un-confirmed rows.
    """
    extraction = await ExtractionResultRepository.get_by_id(db, extraction_id)
    if extraction is None:
        raise HTTPException(404, "Extraction result not found")
    if extraction.account_id is not None:
        raise HTTPException(400, "Cannot dismiss an extraction that has already been confirmed")

    await ExtractionResultRepository.delete(db, extraction)