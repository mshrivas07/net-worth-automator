-- Net Worth Automator - Development/Test Seed Data
-- Target DB/schema: net_worth_auotmator_db / networth
-- PostgreSQL 18
--
-- Test user_id intentionally matches the UUID used in Swagger:
-- 3fa85f64-5717-4562-b3fc-2c963f66afa6
--
-- All test balances are CAD so the current NetWorthService can safely sum them.
-- This script is intended for DEVELOPMENT/TEST databases only.

BEGIN;

-- ============================================================
-- 1. Clean previous test data
-- ============================================================

DELETE FROM networth.account_snapshots
WHERE account_id IN (
    '10000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000002',
    '10000000-0000-0000-0000-000000000003',
    '10000000-0000-0000-0000-000000000004',
    '10000000-0000-0000-0000-000000000005',
    '10000000-0000-0000-0000-000000000006',
    '10000000-0000-0000-0000-000000000007',
    '10000000-0000-0000-0000-000000000008'
);

DELETE FROM networth.monthly_net_worth
WHERE user_id = '3fa85f64-5717-4562-b3fc-2c963f66afa6';

DELETE FROM networth.accounts
WHERE id IN (
    '10000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000002',
    '10000000-0000-0000-0000-000000000003',
    '10000000-0000-0000-0000-000000000004',
    '10000000-0000-0000-0000-000000000005',
    '10000000-0000-0000-0000-000000000006',
    '10000000-0000-0000-0000-000000000007',
    '10000000-0000-0000-0000-000000000008'
);

DELETE FROM networth.financial_institutions
WHERE id IN (
    '20000000-0000-0000-0000-000000000001',
    '20000000-0000-0000-0000-000000000002'
);

DELETE FROM networth.users
WHERE id = '3fa85f64-5717-4562-b3fc-2c963f66afa6';

-- ============================================================
-- 2. Test User
-- ============================================================

INSERT INTO networth.users (
    id, email, first_name, last_name, timezone,
    is_active, created_at, updated_at
)
VALUES (
    '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    'test.user@networth.local',
    'Test',
    'User',
    'America/Toronto',
    TRUE,
    NOW(),
    NOW()
);

-- ============================================================
-- 3. Financial Institutions
-- ============================================================

INSERT INTO networth.financial_institutions (
    id, name, short_name, website,
    is_active, created_at, updated_at
)
VALUES
(
    '20000000-0000-0000-0000-000000000001',
    'Royal Bank of Canada',
    'RBC',
    'https://www.rbcroyalbank.com',
    TRUE,
    NOW(),
    NOW()
),
(
    '20000000-0000-0000-0000-000000000002',
    'Toronto-Dominion Bank',
    'TD',
    'https://www.td.com',
    TRUE,
    NOW(),
    NOW()
);

-- ============================================================
-- 4. Accounts
-- ============================================================
-- Active + included:
--   001 Chequing       ASSET
--   002 Savings        ASSET
--   003 TFSA           ASSET
--   004 RRSP           ASSET
--   005 Primary Home   ASSET
--   006 Credit Card    LIABILITY
--   007 Mortgage       LIABILITY
--
-- Special test cases:
--   008 Old Savings    ASSET, INACTIVE
--   009 excluded account can be created manually later if needed

INSERT INTO networth.accounts (
    id, user_id, institution_id, name, account_type,
    classification, account_number_last4, currency,
    description, is_active, include_in_net_worth,
    expected_statement, created_at, updated_at
)
VALUES
(
    '10000000-0000-0000-0000-000000000001',
    '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    '20000000-0000-0000-0000-000000000001',
    'RBC Chequing',
    'CHEQUING',
    'ASSET',
    '1001',
    'CAD',
    'Primary day-to-day bank account',
    TRUE, TRUE, TRUE, NOW(), NOW()
),
(
    '10000000-0000-0000-0000-000000000002',
    '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    '20000000-0000-0000-0000-000000000001',
    'RBC Savings',
    'SAVINGS',
    'ASSET',
    '2002',
    'CAD',
    'Emergency savings',
    TRUE, TRUE, TRUE, NOW(), NOW()
),
(
    '10000000-0000-0000-0000-000000000003',
    '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    '20000000-0000-0000-0000-000000000002',
    'TD TFSA',
    'TFSA',
    'ASSET',
    '3003',
    'CAD',
    'Long-term investment account',
    TRUE, TRUE, TRUE, NOW(), NOW()
),
(
    '10000000-0000-0000-0000-000000000004',
    '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    '20000000-0000-0000-0000-000000000002',
    'TD RRSP',
    'RRSP',
    'ASSET',
    '4004',
    'CAD',
    'Retirement account',
    TRUE, TRUE, TRUE, NOW(), NOW()
),
(
    '10000000-0000-0000-0000-000000000005',
    '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    NULL,
    'Primary Home',
    'REAL_ESTATE',
    'ASSET',
    NULL,
    'CAD',
    'Primary residence',
    TRUE, TRUE, FALSE, NOW(), NOW()
),
(
    '10000000-0000-0000-0000-000000000006',
    '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    '20000000-0000-0000-0000-000000000001',
    'RBC Credit Card',
    'CREDIT_CARD',
    'LIABILITY',
    '6006',
    'CAD',
    'Credit card balance',
    TRUE, TRUE, TRUE, NOW(), NOW()
),
(
    '10000000-0000-0000-0000-000000000007',
    '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    '20000000-0000-0000-0000-000000000002',
    'TD Mortgage',
    'MORTGAGE',
    'LIABILITY',
    '7007',
    'CAD',
    'Primary home mortgage',
    TRUE, TRUE, TRUE, NOW(), NOW()
),
(
    '10000000-0000-0000-0000-000000000008',
    '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    '20000000-0000-0000-0000-000000000001',
    'Old Savings',
    'SAVINGS',
    'ASSET',
    '8008',
    'CAD',
    'Inactive account used to test active_only',
    FALSE, TRUE, TRUE, NOW(), NOW()
);

