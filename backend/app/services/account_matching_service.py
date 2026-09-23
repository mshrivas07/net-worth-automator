# app/services/account_matching_service.py
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account


class AccountMatchingService:

    @staticmethod
    async def suggest_match(
        db: AsyncSession,
        user_id: UUID,
        extracted_last4: str | None,
        extracted_institution: str | None,
    ) -> Account | None:
        if not extracted_last4:
            return None

        query = select(Account).where(
            Account.user_id == user_id,
            Account.account_number_last4 == extracted_last4,
            Account.is_active.is_(True),
        )
        result = await db.execute(query)
        candidates = list(result.scalars().all())

        if len(candidates) == 1:
            return candidates[0]
        # Multiple accounts share last4 (rare but possible across institutions) —
        # don't guess, let the user pick in the review UI.
        return None