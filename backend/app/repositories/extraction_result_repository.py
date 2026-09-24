# app/repositories/extraction_result_repository.py
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.extraction_result import ExtractionResult


class ExtractionResultRepository:

    @staticmethod
    async def create(db: AsyncSession, extraction_result: ExtractionResult) -> ExtractionResult:
        db.add(extraction_result)
        await db.commit()
        await db.refresh(extraction_result)
        return extraction_result

    @staticmethod
    async def create_many(
        db: AsyncSession, extraction_results: list[ExtractionResult]
    ) -> list[ExtractionResult]:
        db.add_all(extraction_results)
        await db.commit()
        for result in extraction_results:
            await db.refresh(result)
        return extraction_results

    @staticmethod
    async def get_by_id(db: AsyncSession, extraction_id: UUID) -> ExtractionResult | None:
        query = select(ExtractionResult).where(ExtractionResult.id == extraction_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_document_id(db: AsyncSession, document_id: UUID) -> list[ExtractionResult]:
        query = (
            select(ExtractionResult)
            .where(ExtractionResult.document_id == document_id)
            .order_by(ExtractionResult.created_at)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def list_pending_review(db: AsyncSession, document_id: UUID) -> list[ExtractionResult]:
        query = select(ExtractionResult).where(
            ExtractionResult.document_id == document_id,
            ExtractionResult.requires_review.is_(True),
            ExtractionResult.account_id.is_(None),
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def assign_account(
        db: AsyncSession, extraction_result: ExtractionResult, account_id: UUID
    ) -> ExtractionResult:
        extraction_result.account_id = account_id
        await db.commit()
        await db.refresh(extraction_result)
        return extraction_result

    @staticmethod
    async def delete(db: AsyncSession, extraction_result: ExtractionResult) -> None:
        await db.delete(extraction_result)
        await db.commit()