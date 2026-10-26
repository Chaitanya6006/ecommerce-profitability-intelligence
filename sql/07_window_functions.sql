-- ============================================================================
-- 07_window_functions.sql
-- Advanced Analytical Window Functions
-- Demonstrates RANK, DENSE_RANK, Running Aggregations, MoM Growth (LAG), and NTILE
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. Product Profitability Ranking within Category (RANK vs DENSE_RANK)
-- ----------------------------------------------------------------------------
WITH product_performance AS (
    SELECT
        p.category,
        p.sub_category,
        p.product_id,
        p.product_name,
        ROUND(SUM(f.sales), 2) AS total_sales,
        ROUND(SUM(f.profit), 2) AS total_profit,
        ROUND((SUM(f.profit) / NULLIF(SUM(f.sales), 0)) * 100.0, 2) AS margin_pct
    FROM fact_orders f
    JOIN dim_products p ON f.product_key = p.product_key
    GROUP BY p.category, p.sub_category, p.product_id, p.product_name
)
SELECT
    category,
    sub_category,
    product_name,
    total_sales,
    total_profit,
    margin_pct,
    -- Rank within Category by Profit
    RANK() OVER (PARTITION BY category ORDER BY total_profit DESC) AS profit_rank,
    DENSE_RANK() OVER (PARTITION BY category ORDER BY total_profit DESC) AS profit_dense_rank
FROM product_performance
WHERE profit_rank <= 5
ORDER BY category, profit_rank;

-- ----------------------------------------------------------------------------
-- 2. Monthly Pacing, Cumulative Running Totals & MoM Growth (LAG)
-- ----------------------------------------------------------------------------
WITH monthly_aggregation AS (
    SELECT
        d.year,
        d.month,
        STRFTIME('%Y-%m', d.full_date) AS year_month,
        COUNT(DISTINCT f.order_id) AS distinct_orders,
        ROUND(SUM(f.sales), 2) AS monthly_sales,
        ROUND(SUM(f.profit), 2) AS monthly_profit
    FROM fact_orders f
    JOIN dim_date d ON f.order_date_key = d.date_key
    GROUP BY d.year, d.month, STRFTIME('%Y-%m', d.full_date)
),
monthly_metrics AS (
    SELECT
        year_month,
        distinct_orders,
        monthly_sales,
        monthly_profit,
        -- Running Total across all preceding months
        ROUND(SUM(monthly_sales) OVER (
            ORDER BY year_month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ), 2) AS cumulative_running_sales,
        ROUND(SUM(monthly_profit) OVER (
            ORDER BY year_month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ), 2) AS cumulative_running_profit,
        -- Previous month's sales via LAG
        LAG(monthly_sales, 1) OVER (ORDER BY year_month) AS prev_month_sales,
        LAG(monthly_profit, 1) OVER (ORDER BY year_month) AS prev_month_profit
    FROM monthly_aggregation
)
SELECT
    year_month,
    distinct_orders,
    monthly_sales,
    monthly_profit,
    cumulative_running_sales,
    cumulative_running_profit,
    prev_month_sales,
    ROUND(((monthly_sales - prev_month_sales) / NULLIF(prev_month_sales, 0)) * 100.0, 2) AS mom_sales_growth_pct,
    ROUND(((monthly_profit - prev_month_profit) / NULLIF(ABS(prev_month_profit), 0)) * 100.0, 2) AS mom_profit_growth_pct
FROM monthly_metrics
ORDER BY year_month;

-- ----------------------------------------------------------------------------
-- 3. Order Basket Size Quartile Analysis (NTILE 4)
-- ----------------------------------------------------------------------------
WITH order_totals AS (
    SELECT
        f.order_id,
        COUNT(*) AS items_in_order,
        SUM(f.quantity) AS total_units,
        ROUND(SUM(f.sales), 2) AS order_total_sales,
        ROUND(SUM(f.profit), 2) AS order_total_profit,
        MAX(f.is_returned) AS order_returned
    FROM fact_orders f
    GROUP BY f.order_id
),
order_quartiles AS (
    SELECT
        *,
        NTILE(4) OVER (ORDER BY order_total_sales ASC) AS basket_quartile
    FROM order_totals
)
SELECT
    basket_quartile,
    CASE basket_quartile
        WHEN 1 THEN 'Q1 - Micro Baskets'
        WHEN 2 THEN 'Q2 - Low/Medium Baskets'
        WHEN 3 THEN 'Q3 - Medium/High Baskets'
        WHEN 4 THEN 'Q4 - Enterprise Baskets'
    END AS quartile_label,
    COUNT(*) AS total_orders,
    ROUND(MIN(order_total_sales), 2) AS min_basket_usd,
    ROUND(MAX(order_total_sales), 2) AS max_basket_usd,
    ROUND(AVG(order_total_sales), 2) AS avg_basket_usd,
    ROUND(SUM(order_total_sales), 2) AS total_sales_usd,
    ROUND(SUM(order_total_profit), 2) AS total_profit_usd,
    ROUND((SUM(order_total_profit) / NULLIF(SUM(order_total_sales), 0)) * 100.0, 2) AS quartile_profit_margin_pct,
    ROUND((SUM(order_returned) * 100.0) / COUNT(*), 2) AS return_rate_pct
FROM order_quartiles
GROUP BY basket_quartile
ORDER BY basket_quartile ASC;
