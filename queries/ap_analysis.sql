-- ============================================================
-- ACCOUNTS PAYABLE ANALYSIS
-- Purpose : AP aging by vendor, DPO calculation,
--           and payment obligation exposure per status.
-- ============================================================

WITH ref AS (
    SELECT MAX(InvoiceDate) AS today FROM accounts_payable
),
ap_aged AS (
    SELECT
        ap.APID,
        ap.Vendor,
        ap.InvoiceDate,
        ap.DueDate,
        ap.Amount,
        ap.Currency,
        ap.Status,
        rd.today AS ReferenceDate,
        CAST(JULIANDAY(rd.today) - JULIANDAY(ap.InvoiceDate) AS INTEGER) AS DaysOld,
        CASE
            WHEN ap.Status = 'Paid' THEN 'Paid'
            WHEN CAST(JULIANDAY(rd.today) - JULIANDAY(ap.DueDate) AS INTEGER) <= 0  THEN 'Current'
            WHEN CAST(JULIANDAY(rd.today) - JULIANDAY(ap.DueDate) AS INTEGER) <= 30 THEN '1-30 days overdue'
            WHEN CAST(JULIANDAY(rd.today) - JULIANDAY(ap.DueDate) AS INTEGER) <= 60 THEN '31-60 days overdue'
            ELSE '60+ days overdue'
        END AS AgingBucket
    FROM accounts_payable ap
    JOIN ref rd ON 1=1
),
vendor_summary AS (
    SELECT
        Vendor,
        COUNT(*)                                                        AS TotalInvoices,
        ROUND(SUM(Amount), 2)                                           AS TotalAmount,
        ROUND(SUM(CASE WHEN Status = 'Open'    THEN Amount ELSE 0 END), 2) AS OpenAmount,
        ROUND(SUM(CASE WHEN Status = 'Partial' THEN Amount ELSE 0 END), 2) AS PartialAmount,
        ROUND(SUM(CASE WHEN Status = 'Paid'    THEN Amount ELSE 0 END), 2) AS PaidAmount,
        COUNT(CASE WHEN Status = 'Open'    THEN 1 END)                  AS OpenCount,
        COUNT(CASE WHEN Status = 'Partial' THEN 1 END)                  AS PartialCount,
        COUNT(CASE WHEN Status = 'Paid'    THEN 1 END)                  AS PaidCount,
        -- DPO = (AP Balance / COGS) x Days
        ROUND(
            SUM(CASE WHEN Status IN ('Open','Partial') THEN Amount ELSE 0 END)
            / NULLIF(SUM(Amount), 0) * 30, 1
        )                                                               AS EstimatedDPO
    FROM accounts_payable
    GROUP BY Vendor
)
SELECT
    Vendor,
    TotalInvoices,
    TotalAmount,
    OpenAmount,
    PartialAmount,
    PaidAmount,
    OpenCount,
    PartialCount,
    PaidCount,
    EstimatedDPO,
    ROUND((OpenAmount + PartialAmount) / NULLIF(TotalAmount, 0) * 100, 1) AS UnpaidPct
FROM vendor_summary
ORDER BY OpenAmount DESC;
