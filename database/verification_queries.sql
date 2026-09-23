-- Net Worth Automator - Verification Queries
-- Run these in pgAdmin after executing seed_test_data.sql

-- 1. Confirm test user
SELECT *
FROM networth.users
WHERE id = '3fa85f64-5717-4562-b3fc-2c963f66afa6';

-- 2. All test accounts
SELECT
    id,
    name,
    account_type,
    classification,
    currency,
    is_active,
    include_in_net_worth
FROM networth.accounts
WHERE user_id = '3fa85f64-5717-4562-b3fc-2c963f66afa6'
ORDER BY name;

-- 3. Active accounts only
SELECT name, is_active
FROM networth.accounts
WHERE user_id = '3fa85f64-5717-4562-b3fc-2c963f66afa6'
  AND is_active = TRUE
ORDER BY name;

-- Expected: 7 active accounts.

-- 4. March snapshots
SELECT
    a.name,
    a.classification,
    a.is_active,
    a.include_in_net_worth,
    s.snapshot_date,
    s.balance
FROM networth.accounts a
JOIN networth.account_snapshots s
    ON s.account_id = a.id
WHERE a.user_id = '3fa85f64-5717-4562-b3fc-2c963f66afa6'
  AND s.snapshot_date = '2026-03-31'
ORDER BY a.classification, a.name;

-- 5. Expected net worth for 2026-03-31
SELECT
    SUM(CASE
        WHEN a.classification = 'ASSET'
         AND a.is_active = TRUE
         AND a.include_in_net_worth = TRUE
        THEN s.balance ELSE 0 END) AS total_assets,

    SUM(CASE
        WHEN a.classification = 'LIABILITY'
         AND a.is_active = TRUE
         AND a.include_in_net_worth = TRUE
        THEN s.balance ELSE 0 END) AS total_liabilities,

    SUM(CASE
        WHEN a.classification = 'ASSET'
         AND a.is_active = TRUE
         AND a.include_in_net_worth = TRUE
        THEN s.balance
        WHEN a.classification = 'LIABILITY'
         AND a.is_active = TRUE
         AND a.include_in_net_worth = TRUE
        THEN -s.balance
        ELSE 0
    END) AS net_worth
FROM networth.accounts a
JOIN networth.account_snapshots s
    ON s.account_id = a.id
WHERE a.user_id = '3fa85f64-5717-4562-b3fc-2c963f66afa6'
  AND s.snapshot_date = '2026-03-31';

-- Expected:
-- total_assets      = 845000
-- total_liabilities = 401200
-- net_worth         = 443800

-- 6. Monthly history table
SELECT
    snapshot_month,
    total_assets,
    total_liabilities,
    net_worth,
    asset_account_count,
    liability_account_count,
    is_finalized
FROM networth.monthly_net_worth
WHERE user_id = '3fa85f64-5717-4562-b3fc-2c963f66afa6'
ORDER BY snapshot_month;
