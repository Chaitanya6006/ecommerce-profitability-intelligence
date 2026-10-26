-- ============================================================================
-- 05_customer_rfm.sql
-- Customer RFM (Recency, Frequency, Monetary) Segmentation
-- Assigns quintile scores (NTILE 5) and maps customers to strategic personas
-- ============================================================================

WITH dataset_snapshot AS (
    -- Reference date is the latest order timestamp in the historical dataset (2015-12-31)
    SELECT MAX(full_date) AS max_calendar_date
    FROM dim_date d
    JOIN fact_orders f ON d.date_key = f.order_date_key
),
customer_raw_metrics AS (
    SELECT
        c.customer_key,
        c.customer_id,
        c.customer_name,
        c.segment AS market_segment,
        MAX(d.full_date) AS last_order_date,
        -- Recency: Days elapsed between last purchase and dataset snapshot date
        CAST((JULIANDAY((SELECT max_calendar_date FROM dataset_snapshot)) - JULIANDAY(MAX(d.full_date))) AS INTEGER) AS recency_days,
        -- Frequency: Count of distinct transactional orders placed
        COUNT(DISTINCT f.order_id) AS order_frequency,
        -- Monetary: Net sales and net profit contributed
        ROUND(SUM(f.sales), 2) AS monetary_sales,
        ROUND(SUM(f.profit), 2) AS monetary_profit,
        SUM(f.quantity) AS total_units_bought,
        SUM(f.is_returned) AS total_returned_items
    FROM fact_orders f
    JOIN dim_customers c ON f.customer_key = c.customer_key
    JOIN dim_date d ON f.order_date_key = d.date_key
    GROUP BY c.customer_key, c.customer_id, c.customer_name, c.segment
),
customer_quintiles AS (
    SELECT
        *,
        -- R Score: Lower recency_days gets higher score (5 = most recent)
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        -- F Score: Higher frequency gets higher score (5 = most frequent)
        NTILE(5) OVER (ORDER BY order_frequency ASC) AS f_score,
        -- M Score: Higher net sales gets higher score (5 = highest spending)
        NTILE(5) OVER (ORDER BY monetary_sales ASC) AS m_score
    FROM customer_raw_metrics
),
customer_segmented AS (
    SELECT
        *,
        CASE
            -- Explicit Business Rule: Margin Drainers are customers who generated negative net profit
            WHEN monetary_profit < 0 THEN 'Margin Drainers (Negative Profit)'
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score < 3 THEN 'Potential Loyalists'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk / Churn Warning'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Hibernating / Inactive'
            ELSE 'Standard / Occasional Customers'
        END AS rfm_segment
    FROM customer_quintiles
)
-- Segment Level Aggregate Summary
SELECT
    rfm_segment,
    COUNT(*) AS customer_count,
    ROUND((COUNT(*) * 100.0) / (SELECT COUNT(*) FROM customer_segmented), 2) AS customer_share_pct,
    ROUND(AVG(recency_days), 1) AS avg_recency_days,
    ROUND(AVG(order_frequency), 2) AS avg_order_frequency,
    ROUND(SUM(monetary_sales), 2) AS total_segment_sales_usd,
    ROUND(AVG(monetary_sales), 2) AS avg_sales_per_customer_usd,
    ROUND(SUM(monetary_profit), 2) AS total_segment_profit_usd,
    ROUND((SUM(monetary_profit) / NULLIF(SUM(monetary_sales), 0)) * 100.0, 2) AS segment_profit_margin_pct,
    SUM(total_returned_items) AS total_returned_items
FROM customer_segmented
GROUP BY rfm_segment
ORDER BY total_segment_profit_usd DESC;
