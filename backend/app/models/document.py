# app/models/document.py
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING
from sqlalchemy import BigInteger, Date, DateTime, Enum, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models.extraction_result import ExtractionResult

document_type_enum = Enum(
    "BANK_STATEMENT", "CREDIT_CARD_STATEMENT", "INVESTMENT_STATEMENT",
    "MORTGAGE_STATEMENT", "HELOC_STATEMENT", "SCREENSHOT", "OTHER",
    name="document_type", schema="networth", create_type=False,
)

document_status_enum = Enum(
    "UPLOADED", "PROCESSING", "PROCESSED", "REVIEW_REQUIRED", "FAILED",
    name="document_status", schema="networth", create_type=False,
)


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = {"schema": "networth"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    document_type: Mapped[str] = mapped_column(document_type_enum, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    storage_path: Mapped[str | None] = mapped_column(String(1000))
    file_hash: Mapped[str | None] = mapped_column(String(128))
    mime_type: Mapped[str | None] = mapped_column(String(100))
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger)

    statement_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(document_status_enum, default="UPLOADED")

    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)
    extraction_results: Mapped[list["ExtractionResult"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="raise",
        order_by="ExtractionResult.created_at",
    )