-- ============================================================
-- 5. Account Snapshots
-- ============================================================
-- Dates:
--   2026-01-31
--   2026-02-28
--   2026-03-31
--
-- Expected active/included totals for 2026-03-31:
--
-- Assets:
--   Chequing   15,000
--   Savings    30,000
--   TFSA       60,000
--   RRSP       90,000
--   Home      650,000
--   ----------------
--   Total     845,000
--
-- Liabilities:
--   Credit Card  3,200
--   Mortgage   398,000
--   ----------------
--   Total      401,200
--
-- Net Worth = 443,800

INSERT INTO networth.account_snapshots (
    id, account_id, snapshot_date, balance, currency,
    extraction_method, confidence_score, is_verified,
    source_document_id, notes, created_at, updated_at
)
VALUES
-- ==========================================================
-- 2026-01-31
-- ==========================================================
('30000000-0000-0000-0000-000000000001',
 '10000000-0000-0000-0000-000000000001',
 '2026-01-31', 10000, 'CAD', 'MANUAL', 100, TRUE, NULL, 'January test balance', NOW(), NOW()),

('30000000-0000-0000-0000-000000000002',
 '10000000-0000-0000-0000-000000000002',
 '2026-01-31', 25000, 'CAD', 'MANUAL', 100, TRUE, NULL, 'January test balance', NOW(), NOW()),

('30000000-0000-0000-0000-000000000003',
 '10000000-0000-0000-0000-000000000003',
 '2026-01-31', 50000, 'CAD', 'MANUAL', 100, TRUE, NULL, 'January test balance', NOW(), NOW()),

('30000000-0000-0000-0000-000000000004',
 '10000000-0000-0000-0000-000000000004',
 '2026-01-31', 80000, 'CAD', 'MANUAL', 100, TRUE, NULL, 'January test balance', NOW(), NOW()),

('30000000-0000-0000-0000-000000000005',
 '10000000-0000-0000-0000-000000000005',
 '2026-01-31', 600000, 'CAD', 'MANUAL', 100, TRUE, NULL, 'January home valuation', NOW(), NOW()),

('30000000-0000-0000-0000-000000000006',
 '10000000-0000-0000-0000-000000000006',
 '2026-01-31', 2500, 'CAD', 'MANUAL', 100, TRUE, NULL, 'January credit card balance', NOW(), NOW()),

('30000000-0000-0000-0000-000000000007',
 '10000000-0000-0000-0000-000000000007',
 '2026-01-31', 405000, 'CAD', 'MANUAL', 100, TRUE, NULL, 'January mortgage balance', NOW(), NOW()),

-- ==========================================================
-- 2026-02-28
-- ==========================================================
('30000000-0000-0000-0000-000000000011',
 '10000000-0000-0000-0000-000000000001',
 '2026-02-28', 12000, 'CAD', 'MANUAL', 100, TRUE, NULL, 'February test balance', NOW(), NOW()),

('30000000-0000-0000-0000-000000000012',
 '10000000-0000-0000-0000-000000000002',
 '2026-02-28', 28000, 'CAD', 'MANUAL', 100, TRUE, NULL, 'February test balance', NOW(), NOW()),

('30000000-0000-0000-0000-000000000013',
 '10000000-0000-0000-0000-000000000003',
 '2026-02-28', 55000, 'CAD', 'MANUAL', 100, TRUE, NULL, 'February test balance', NOW(), NOW()),

('30000000-0000-0000-0000-000000000014',
 '10000000-0000-0000-0000-000000000004',
 '2026-02-28', 85000, 'CAD', 'MANUAL', 100, TRUE, NULL, 'February test balance', NOW(), NOW()),

('30000000-0000-0000-0000-000000000015',
 '10000000-0000-0000-0000-000000000005',
 '2026-02-28', 625000, 'CAD', 'MANUAL', 100, TRUE, NULL, 'February home valuation', NOW(), NOW()),

