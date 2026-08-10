-- ============================================================
-- NET WORTH AUTOMATOR
-- PostgreSQL Initial Database Schema
-- ============================================================
CREATE EXTENSION IF NOT EXISTS pgcrypto;
BEGIN;

-- ============================================================
-- SCHEMA
-- ============================================================

CREATE SCHEMA IF NOT EXISTS networth;

SET search_path TO networth, public;


-- ============================================================
-- ENUM TYPES
-- ============================================================

CREATE TYPE account_classification AS ENUM (
    'ASSET',
    'LIABILITY'
);

CREATE TYPE account_type AS ENUM (
    'CHEQUING',
    'SAVINGS',
    'CASH',
    'TFSA',
    'RRSP',
    'RESP',
    'FHSA',
    'INVESTMENT',
    'BROKERAGE',
    'REAL_ESTATE',
    'VEHICLE',
    'OTHER_ASSET',
    'CREDIT_CARD',
    'MORTGAGE',
    'HELOC',
    'LOAN',
    'OTHER_LIABILITY'
);

CREATE TYPE currency_code AS ENUM (
    'CAD',
    'USD',
    'EUR',
    'GBP',
    'INR',
    'OTHER'
);

CREATE TYPE document_type AS ENUM (
    'BANK_STATEMENT',
    'CREDIT_CARD_STATEMENT',
    'INVESTMENT_STATEMENT',
    'MORTGAGE_STATEMENT',
    'HELOC_STATEMENT',
    'SCREENSHOT',
    'OTHER'
);

CREATE TYPE document_status AS ENUM (
    'UPLOADED',
    'PROCESSING',
    'PROCESSED',
    'REVIEW_REQUIRED',
    'FAILED'
);

CREATE TYPE extraction_method AS ENUM (
    'MANUAL',
    'PDF_TEXT',
    'OCR',
    'AI'
);

CREATE TYPE processing_status AS ENUM (
    'PENDING',
    'PROCESSING',
    'COMPLETED',
    'FAILED',
    'PARTIAL'
);


-- ============================================================
-- USERS
-- ============================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    email VARCHAR(255) NOT NULL UNIQUE,

    first_name VARCHAR(100),
    last_name VARCHAR(100),

    timezone VARCHAR(100) DEFAULT 'America/Toronto',

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- FINANCIAL INSTITUTIONS
-- ============================================================

CREATE TABLE financial_institutions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(200) NOT NULL,

    short_name VARCHAR(100),

    website VARCHAR(500),

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_financial_institution_name
        UNIQUE (name)
);


-- ============================================================
-- ACCOUNTS
-- ============================================================

CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL,

    institution_id UUID,

    name VARCHAR(200) NOT NULL,

    account_type account_type NOT NULL,

    classification account_classification NOT NULL,

    account_number_last4 VARCHAR(4),

    currency currency_code NOT NULL DEFAULT 'CAD',

    description TEXT,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    include_in_net_worth BOOLEAN NOT NULL DEFAULT TRUE,

    expected_statement BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_accounts_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_accounts_institution
        FOREIGN KEY (institution_id)
        REFERENCES financial_institutions(id)
        ON DELETE SET NULL
);


-- ============================================================
-- ACCOUNT SNAPSHOTS
-- ============================================================

CREATE TABLE account_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    account_id UUID NOT NULL,

    snapshot_date DATE NOT NULL,

    balance NUMERIC(19,4) NOT NULL,

    currency currency_code NOT NULL DEFAULT 'CAD',

    extraction_method extraction_method NOT NULL DEFAULT 'MANUAL',

    confidence_score NUMERIC(5,2),

    is_verified BOOLEAN NOT NULL DEFAULT FALSE,

    source_document_id UUID,

    notes TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_snapshot_account
        FOREIGN KEY (account_id)
        REFERENCES accounts(id)
        ON DELETE CASCADE,

    CONSTRAINT chk_confidence_score
        CHECK (
            confidence_score IS NULL
            OR (
                confidence_score >= 0
                AND confidence_score <= 100
            )
        ),

    CONSTRAINT uq_account_snapshot
        UNIQUE (account_id, snapshot_date)
);


-- ============================================================
-- DOCUMENTS
-- ============================================================

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL,

    document_type document_type NOT NULL,

    original_filename VARCHAR(500) NOT NULL,

    storage_path VARCHAR(1000),

    file_hash VARCHAR(128),

    mime_type VARCHAR(100),

    file_size_bytes BIGINT,

    statement_date DATE,

    status document_status NOT NULL DEFAULT 'UPLOADED',

    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    processed_at TIMESTAMPTZ,

    error_message TEXT,

    CONSTRAINT fk_documents_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


-- ============================================================
-- EXTRACTION RESULTS
-- ============================================================

CREATE TABLE extraction_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    document_id UUID NOT NULL,

    account_id UUID,

    extracted_institution VARCHAR(200),

    extracted_account_name VARCHAR(300),

    extracted_account_last4 VARCHAR(4),

    extracted_statement_date DATE,

    extracted_balance NUMERIC(19,4),

    extracted_currency currency_code,

    extraction_method extraction_method NOT NULL,

    confidence_score NUMERIC(5,2),

    raw_text TEXT,

    raw_json JSONB,

    requires_review BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_extraction_document
        FOREIGN KEY (document_id)
        REFERENCES documents(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_extraction_account
        FOREIGN KEY (account_id)
        REFERENCES accounts(id)
        ON DELETE SET NULL,

    CONSTRAINT chk_extraction_confidence
        CHECK (
            confidence_score IS NULL
            OR (
                confidence_score >= 0
                AND confidence_score <= 100
            )
        )
);


