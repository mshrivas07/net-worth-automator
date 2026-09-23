# app/models/extraction_result.py
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, Enum, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


extraction_method_enum = Enum(
    "MANUAL", "PDF_TEXT", "OCR", "AI",
    name="extraction_method", schema="networth", create_type=False,
)

currency_enum = Enum(
    "CAD", "USD", "EUR", "GBP", "INR", "OTHER",
    name="currency_code", schema="networth", create_type=False,
)


class ExtractionResult(Base):
    __tablename__ = "extraction_results"
    __table_args__ = {"schema": "networth"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    account_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))

    extracted_institution: Mapped[str | None] = mapped_column(String(200))
    extracted_account_name: Mapped[str | None] = mapped_column(String(300))
    extracted_account_last4: Mapped[str | None] = mapped_column(String(4))
    extracted_statement_date: Mapped[date | None] = mapped_column(Date)
    extracted_balance: Mapped[Decimal | None] = mapped_column(Numeric(19, 4))
    extracted_currency: Mapped[str | None] = mapped_column(currency_enum)

    extraction_method: Mapped[str] = mapped_column(extraction_method_enum, nullable=False)
    confidence_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))

    raw_text: Mapped[str | None] = mapped_column(Text)
    raw_json: Mapped[dict | None] = mapped_column(JSONB)

    requires_review: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))