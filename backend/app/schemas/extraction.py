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


class ExtractionConfirm(BaseModel):
    account_id: UUID          # user-selected or user-confirmed account
    snapshot_date: date       # editable — defaults to extracted_statement_date, user can correct
    balance: Decimal          # editable — defaults to extracted_balance, user can correct
    currency: str = "CAD"