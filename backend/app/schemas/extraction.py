# app/schemas/extraction.py
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ExtractionResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    account_id: UUID | None

    extracted_institution: str | None
    extracted_account_name: str | None
    extracted_account_last4: str | None
    extracted_statement_date: date | None
    extracted_balance: Decimal | None
    extracted_currency: str | None

    extraction_method: str
    confidence_score: Decimal | None
    requires_review: bool

    created_at: datetime


class ExtractionResultListResponse(BaseModel):
    document_id: UUID
    results: list[ExtractionResultResponse]


class ExtractionConfirm(BaseModel):
    """
    Submitted by the review UI. Pre-filled with extracted values but the
    user may have corrected any field before submitting — whatever is
    sent here is treated as final and written to AccountSnapshot as-is.
    """
    account_id: UUID
    snapshot_date: date
    balance: Decimal
    currency: str = "CAD"