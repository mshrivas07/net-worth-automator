## Properties vs. accounts — the trade-offs

**Option A: Fold real estate into `accounts` + `account_snapshots`** (drop `properties`/`property_valuations`)
- Pro: One data model for everything — net worth calc, history charts, the review pipeline, the API all "just work" for real estate with zero special-casing
- Pro: Less code — no second CRUD stack, no second valuation-history endpoint
- Con: `accounts` doesn't have address, property type (condo/detached/etc.), or a "valuation source" (e.g. "Zillow estimate" vs "appraisal") — you'd need to either add nullable columns to `accounts` that only real estate uses (schema gets messier), or drop that detail entirely
- Con: A "statement" for a house isn't a bank statement — it's a Zillow/realtor estimate, so it doesn't fit your PDF/screenshot extraction pipeline the same way; you'd likely still enter/update these values manually or via a different flow anyway

**Option B: Keep `properties` separate**
- Pro: Clean home for property-specific fields (address, valuation source, valuation date) without polluting `accounts`
- Pro: Matches reality — property valuation is fundamentally a manual/periodic estimate, not a parsed statement, so it's a genuinely different workflow from bank/broker snapshots
- Con: Net worth calculation has to union two sources (`account_snapshots` + `property_valuations`) instead of one — `NetWorthService.calculate` needs a second query and a merge
- Con: Two CRUD stacks, two "history" endpoints, two of everything

**My read:** given real estate valuation is manual/infrequent and genuinely different in kind from a parsed bank balance, I'd lean **Option B (keep separate)** — but make the net worth engine treat both as just "valued things with a date and amount" at the point where it sums up. That is: build one shared internal concept (`ValuedItem`: id, type, date, amount) that both `AccountSnapshot` and `PropertyValuation` implement, so `NetWorthService.calculate` stays a single clean query pattern even though the storage is split. Low regret either way, but B keeps the extraction pipeline scoped to what it's actually good at — parsing statements — without stretching it to cover things it'll never parse.

## Storage — recommendation

Given: CIBC/enterprise background, Azure familiarity likely, and you'll eventually need signed URLs for both web and mobile upload flows — **Azure Blob Storage** is the sensible default: same account for dev/staging/prod, native SDK support in FastAPI, and it avoids the "local filesystem won't survive a redeploy" trap while you're still early. Start with a single container (`statements/`), path convention `{user_id}/{document_id}/{original_filename}`, and store just the blob path in `documents.storage_path` (already in your schema) — never the full URL, so you can rotate storage accounts without a data migration.

If you don't already have Azure infra and want zero setup friction for local dev, local filesystem behind the same storage-path abstraction is a fine placeholder — just make sure the storage layer is an interface (`save(file) -> path`, `load(path) -> bytes`) from day one so swapping to Azure later touches one file, not every caller.

## Locking in JWT auth. Here's the buildout roadmapAuth comes first because everything downstream — documents, extraction, snapshots — needs to be scoped to a real authenticated user rather than a trusted `user_id` param anyone could pass in. Once that's in, ingestion and extraction can be built and tested against your own account with real statements instead of dummy data, and the client apps have something real to talk to from day one instead of retrofitting auth into a working UI later.

A few concrete notes on Phase 1 since it unblocks everything else:
- `User` model needs a `password_hash` column (schema migration — you're on raw SQL, not Alembic, so I'd add Alembic now while the schema is still small, rather than hand-writing more `.sql` migration files as it grows)
- JWT access + refresh token pair, short-lived access token (~15 min), refresh token stored httpOnly for web / secure storage for React Native
- A `get_current_user` FastAPI dependency replaces the `user_id: UUID` query param pattern currently used everywhere — that's a small refactor across `accounts.py`, `snapshots.py`, `net_worth.py`

Where do you want to start — should I write out the actual Phase 1 code (auth module, updated User model, Alembic setup) against your existing repo structure, or do you want the full API contract for Phase 2/3 (document upload + extraction endpoints, request/response schemas) designed first so both backend and eventual frontend work can move in parallel?

