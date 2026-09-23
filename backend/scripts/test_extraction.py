# scripts/test_extraction.py
import asyncio
import sys

from app.services.extraction_service import ExtractionService


async def main(file_path: str):
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    mime_type = "application/pdf" if file_path.endswith(".pdf") else "image/png"

    service = ExtractionService()
    result = await service.extract(file_bytes, mime_type)

    print(f"document_kind: {result.get('document_kind')}")
    print(f"accounts found: {len(result.get('accounts', []))}\n")

    for i, acc in enumerate(result.get("accounts", []), 1):
        print(f"[{i}] {acc['institution_name']} - {acc['account_name']} (****{acc['account_last4']})")
        print(f"    type={acc['account_type']}  classification={acc['classification']}")
        print(f"    balance={acc['balance']} {acc['currency']}  review_needed={acc['requires_review']}")
        print(f"    overall_confidence={acc['overall_confidence']}\n")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))