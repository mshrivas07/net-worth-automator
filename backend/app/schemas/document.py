# app/schemas/document.py
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    document_type: str
    original_filename: str
    mime_type: str | None
    file_size_bytes: int | None
    statement_date: date | None
    status: str
    uploaded_at: datetime
    processed_at: datetime | None
    error_message: str | None


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]