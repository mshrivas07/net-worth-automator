# app/services/extraction_service.py
import base64
import json
from decimal import Decimal

from openai import OpenAI

from app.config import settings


EXTRACTION_SYSTEM_PROMPT = """You are extracting structured account balance data from a financial document. This could be:
(a) a single statement for one account (PDF or screenshot), or
(b) a bank/broker dashboard screenshot showing MULTIPLE accounts grouped under section headers (e.g. "Banking", "Credit Cards", "Loans and Mortgages", "Investments").

Extract ONE entry per INDIVIDUAL ACCOUNT LINE ITEM — never a section subtotal or grand total row. For example, if you see:
  Banking                                    $7.72       <- SKIP this, it's a section subtotal
  TD MINIMUM CHEQUING ACCOUNT ****3204        $7.22       <- EXTRACT this
  TD EVERY DAY SAVINGS ACCOUNT ****9075       $0.50       <- EXTRACT this
extract only the two individual account rows, not the "$7.72" Banking subtotal.

For each account, classify:
- account_type: one of CHEQUING, SAVINGS, CREDIT_CARD, MORTGAGE, HELOC, LOAN, TFSA, RRSP, RESP, FHSA, INVESTMENT, OTHER
- classification: "ASSET" or "LIABILITY" — chequing/savings/TFSA/RRSP/investments are ASSET; credit cards/mortgages/HELOC/loans are LIABILITY

Rules:
- Report every balance as a POSITIVE number. classification (not sign) indicates whether it's owed or owned.
- If a statement/as-of date is visible for the whole document, use it for every account. If this is a live dashboard screenshot with no explicit date shown, set statement_date to null — do not guess today's date.
- account_last4 is the last 4 digits only, even if the display shows a longer masked number (e.g. "**** **** 6200" → "6200").
- All confidence scores are floats from 0.0 to 1.0 (not 0-100, not percentages).
- If a value is unclear, cut off, or you are guessing, reflect that with a LOW confidence score rather than omitting the field.
- Never fabricate a value you cannot see in the document."""

EXTRACTION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "document_kind": {
            "type": "string",
            "enum": ["single_account_statement", "multi_account_summary"],
        },
        "accounts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "institution_name": {"type": ["string", "null"]},
                    "account_name": {"type": ["string", "null"]},
                    "account_last4": {"type": ["string", "null"]},
                    "account_type": {
                        "type": ["string", "null"],
                        "enum": [
                            "CHEQUING", "SAVINGS", "CREDIT_CARD", "MORTGAGE", "HELOC",
                            "LOAN", "TFSA", "RRSP", "RESP", "FHSA", "INVESTMENT", "OTHER", None,
                        ],
                    },
                    "classification": {
                        "type": ["string", "null"],
                        "enum": ["ASSET", "LIABILITY", None],
                    },
                    "statement_date": {"type": ["string", "null"], "description": "YYYY-MM-DD"},
                    "balance": {"type": ["number", "null"]},
                    "currency": {
                        "type": ["string", "null"],
                        "enum": ["CAD", "USD", "EUR", "GBP", "INR", "OTHER", None],
                    },
                    "confidence": {
                        "type": "object",
                        "properties": {
                            "institution_name": {"type": "number"},
                            "account_last4": {"type": "number"},
                            "statement_date": {"type": "number"},
                            "balance": {"type": "number"},
                        },
                        "required": ["institution_name", "account_last4", "statement_date", "balance"],
                        "additionalProperties": False,
                    },
                    "notes": {"type": ["string", "null"]},
                },
                "required": [
                    "institution_name", "account_name", "account_last4", "account_type",
                    "classification", "statement_date", "balance", "currency",
                    "confidence", "notes",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": ["document_kind", "accounts"],
    "additionalProperties": False,
}


class ExtractionService:

    def __init__(self):
        self._client = OpenAI(api_key=settings.openai_api_key)

    async def extract(self, file_bytes: bytes, mime_type: str) -> dict:
        b64 = base64.b64encode(file_bytes).decode("utf-8")

        if mime_type == "application/pdf":
            file_block = {
                "type": "input_file",
                "filename": "statement.pdf",
                "file_data": f"data:application/pdf;base64,{b64}",
            }
        else:
            file_block = {
                "type": "input_image",
                "image_url": f"data:{mime_type};base64,{b64}",
            }

        response = self._client.responses.create(
            model="gpt-4o",
            input=[
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        file_block,
                        {"type": "input_text", "text": "Extract every individual account as specified."},
                    ],
                },
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "extraction_result",
                    "schema": EXTRACTION_JSON_SCHEMA,
                    "strict": True,
                }
            },
        )

        return self._parse(response.output_text)

    def _parse(self, raw_text: str) -> dict:
        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            return {
                "parse_failed": True,
                "raw_text": raw_text,
                "document_kind": None,
                "accounts": [],
            }

        for account in data.get("accounts", []):
            overall_confidence = self._overall_confidence(account.get("confidence", {}))
            account["overall_confidence"] = overall_confidence
            account["requires_review"] = overall_confidence < settings.extraction_auto_accept_threshold

        return data

    @staticmethod
    def _overall_confidence(field_confidences: dict) -> Decimal:
        # balance and statement_date matter most for net worth accuracy —
        # weight them heavier than fields used only for account matching.
        weights = {"balance": 0.4, "statement_date": 0.3, "account_last4": 0.2, "institution_name": 0.1}
        total = Decimal("0")
        for field, weight in weights.items():
            score = field_confidences.get(field) or 0
            total += Decimal(str(score)) * Decimal(str(weight))
        return total.quantize(Decimal("0.01"))