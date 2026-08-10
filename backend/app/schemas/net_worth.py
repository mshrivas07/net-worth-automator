from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class NetWorthResponse(BaseModel):
    user_id: UUID

    snapshot_month: date

    total_assets: Decimal

    total_liabilities: Decimal

    net_worth: Decimal

    asset_account_count: int

    liability_account_count: int


class NetWorthHistoryItem(BaseModel):
    snapshot_month: date

    total_assets: Decimal

    total_liabilities: Decimal

    net_worth: Decimal