___

Good instinct — breaking this into small, scoped prompts will keep us from touching the same file twice in inconsistent ways. Here's the phase-wise prompt list, in your requested order (**Phase 3 → Phase 2 → Phase 1 → Phase 4**), with each prompt scoped tightly enough that one prompt = one clear set of files.

## Phase 3 — Extraction (finishing what's in progress)

Already done: `ExtractionService` (multi-account, OpenAI), config threshold fix, test script. Remaining:

1. **"Create the ExtractionResult model and repository"**
   → `app/models/extraction_result.py`, `app/repositories/extraction_result_repository.py`
2. **"Create extraction result schemas and the confirm endpoint"**
   → `app/schemas/extraction.py`, `app/api/v1/extraction.py`, router registration in `app/main.py`
3. **"Create the account matching service"**
   → `app/services/account_matching_service.py`

*(Note: prompt 1–2 will reference `document_id` as a foreign key even though `Document` doesn't exist as a model yet — that's fine, SQLAlchemy just needs the column, not a resolved relationship yet. We link it up properly in Phase 2.)*

## Phase 2 — Document ingestion

4. **"Create the Document model and repository"**
   → `app/models/document.py`, `app/repositories/document_repository.py`
5. **"Create the storage service for [Azure Blob / local filesystem — pick one]"**
   → `app/services/storage_service.py`, config additions in `app/config.py`
6. **"Create document schemas and the upload endpoint"**
   → `app/schemas/document.py`, `app/api/v1/documents.py`, router registration
7. **"Create the document processing orchestration service and wire it into upload"**
   → `app/services/document_processing_service.py`, edit to `app/api/v1/documents.py` (adds `BackgroundTasks` call)
8. **"Link ExtractionResult's document_id relationship now that Document exists"**
   → edits to `app/models/extraction_result.py`, `app/models/document.py` (adds `relationship()` both directions, if you want ORM-level joins instead of raw UUIDs)

## Phase 1 — Auth

9. **"Add password_hash to the User model and set up Alembic"**
   → edit `app/models/user.py`, new `alembic.ini`, `alembic/env.py`, first migration file
10. **"Create the auth module — JWT creation/verification, password hashing"**
    → `app/core/security.py` (or `app/auth/security.py`)
11. **"Create register/login endpoints and the get_current_user dependency"**
    → `app/schemas/auth.py`, `app/api/v1/auth.py`, `app/dependencies.py` (or wherever you want `get_current_user`), router registration
12. **"Refactor existing endpoints to use get_current_user instead of user_id params"**
    → edits to `app/api/v1/accounts.py`, `app/api/v1/snapshots.py`, `app/api/v1/net_worth.py`, `app/api/v1/documents.py`, `app/api/v1/extraction.py`

## Phase 4 — History, properties, clients

13. **"Create the job to populate monthly_net_worth"**
    → `app/services/net_worth_snapshot_job.py`, likely a scheduling mechanism (APScheduler or a manual trigger endpoint — we'll discuss which)
14. **"Create the properties module"** *(after we settle the accounts-vs-properties decision from earlier)*
    → `app/models/property.py`, `app/repositories/property_repository.py`, `app/schemas/property.py`, `app/api/v1/properties.py`
15. **"Scaffold the React web app"**
    → separate `frontend/` directory, own file list at that time
16. **"Scaffold the React Native mobile app"**
    → separate `mobile/` directory, own file list at that time

---

**How to use this:** paste one numbered prompt at a time (you can shorten it, e.g. just "Phase 2 — #4" or the quoted text), and I'll respond the way I did for extraction: code + an explicit **"files created/modified"** list at the end, so nothing gets lost or duplicated across prompts. If a prompt turns out to need something from a *later* numbered prompt (like #1–2 needing `Document` before they can fully compile), I'll flag that inline as a known temporary gap rather than silently working around it.

Want to start with **Phase 3, #1** (ExtractionResult model + repository) since that continues what's already in flight, or jump straight to Phase 2 since that's what unblocks testing the full flow end-to-end?