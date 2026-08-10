from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SnapshotCreate(BaseModel):
    account_id: UUID

    snapshot_date: date

    balance: Decimal

    currency: str = "CAD"

    extraction_method: str = "MANUAL"

    confidence_score: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    is_verified: bool = False

    notes: str | None = None


class SnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    account_id: UUID

    snapshot_date: date

    balance: Decimal

    currency: str

    extraction_method: str

    confidence_score: Decimal | None

    is_verified: bool

    source_document_id: UUID | None

    notes: str | None

    created_at: datetime
    updated_at: datetime