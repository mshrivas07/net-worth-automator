import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Integer,
    Numeric,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class MonthlyNetWorth(Base):
    __tablename__ = "monthly_net_worth"
    __table_args__ = {"schema": "networth"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    snapshot_month: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    total_assets: Mapped[Decimal] = mapped_column(
        Numeric(19, 4),
        default=0,
    )

    total_liabilities: Mapped[Decimal] = mapped_column(
        Numeric(19, 4),
        default=0,
    )

    net_worth: Mapped[Decimal] = mapped_column(
        Numeric(19, 4),
        default=0,
    )

    asset_account_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    liability_account_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    is_finalized: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )