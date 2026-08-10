from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account


class AccountRepository:

    @staticmethod
    async def create(
        db: AsyncSession,
        account: Account,
    ) -> Account:

        db.add(account)

        await db.commit()
        await db.refresh(account)

        return account

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        account_id: UUID,
    ) -> Account | None:

        result = await db.execute(
            select(Account).where(
                Account.id == account_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user(
        db: AsyncSession,
        user_id: UUID,
        active_only: bool = False,
    ) -> list[Account]:

        query = select(Account).where(
            Account.user_id == user_id
        )

        if active_only:
            query = query.where(
                Account.is_active.is_(True)
            )

        query = query.order_by(Account.name)

        result = await db.execute(query)

        return list(result.scalars().all())

    @staticmethod
    async def delete(
        db: AsyncSession,
        account: Account,
    ) -> None:

        await db.delete(account)

        await db.commit()