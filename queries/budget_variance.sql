-- ============================================================
-- BUDGET VARIANCE ANALYSIS
-- Purpose : Compare Budget vs Forecast vs Actual per
--           department and quarter. Flag over/under budget.
-- ============================================================

WITH variance_detail AS (
    SELECT
        FiscalYear,
        Dept,
        Quarter,
        BudgetUSD,
        ForecastUSD,
        ActualUSD,
        VarianceUSD,
        -- Budget vs Actual variance %
        ROUND(VarianceUSD / NULLIF(BudgetUSD, 0) * 100, 1)       AS VariancePct,
        -- Forecast accuracy
        ROUND((ForecastUSD - ActualUSD)
              / NULLIF(ForecastUSD, 0) * 100, 1)                  AS ForecastErrorPct,
        CASE
            WHEN VarianceUSD > 0  THEN 'Over Budget'
            WHEN VarianceUSD < 0  THEN 'Under Budget'
            ELSE 'On Budget'
        END AS BudgetStatus,
        CASE
            WHEN ABS(VarianceUSD / NULLIF(BudgetUSD, 0)) > 0.10 THEN 'HIGH'
            WHEN ABS(VarianceUSD / NULLIF(BudgetUSD, 0)) > 0.05 THEN 'MEDIUM'
            ELSE 'LOW'
        END AS RiskFlag
    FROM budget_forecast
),
dept_totals AS (
    SELECT
        FiscalYear,
        Dept,
        ROUND(SUM(BudgetUSD), 2)    AS AnnualBudget,
        ROUND(SUM(ForecastUSD), 2)  AS AnnualForecast,
        ROUND(SUM(ActualUSD), 2)    AS AnnualActual,
        ROUND(SUM(VarianceUSD), 2)  AS AnnualVariance,
        ROUND(SUM(VarianceUSD) / NULLIF(SUM(BudgetUSD), 0) * 100, 1) AS AnnualVariancePct
    FROM budget_forecast
    GROUP BY FiscalYear, Dept
)
SELECT
    vd.FiscalYear,
    vd.Dept,
    vd.Quarter,
    vd.BudgetUSD,
    vd.ForecastUSD,
    vd.ActualUSD,
    vd.VarianceUSD,
    vd.VariancePct,
    vd.ForecastErrorPct,
    vd.BudgetStatus,
    vd.RiskFlag,
    dt.AnnualBudget,
    dt.AnnualActual,
    dt.AnnualVariance,
    dt.AnnualVariancePct
FROM variance_detail vd
JOIN dept_totals dt
  ON vd.FiscalYear = dt.FiscalYear AND vd.Dept = dt.Dept
ORDER BY vd.FiscalYear, vd.Dept, vd.Quarter;
