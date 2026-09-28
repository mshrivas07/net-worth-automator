# app/services/storage_service.py
import hashlib
import uuid
from pathlib import Path

from app.config import settings


class StorageService:
    """
    Local-filesystem storage backend. Files are laid out as:
        {storage_root}/{user_id}/{document_id}/{original_filename}

    storage_path saved on the Document model is always RELATIVE to
    storage_root (e.g. "3f2a.../7c1b.../statement.pdf") — never an
    absolute path. This is what lets a future Azure Blob swap only
    change this file: relative path in the DB works identically as
    a blob key.
    """

    @staticmethod
    def _root() -> Path:
        root = Path(settings.storage_root)
        root.mkdir(parents=True, exist_ok=True)
        return root

    @staticmethod
    def hash_bytes(file_bytes: bytes) -> str:
        return hashlib.sha256(file_bytes).hexdigest()

    @classmethod
    async def save(cls, user_id: uuid.UUID, document_id: uuid.UUID, filename: str, file_bytes: bytes) -> str:
        """
        Writes file_bytes to disk and returns the relative storage_path
        to persist on the Document row.
        """
        safe_filename = Path(filename).name  # strips any path traversal attempt
        relative_dir = Path(str(user_id)) / str(document_id)
        full_dir = cls._root() / relative_dir
        full_dir.mkdir(parents=True, exist_ok=True)

        full_path = full_dir / safe_filename
        full_path.write_bytes(file_bytes)

        return str(relative_dir / safe_filename)

    @classmethod
    async def load(cls, storage_path: str) -> bytes:
        full_path = cls._root() / storage_path
        if not full_path.is_file():
            raise FileNotFoundError(f"Document not found at storage_path: {storage_path}")
        return full_path.read_bytes()

    @classmethod
    async def delete(cls, storage_path: str) -> None:
        full_path = cls._root() / storage_path
        full_path.unlink(missing_ok=True)