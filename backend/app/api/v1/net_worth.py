from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.net_worth import MonthlyNetWorth
from app.schemas.net_worth import (
    NetWorthHistoryItem,
    NetWorthResponse,
)
from app.services.net_worth_service import NetWorthService


router = APIRouter(
    prefix="/net-worth",
    tags=["Net Worth"],
)


@router.get(
    "/current",
    response_model=NetWorthResponse,
)
async def get_current_net_worth(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):

    result = await NetWorthService.calculate_latest(
        db,
        user_id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="No account snapshots found",
        )

    return result


@router.get(
    "/{snapshot_date}",
    response_model=NetWorthResponse,
)
async def get_net_worth(
    snapshot_date: date,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):

    result = await NetWorthService.calculate(
        db,
        user_id,
        snapshot_date,
    )

    return result


@router.get(
    "/history/all",
    response_model=list[NetWorthHistoryItem],
)
async def get_net_worth_history(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(MonthlyNetWorth)
        .where(
            MonthlyNetWorth.user_id == user_id
        )
        .order_by(
            MonthlyNetWorth.snapshot_month
        )
    )

    return list(result.scalars().all())