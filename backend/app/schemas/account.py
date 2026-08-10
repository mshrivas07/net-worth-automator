from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):
    user_id: UUID
    institution_id: UUID | None = None

    name: str = Field(min_length=1, max_length=200)

    account_type: str
    classification: str

    account_number_last4: str | None = Field(
        default=None,
        min_length=4,
        max_length=4,
    )

    currency: str = "CAD"

    description: str | None = None

    include_in_net_worth: bool = True
    expected_statement: bool = True


class AccountUpdate(BaseModel):
    institution_id: UUID | None = None
    name: str | None = None
    account_type: str | None = None
    classification: str | None = None
    description: str | None = None
    include_in_net_worth: bool | None = None
    expected_statement: bool | None = None
    is_active: bool | None = None


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    institution_id: UUID | None

    name: str
    account_type: str
    classification: str

    account_number_last4: str | None

    currency: str

    description: str | None

    is_active: bool
    include_in_net_worth: bool
    expected_statement: bool

    created_at: datetime
    updated_at: datetime