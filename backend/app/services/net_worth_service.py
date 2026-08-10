from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.snapshot import AccountSnapshot


class NetWorthService:

    @staticmethod
    async def calculate(
        db: AsyncSession,
        user_id: UUID,
        snapshot_date: date,
    ):

        result = await db.execute(
            select(Account, AccountSnapshot)
            .join(
                AccountSnapshot,
                AccountSnapshot.account_id == Account.id,
            )
            .where(
                Account.user_id == user_id,
                Account.include_in_net_worth.is_(True),
                Account.is_active.is_(True),
                AccountSnapshot.snapshot_date == snapshot_date,
            )
        )

        rows = result.all()

        total_assets = Decimal("0")
        total_liabilities = Decimal("0")

        asset_count = 0
        liability_count = 0

        for account, snapshot in rows:

            balance = snapshot.balance

            if account.classification == "ASSET":
                total_assets += balance
                asset_count += 1

            elif account.classification == "LIABILITY":
                total_liabilities += balance
                liability_count += 1

        net_worth = total_assets - total_liabilities

        return {
            "user_id": user_id,
            "snapshot_month": snapshot_date,
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "net_worth": net_worth,
            "asset_account_count": asset_count,
            "liability_account_count": liability_count,
        }

    @staticmethod
    async def calculate_latest(
        db: AsyncSession,
        user_id: UUID,
    ):

        result = await db.execute(
            select(AccountSnapshot.snapshot_date)
            .join(
                Account,
                Account.id == AccountSnapshot.account_id,
            )
            .where(
                Account.user_id == user_id,
                Account.include_in_net_worth.is_(True),
            )
            .order_by(
                AccountSnapshot.snapshot_date.desc()
            )
            .limit(1)
        )

        latest_date = result.scalar_one_or_none()

        if latest_date is None:
            return None

        return await NetWorthService.calculate(
            db,
            user_id,
            latest_date,
        )