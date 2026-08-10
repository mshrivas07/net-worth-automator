from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.account import Account
from app.models.snapshot import AccountSnapshot
from app.repositories.snapshot_repository import SnapshotRepository
from app.schemas.snapshot import (
    SnapshotCreate,
    SnapshotResponse,
)


router = APIRouter(
    prefix="/snapshots",
    tags=["Snapshots"],
)


@router.post(
    "",
    response_model=SnapshotResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_snapshot(
    request: SnapshotCreate,
    db: AsyncSession = Depends(get_db),
):

    account = await db.get(
        Account,
        request.account_id,
    )

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found",
        )

    existing = await SnapshotRepository.get_for_account_and_date(
        db,
        request.account_id,
        request.snapshot_date,
    )

    if existing:

        existing.balance = request.balance
        existing.currency = request.currency
        existing.extraction_method = request.extraction_method
        existing.confidence_score = request.confidence_score
        existing.is_verified = request.is_verified
        existing.notes = request.notes
        existing.updated_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(existing)

        return existing

    snapshot = AccountSnapshot(
        account_id=request.account_id,
        snapshot_date=request.snapshot_date,
        balance=request.balance,
        currency=request.currency,
        extraction_method=request.extraction_method,
        confidence_score=request.confidence_score,
        is_verified=request.is_verified,
        notes=request.notes,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    return await SnapshotRepository.create(
        db,
        snapshot,
    )


@router.get(
    "/latest/{account_id}",
    response_model=SnapshotResponse | None,
)
async def get_latest_snapshot(
    account_id: UUID,
    db: AsyncSession = Depends(get_db),
):

    return await SnapshotRepository.get_latest_for_account(
        db,
        account_id,
    )