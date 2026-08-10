import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


account_type_enum = Enum(
    "CHEQUING",
    "SAVINGS",
    "CASH",
    "TFSA",
    "RRSP",
    "RESP",
    "FHSA",
    "INVESTMENT",
    "BROKERAGE",
    "REAL_ESTATE",
    "VEHICLE",
    "OTHER_ASSET",
    "CREDIT_CARD",
    "MORTGAGE",
    "HELOC",
    "LOAN",
    "OTHER_LIABILITY",
    name="account_type",
    schema="networth",
    create_type=False,
)

classification_enum = Enum(
    "ASSET",
    "LIABILITY",
    name="account_classification",
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


class Account(Base):
    __tablename__ = "accounts"
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

    institution_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True)
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    account_type: Mapped[str] = mapped_column(
        account_type_enum,
        nullable=False,
    )

    classification: Mapped[str] = mapped_column(
        classification_enum,
        nullable=False,
    )

    account_number_last4: Mapped[str | None] = mapped_column(
        String(4)
    )

    currency: Mapped[str] = mapped_column(
        currency_enum,
        default="CAD",
    )

    description: Mapped[str | None] = mapped_column()

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    include_in_net_worth: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    expected_statement: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )