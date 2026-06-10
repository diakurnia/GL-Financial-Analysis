-- ============================================================
-- TRIAL BALANCE
-- Purpose : Summarise total debits and credits per account
--           and verify whether the GL is in balance.
-- Note    : Multi-currency amounts are compared as-is.
--           A balanced GL requires total debits = total credits
--           within the same currency.
-- ============================================================

WITH account_balances AS (
    SELECT
        AccountNumber,
        AccountName,
        Currency,
        ROUND(SUM(Debit),  2) AS TotalDebit,
        ROUND(SUM(Credit), 2) AS TotalCredit,
        ROUND(SUM(Debit) - SUM(Credit), 2) AS NetBalance,
        COUNT(*) AS TxnCount
    FROM general_ledger
    GROUP BY AccountNumber, AccountName, Currency
),
currency_check AS (
    SELECT
        Currency,
        ROUND(SUM(Debit),  2) AS CurrencyDebit,
        ROUND(SUM(Credit), 2) AS CurrencyCredit,
        ROUND(SUM(Debit) - SUM(Credit), 2) AS CurrencyImbalance,
        CASE
            WHEN ROUND(SUM(Debit), 2) = ROUND(SUM(Credit), 2)
            THEN 'BALANCED'
            ELSE 'IMBALANCED'
        END AS BalanceStatus
    FROM general_ledger
    GROUP BY Currency
)
SELECT
    ab.AccountNumber,
    ab.AccountName,
    ab.Currency,
    ab.TotalDebit,
    ab.TotalCredit,
    ab.NetBalance,
    ab.TxnCount,
    cc.BalanceStatus
FROM account_balances ab
JOIN currency_check cc ON ab.Currency = cc.Currency
ORDER BY ab.Currency, ab.AccountNumber;