-- ============================================================
-- MONTHLY NET WORTH SNAPSHOTS
-- ============================================================

CREATE TABLE monthly_net_worth (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL,

    snapshot_month DATE NOT NULL,

    total_assets NUMERIC(19,4) NOT NULL DEFAULT 0,

    total_liabilities NUMERIC(19,4) NOT NULL DEFAULT 0,

    net_worth NUMERIC(19,4) NOT NULL DEFAULT 0,

    asset_account_count INTEGER NOT NULL DEFAULT 0,

    liability_account_count INTEGER NOT NULL DEFAULT 0,

    is_finalized BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_monthly_networth_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_user_monthly_networth
        UNIQUE (user_id, snapshot_month)
);


-- ============================================================
-- PROPERTIES
-- ============================================================

CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL,

    name VARCHAR(200) NOT NULL,

    address TEXT,

    estimated_value NUMERIC(19,4),

    currency currency_code NOT NULL DEFAULT 'CAD',

    include_in_net_worth BOOLEAN NOT NULL DEFAULT TRUE,

    valuation_date DATE,

    notes TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_properties_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


-- ============================================================
-- PROPERTY VALUATIONS
-- ============================================================

CREATE TABLE property_valuations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    property_id UUID NOT NULL,

    valuation_date DATE NOT NULL,

    estimated_value NUMERIC(19,4) NOT NULL,

    currency currency_code NOT NULL DEFAULT 'CAD',

    source VARCHAR(200),

    notes TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_property_valuation_property
        FOREIGN KEY (property_id)
        REFERENCES properties(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_property_valuation
        UNIQUE (property_id, valuation_date)
);


-- ============================================================
-- PROCESSING JOBS
-- ============================================================

CREATE TABLE processing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL,

    job_type VARCHAR(100) NOT NULL,

    status processing_status NOT NULL DEFAULT 'PENDING',

    period_start DATE,

    period_end DATE,

    total_documents INTEGER NOT NULL DEFAULT 0,

    processed_documents INTEGER NOT NULL DEFAULT 0,

    failed_documents INTEGER NOT NULL DEFAULT 0,

    started_at TIMESTAMPTZ,

    completed_at TIMESTAMPTZ,

    error_message TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_processing_job_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


-- ============================================================
-- PROCESSING JOB DOCUMENTS
-- ============================================================

CREATE TABLE processing_job_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    job_id UUID NOT NULL,

    document_id UUID NOT NULL,

    status processing_status NOT NULL DEFAULT 'PENDING',

    error_message TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_job_document_job
        FOREIGN KEY (job_id)
        REFERENCES processing_jobs(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_job_document_document
        FOREIGN KEY (document_id)
        REFERENCES documents(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_job_document
        UNIQUE (job_id, document_id)
);


-- ============================================================
-- AUDIT LOG
-- ============================================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID,

    entity_type VARCHAR(100) NOT NULL,

    entity_id UUID,

    action VARCHAR(100) NOT NULL,

    old_value JSONB,

    new_value JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_audit_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE SET NULL
);


-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX idx_accounts_user
    ON accounts(user_id);

CREATE INDEX idx_accounts_institution
    ON accounts(institution_id);

CREATE INDEX idx_account_snapshots_account
    ON account_snapshots(account_id);

CREATE INDEX idx_account_snapshots_date
    ON account_snapshots(snapshot_date);

CREATE INDEX idx_documents_user
    ON documents(user_id);

CREATE INDEX idx_documents_status
    ON documents(status);

CREATE INDEX idx_documents_statement_date
    ON documents(statement_date);

CREATE INDEX idx_extraction_document
    ON extraction_results(document_id);

CREATE INDEX idx_extraction_account
    ON extraction_results(account_id);

CREATE INDEX idx_monthly_networth_user
    ON monthly_net_worth(user_id);

CREATE INDEX idx_monthly_networth_month
    ON monthly_net_worth(snapshot_month);

CREATE INDEX idx_processing_jobs_user
    ON processing_jobs(user_id);

CREATE INDEX idx_audit_logs_user
    ON audit_logs(user_id);

CREATE INDEX idx_audit_logs_entity
    ON audit_logs(entity_type, entity_id);


-- ============================================================
-- DEFAULT FINANCIAL INSTITUTIONS
-- ============================================================

INSERT INTO financial_institutions (name, short_name)
VALUES
    ('TD Canada Trust', 'TD'),
    ('Royal Bank of Canada', 'RBC'),
    ('Bank of Montreal', 'BMO'),
    ('Scotiabank', 'Scotiabank'),
    ('Canadian Imperial Bank of Commerce', 'CIBC'),
    ('National Bank of Canada', 'National Bank'),
    ('Tangerine Bank', 'Tangerine'),
    ('Simplii Financial', 'Simplii'),
    ('Questrade', 'Questrade'),
    ('Wealthsimple', 'Wealthsimple'),
    ('EQ Bank', 'EQ Bank'),
    ('Manulife', 'Manulife'),
    ('Sun Life', 'Sun Life'),
    ('Other', 'Other')
ON CONFLICT (name) DO NOTHING;


COMMIT;