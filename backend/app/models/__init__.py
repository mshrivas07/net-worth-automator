# app/models/__init__.py
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import models AFTER Base is defined. This registers every model with
# Base.metadata / the declarative registry, which string-based
# relationship() references (e.g. relationship("Document")) depend on.
from app.models.document import Document  # noqa: E402,F401
from app.models.extraction_result import ExtractionResult  # noqa: E402,F401