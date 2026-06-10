-- ============================================================
-- ACCOUNTS RECEIVABLE ANALYSIS
-- Purpose : AR aging by customer, DSO calculation,
--           and outstanding exposure per status.
-- Reference date : MAX(DueDate) in dataset.
-- ============================================================

WITH ref AS (
    SELECT MAX(InvoiceDate) AS today FROM accounts_receivable
),
ar_aged AS (
    SELECT
        ar.ARID,
        ar.Customer,
        ar.InvoiceDate,
        ar.DueDate,
        ar.Amount,
        ar.Currency,
        ar.Status,
        ar.Terms,
        rd.today                                                          AS ReferenceDate,
        CAST(JULIANDAY(rd.today) - JULIANDAY(ar.InvoiceDate) AS INTEGER) AS DaysOutstanding,
        CASE
            WHEN ar.Status = 'Received' THEN 'Collected'
            WHEN CAST(JULIANDAY(rd.today) - JULIANDAY(ar.DueDate) AS INTEGER) <= 0  THEN 'Current'
            WHEN CAST(JULIANDAY(rd.today) - JULIANDAY(ar.DueDate) AS INTEGER) <= 30 THEN '1-30 days overdue'
            WHEN CAST(JULIANDAY(rd.today) - JULIANDAY(ar.DueDate) AS INTEGER) <= 60 THEN '31-60 days overdue'
            WHEN CAST(JULIANDAY(rd.today) - JULIANDAY(ar.DueDate) AS INTEGER) <= 90 THEN '61-90 days overdue'
            ELSE '90+ days overdue'
        END AS AgingBucket
    FROM accounts_receivable ar
    JOIN ref rd ON 1=1
),
customer_summary AS (
    SELECT
        Customer,
        COUNT(*)                                                    AS TotalInvoices,
        ROUND(SUM(Amount), 2)                                       AS TotalBilled,
        ROUND(SUM(CASE WHEN Status = 'Open'    THEN Amount ELSE 0 END), 2) AS OpenAmount,
        ROUND(SUM(CASE WHEN Status = 'Partial' THEN Amount ELSE 0 END), 2) AS PartialAmount,
        ROUND(SUM(CASE WHEN Status = 'Received'THEN Amount ELSE 0 END), 2) AS CollectedAmount,
        COUNT(CASE WHEN Status = 'Open'    THEN 1 END)              AS OpenCount,
        COUNT(CASE WHEN Status = 'Partial' THEN 1 END)              AS PartialCount,
        -- DSO = (Open AR / Total Revenue) x Days in Period
        ROUND(
            SUM(CASE WHEN Status IN ('Open','Partial') THEN Amount ELSE 0 END)
            / NULLIF(SUM(Amount), 0) * 45, 1
        )                                                           AS EstimatedDSO
    FROM accounts_receivable
    GROUP BY Customer
)
SELECT
    cs.Customer,
    cs.TotalInvoices,
    cs.TotalBilled,
    cs.OpenAmount,
    cs.PartialAmount,
    cs.CollectedAmount,
    cs.OpenCount,
    cs.PartialCount,
    cs.EstimatedDSO,
    ROUND(cs.OpenAmount / NULLIF(cs.TotalBilled, 0) * 100, 1) AS OpenPct
FROM customer_summary cs
ORDER BY cs.OpenAmount DESC;
