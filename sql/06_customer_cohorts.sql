-- ============================================================================
-- 06_customer_cohorts.sql
-- Customer Lifecycle & Cohort Retention Analysis
-- Tracks repeat purchasing activity by acquisition vintage across time
-- 
-- DEFINITIONS:
-- * Cohort Month: The calendar month of a customer's first completed purchase.
-- * Cohort Size (Denominator): Count of unique customers acquired in Month 0.
-- * Period Index: Number of elapsed calendar months since acquisition.
-- * Retention Rate %: (Active Customers in Period N / Cohort Size) * 100.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. Annual Cohort Cumulative Value & Retention Matrix
-- ----------------------------------------------------------------------------
WITH customer_acquisition AS (
    SELECT
        f.customer_key,
        MIN(d.year) AS cohort_year,
        MIN(d.full_date) AS first_order_date
    FROM fact_orders f
    JOIN dim_date d ON f.order_date_key = d.date_key
    GROUP BY f.customer_key
),
cohort_sizes AS (
    SELECT
        cohort_year,
        COUNT(DISTINCT customer_key) AS cohort_customer_count
    FROM customer_acquisition
    GROUP BY cohort_year
),
customer_annual_activity AS (
    SELECT
        ca.cohort_year,
        d.year AS activity_year,
        (d.year - ca.cohort_year) AS year_index,
        COUNT(DISTINCT f.customer_key) AS active_customers,
        COUNT(DISTINCT f.order_id) AS orders_placed,
        ROUND(SUM(f.sales), 2) AS total_sales_usd,
        ROUND(SUM(f.profit), 2) AS total_profit_usd
    FROM fact_orders f
    JOIN dim_date d ON f.order_date_key = d.date_key
    JOIN customer_acquisition ca ON f.customer_key = ca.customer_key
    GROUP BY ca.cohort_year, d.year, (d.year - ca.cohort_year)
)
SELECT
    caa.cohort_year,
    cs.cohort_customer_count AS cohort_size,
    caa.activity_year,
    caa.year_index,
    caa.active_customers,
    ROUND((caa.active_customers * 100.0) / cs.cohort_customer_count, 2) AS retention_rate_pct,
    caa.orders_placed,
    caa.total_sales_usd,
    caa.total_profit_usd,
    ROUND((caa.total_profit_usd / NULLIF(caa.total_sales_usd, 0)) * 100.0, 2) AS cohort_margin_pct
FROM customer_annual_activity caa
JOIN cohort_sizes cs ON caa.cohort_year = cs.cohort_year
ORDER BY caa.cohort_year, caa.year_index;

-- ----------------------------------------------------------------------------
-- 2. Monthly Cohort Activity (First 12 Months for 2012–2014 Cohorts)
-- ----------------------------------------------------------------------------
WITH customer_first_purchase AS (
    SELECT
        f.customer_key,
        STRFTIME('%Y-%m', MIN(d.full_date)) AS cohort_month,
        MIN(d.full_date) AS first_date
    FROM fact_orders f
    JOIN dim_date d ON f.order_date_key = d.date_key
    GROUP BY f.customer_key
),
monthly_cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_key) AS cohort_size
    FROM customer_first_purchase
    GROUP BY cohort_month
),
monthly_activity AS (
    SELECT
        cfp.cohort_month,
        -- Calculate month interval: (Year difference * 12) + Month difference
        CAST((STRFTIME('%Y', d.full_date) - STRFTIME('%Y', cfp.first_date)) * 12 +
             (STRFTIME('%m', d.full_date) - STRFTIME('%m', cfp.first_date)) AS INTEGER) AS month_index,
        COUNT(DISTINCT f.customer_key) AS active_customers,
        ROUND(SUM(f.sales), 2) AS cohort_sales,
        ROUND(SUM(f.profit), 2) AS cohort_profit
    FROM fact_orders f
    JOIN dim_date d ON f.order_date_key = d.date_key
    JOIN customer_first_purchase cfp ON f.customer_key = cfp.customer_key
    GROUP BY cfp.cohort_month, month_index
)
SELECT
    ma.cohort_month,
    mcs.cohort_size,
    ma.month_index,
    ma.active_customers,
    ROUND((ma.active_customers * 100.0) / mcs.cohort_size, 2) AS retention_rate_pct,
    ma.cohort_sales,
    ma.cohort_profit
FROM monthly_activity ma
JOIN monthly_cohort_sizes mcs ON ma.cohort_month = mcs.cohort_month
WHERE ma.month_index BETWEEN 0 AND 12
ORDER BY ma.cohort_month, ma.month_index;
