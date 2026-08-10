from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.snapshot import AccountSnapshot


class SnapshotRepository:

    @staticmethod
    async def create(
        db: AsyncSession,
        snapshot: AccountSnapshot,
    ) -> AccountSnapshot:

        db.add(snapshot)

        await db.commit()
        await db.refresh(snapshot)

        return snapshot

    @staticmethod
    async def get_for_account_and_date(
        db: AsyncSession,
        account_id,
        snapshot_date: date,
    ) -> AccountSnapshot | None:

        result = await db.execute(
            select(AccountSnapshot)
            .where(
                AccountSnapshot.account_id == account_id,
                AccountSnapshot.snapshot_date == snapshot_date,
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_latest_for_account(
        db: AsyncSession,
        account_id,
    ) -> AccountSnapshot | None:

        result = await db.execute(
            select(AccountSnapshot)
            .where(
                AccountSnapshot.account_id == account_id
            )
            .order_by(
                AccountSnapshot.snapshot_date.desc()
            )
            .limit(1)
        )

        return result.scalar_one_or_none()