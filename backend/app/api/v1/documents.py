# app/api/v1/documents.py
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentListResponse, DocumentResponse
from app.services.storage_service import StorageService
from app.services.document_processing_service import run_extraction

router = APIRouter(prefix="/documents", tags=["Documents"])

# TODO(Phase 1 #12): replace user_id param with Depends(get_current_user) everywhere in this file.

ALLOWED_MIME_TYPES = {"application/pdf", "image/png", "image/jpeg", "image/jpg"}
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB


@router.post("", response_model=DocumentResponse, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    user_id: UUID = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            400,
            f"Unsupported file type: {file.content_type}. Allowed: {', '.join(sorted(ALLOWED_MIME_TYPES))}",
        )

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(400, f"File exceeds max size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB")
    if len(file_bytes) == 0:
        raise HTTPException(400, "Uploaded file is empty")

    file_hash = StorageService.hash_bytes(file_bytes)

    existing = await DocumentRepository.get_by_hash(db, user_id, file_hash)
    if existing is not None:
        raise HTTPException(
            409,
            f"This exact file was already uploaded as document {existing.id} "
            f"(status: {existing.status}). Re-upload only if this is intentional.",
        )

    document_id = uuid4()
    storage_path = await StorageService.save(
        user_id=user_id,
        document_id=document_id,
        filename=file.filename or "upload",
        file_bytes=file_bytes,
    )

    document = Document(
        id=document_id,
        user_id=user_id,
        document_type=document_type,
        original_filename=file.filename or "upload",
        storage_path=storage_path,
        file_hash=file_hash,
        mime_type=file.content_type,
        file_size_bytes=len(file_bytes),
        status="UPLOADED",
        uploaded_at=datetime.now(timezone.utc),
    )
    document = await DocumentRepository.create(db, document)

    background_tasks.add_task(run_extraction, document.id)

    return document


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: UUID, db: AsyncSession = Depends(get_db)):
    document = await DocumentRepository.get_by_id(db, document_id)
    if document is None:
        raise HTTPException(404, "Document not found")
    return document


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    user_id: UUID,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    documents = await DocumentRepository.list_by_user(db, user_id, status=status)
    return DocumentListResponse(documents=documents)