# app/api/v1/documents.py
from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.document_processing_service import run_extraction
# ... your existing DocumentRepository, StorageService imports

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("", response_model=DocumentResponse, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),  # from your Phase 1 auth
):
    document = await DocumentRepository.create(db, user_id=current_user.id, file=file, ...)
    background_tasks.add_task(run_extraction, document.id)
    return document