('30000000-0000-0000-0000-000000000016',
 '10000000-0000-0000-0000-000000000006',
 '2026-02-28', 2800, 'CAD', 'MANUAL', 100, TRUE, NULL, 'February credit card balance', NOW(), NOW()),

('30000000-0000-0000-0000-000000000017',
 '10000000-0000-0000-0000-000000000007',
 '2026-02-28', 401500, 'CAD', 'MANUAL', 100, TRUE, NULL, 'February mortgage balance', NOW(), NOW()),

-- ==========================================================
-- 2026-03-31
-- ==========================================================
('30000000-0000-0000-0000-000000000021',
 '10000000-0000-0000-0000-000000000001',
 '2026-03-31', 15000, 'CAD', 'MANUAL', 100, TRUE, NULL, 'March test balance', NOW(), NOW()),

('30000000-0000-0000-0000-000000000022',
 '10000000-0000-0000-0000-000000000002',
 '2026-03-31', 30000, 'CAD', 'MANUAL', 100, TRUE, NULL, 'March test balance', NOW(), NOW()),

('30000000-0000-0000-0000-000000000023',
 '10000000-0000-0000-0000-000000000003',
 '2026-03-31', 60000, 'CAD', 'MANUAL', 100, TRUE, NULL, 'March test balance', NOW(), NOW()),

('30000000-0000-0000-0000-000000000024',
 '10000000-0000-0000-0000-000000000004',
 '2026-03-31', 90000, 'CAD', 'MANUAL', 100, TRUE, NULL, 'March test balance', NOW(), NOW()),

('30000000-0000-0000-0000-000000000025',
 '10000000-0000-0000-0000-000000000005',
 '2026-03-31', 650000, 'CAD', 'MANUAL', 100, TRUE, NULL, 'March home valuation', NOW(), NOW()),

('30000000-0000-0000-0000-000000000026',
 '10000000-0000-0000-0000-000000000006',
 '2026-03-31', 3200, 'CAD', 'MANUAL', 100, TRUE, NULL, 'March credit card balance', NOW(), NOW()),

('30000000-0000-0000-0000-000000000027',
 '10000000-0000-0000-0000-000000000007',
 '2026-03-31', 398000, 'CAD', 'MANUAL', 100, TRUE, NULL, 'March mortgage balance', NOW(), NOW()),

-- Inactive account snapshot: should appear in normal account GET,
-- but should NOT be counted in net worth because is_active = false.
('30000000-0000-0000-0000-000000000028',
 '10000000-0000-0000-0000-000000000008',
 '2026-03-31', 5000, 'CAD', 'MANUAL', 100, TRUE, NULL, 'Inactive account test', NOW(), NOW());

-- ============================================================
-- 6. Monthly Net Worth History
-- ============================================================
-- This table is only used by GET /api/v1/net-worth/history/all
-- in the current backend.

INSERT INTO networth.monthly_net_worth (
    id, user_id, snapshot_month,
    total_assets, total_liabilities, net_worth,
    asset_account_count, liability_account_count,
    is_finalized, created_at, updated_at
)
VALUES
(
    '40000000-0000-0000-0000-000000000001',
    '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    '2026-01-31',
    765000,
    407500,
    357500,
    5,
    2,
    TRUE,
    NOW(), NOW()
),
(
    '40000000-0000-0000-0000-000000000002',
    '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    '2026-02-28',
    805000,
    404300,
    400700,
    5,
    2,
    TRUE,
    NOW(), NOW()
),
(
    '40000000-0000-0000-0000-000000000003',
    '3fa85f64-5717-4562-b3fc-2c963f66afa6',
    '2026-03-31',
    845000,
    401200,
    443800,
    5,
    2,
    TRUE,
    NOW(), NOW()
);

COMMIT;

-- ============================================================
-- Quick verification
-- ============================================================

SELECT id, email, first_name, last_name
FROM networth.users
WHERE id = '3fa85f64-5717-4562-b3fc-2c963f66afa6';

SELECT id, name, account_type, classification, is_active, include_in_net_worth
FROM networth.accounts
WHERE user_id = '3fa85f64-5717-4562-b3fc-2c963f66afa6'
ORDER BY name;

SELECT
    snapshot_date,
    SUM(CASE WHEN a.classification = 'ASSET'
              AND a.is_active = TRUE
              AND a.include_in_net_worth = TRUE
             THEN s.balance ELSE 0 END) AS total_assets,
    SUM(CASE WHEN a.classification = 'LIABILITY'
              AND a.is_active = TRUE
              AND a.include_in_net_worth = TRUE
             THEN s.balance ELSE 0 END) AS total_liabilities
FROM networth.account_snapshots s
JOIN networth.accounts a ON a.id = s.account_id
WHERE a.user_id = '3fa85f64-5717-4562-b3fc-2c963f66afa6'
GROUP BY snapshot_date
ORDER BY snapshot_date;
