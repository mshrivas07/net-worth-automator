# app/repositories/document_repository.py
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from sqlalchemy.orm import selectinload

class DocumentRepository:

    @staticmethod
    async def create(db: AsyncSession, document: Document) -> Document:
        db.add(document)
        await db.commit()
        await db.refresh(document)
        return document

    @staticmethod
    async def get_by_id(db: AsyncSession, document_id: UUID) -> Document | None:
        query = select(Document).where(Document.id == document_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_hash(db: AsyncSession, user_id: UUID, file_hash: str) -> Document | None:
        """
        Used at upload time to detect duplicate re-uploads of the same
        file before spending an extraction call on it.
        """
        query = select(Document).where(
            Document.user_id == user_id,
            Document.file_hash == file_hash,
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_user(
        db: AsyncSession, user_id: UUID, status: str | None = None
    ) -> list[Document]:
        query = select(Document).where(Document.user_id == user_id)
        if status is not None:
            query = query.where(Document.status == status)
        query = query.order_by(Document.uploaded_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_status(
        db: AsyncSession,
        document: Document,
        status: str,
        error_message: str | None = None,
    ) -> Document:
        document.status = status
        if error_message is not None:
            document.error_message = error_message
        await db.commit()
        await db.refresh(document)
        return document

    @staticmethod
    async def get_with_extraction_results(db: AsyncSession, document_id: UUID) -> Document | None:
        """
        Loads a document and all of its extraction results in one
        round trip (two queries, via selectinload). Use this whenever
        you need document.extraction_results, since lazy loading is
        disabled on that relationship.
        """
        query = (
            select(Document)
            .where(Document.id == document_id)
            .options(selectinload(Document.extraction_results))
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()