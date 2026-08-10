from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.account import Account
from app.repositories.account_repository import AccountRepository
from app.schemas.account import (
    AccountCreate,
    AccountResponse,
    AccountUpdate,
)


router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"],
)


@router.post(
    "",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_account(
    request: AccountCreate,
    db: AsyncSession = Depends(get_db),
):

    account = Account(
        user_id=request.user_id,
        institution_id=request.institution_id,
        name=request.name,
        account_type=request.account_type,
        classification=request.classification,
        account_number_last4=request.account_number_last4,
        currency=request.currency,
        description=request.description,
        include_in_net_worth=request.include_in_net_worth,
        expected_statement=request.expected_statement,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    return await AccountRepository.create(
        db,
        account,
    )


@router.get(
    "",
    response_model=list[AccountResponse],
)
async def get_accounts(
    user_id: UUID,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
):

    return await AccountRepository.get_by_user(
        db,
        user_id,
        active_only,
    )


@router.get(
    "/{account_id}",
    response_model=AccountResponse,
)
async def get_account(
    account_id: UUID,
    db: AsyncSession = Depends(get_db),
):

    account = await AccountRepository.get_by_id(
        db,
        account_id,
    )

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found",
        )

    return account


@router.put(
    "/{account_id}",
    response_model=AccountResponse,
)
async def update_account(
    account_id: UUID,
    request: AccountUpdate,
    db: AsyncSession = Depends(get_db),
):

    account = await AccountRepository.get_by_id(
        db,
        account_id,
    )

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found",
        )

    updates = request.model_dump(
        exclude_unset=True
    )

    for field, value in updates.items():
        setattr(account, field, value)

    account.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(account)

    return account


@router.delete(
    "/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_account(
    account_id: UUID,
    db: AsyncSession = Depends(get_db),
):

    account = await AccountRepository.get_by_id(
        db,
        account_id,
    )

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found",
        )

    await AccountRepository.delete(
        db,
        account,
    )