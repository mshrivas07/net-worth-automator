import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    Numeric,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


extraction_method_enum = Enum(
    "MANUAL",
    "PDF_TEXT",
    "OCR",
    "AI",
    name="extraction_method",
    schema="networth",
    create_type=False,
)

currency_enum = Enum(
    "CAD",
    "USD",
    "EUR",
    "GBP",
    "INR",
    "OTHER",
    name="currency_code",
    schema="networth",
    create_type=False,
)


class AccountSnapshot(Base):
    __tablename__ = "account_snapshots"
    __table_args__ = {"schema": "networth"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    snapshot_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    balance: Mapped[Decimal] = mapped_column(
        Numeric(19, 4),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        currency_enum,
        default="CAD",
    )

    extraction_method: Mapped[str] = mapped_column(
        extraction_method_enum,
        default="MANUAL",
    )

    confidence_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2)
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    source_document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True)
    )

    notes: Mapped[str | None] = mapped_column(
        Text
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )