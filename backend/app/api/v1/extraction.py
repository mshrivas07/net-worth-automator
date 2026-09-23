# app/api/v1/extraction.py
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.extraction import ExtractionResultResponse, ExtractionConfirm
from app.repositories.extraction_repository import ExtractionRepository
from app.repositories.account_repository import AccountRepository
from app.repositories.snapshot_repository import SnapshotRepository
from app.models.snapshot import AccountSnapshot
from datetime import datetime, timezone

router = APIRouter(prefix="/extraction-results", tags=["Extraction"])


@router.get("/{extraction_id}", response_model=ExtractionResultResponse)
async def get_extraction_result(extraction_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await ExtractionRepository.get_by_id(db, extraction_id)
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
    User has reviewed (and possibly corrected) the extracted fields.
    Writes the confirmed values into account_snapshots.
    """
    extraction = await ExtractionRepository.get_by_id(db, extraction_id)
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
        is_verified=True,  # user just confirmed it
        source_document_id=extraction.document_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    await SnapshotRepository.create(db, snapshot)

    extraction.account_id = request.account_id
    await db.commit()

    return extraction