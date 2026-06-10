-- ============================================================
-- PROFIT & LOSS STATEMENT (Monthly)
-- Purpose : Derive P&L from raw GL entries.
--           Revenue accounts (4xxx) = Credits.
--           Expense accounts (5xxx, 6xxx) = Debits.
--           Gross Profit = Revenue - COGS
--           Net Profit = Gross Profit - Operating Expenses
-- Scope   : USD entries only for comparable P&L.
-- ============================================================

WITH monthly_gl AS (
    SELECT
        STRFTIME('%Y-%m', TxnDate)  AS YearMonth,
        STRFTIME('%Y', TxnDate)     AS Year,
        AccountNumber,
        AccountName,
        CASE
            WHEN AccountNumber IN (4000, 4010) THEN 'Revenue'
            WHEN AccountNumber = 5000          THEN 'COGS'
            WHEN AccountNumber IN (5010, 6000) THEN 'Operating Expense'
        END AS AccountType,
        ROUND(SUM(Credit - Debit), 2) AS NetAmount
    FROM general_ledger
    WHERE Currency = 'USD'
    GROUP BY YearMonth, AccountNumber, AccountName
),
pnl AS (
    SELECT
        YearMonth,
        Year,
        ROUND(SUM(CASE WHEN AccountType = 'Revenue'          THEN NetAmount ELSE 0 END), 2) AS Revenue,
        ROUND(SUM(CASE WHEN AccountType = 'COGS'             THEN -NetAmount ELSE 0 END), 2) AS COGS,
        ROUND(SUM(CASE WHEN AccountType = 'Operating Expense' THEN -NetAmount ELSE 0 END), 2) AS OpEx
    FROM monthly_gl
    GROUP BY YearMonth
)
SELECT
    YearMonth,
    Year,
    Revenue,
    COGS,
    ROUND(Revenue - COGS, 2)          AS GrossProfit,
    ROUND((Revenue - COGS)
          / NULLIF(Revenue, 0) * 100, 1) AS GrossMarginPct,
    OpEx,
    ROUND(Revenue - COGS - OpEx, 2)   AS NetProfit,
    ROUND((Revenue - COGS - OpEx)
          / NULLIF(Revenue, 0) * 100, 1) AS NetMarginPct
FROM pnl
WHERE Revenue > 0 OR COGS > 0 OR OpEx > 0
ORDER BY YearMonth;
