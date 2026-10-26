-- ============================================================================
-- 04_discount_analysis.sql
-- Promotional Discount & Margin Degradation Analysis
-- Evaluates transaction volume, profit margins, and erosion across discount tiers
-- 
-- NOTE ON CAUSALITY:
-- Findings in this script represent observed historical associations across
-- discount brackets. While deep discounting correlates strongly with negative
-- margins, causal claims require econometric modeling to control for product mix.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. Enterprise Discount Tier Breakdown
-- ----------------------------------------------------------------------------
WITH discount_binned AS (
    SELECT
        order_id,
        sales,
        gross_sales,
        discount_amount,
        profit,
        discount,
        is_returned,
        CASE
            WHEN discount = 0.00 THEN '01. No Discount (0%)'
            WHEN discount <= 0.10 THEN '02. Low Discount (0.01% - 10%)'
            WHEN discount <= 0.20 THEN '03. Moderate Discount (10.01% - 20%)'
            WHEN discount <= 0.40 THEN '04. Aggressive Discount (20.01% - 40%)'
            ELSE '05. Deep Discount (> 40%)'
        END AS discount_tier
    FROM fact_orders
)
SELECT
    discount_tier,
    COUNT(DISTINCT order_id) AS distinct_orders,
    COUNT(*) AS total_line_items,
    ROUND((COUNT(*) * 100.0) / (SELECT COUNT(*) FROM fact_orders), 2) AS line_item_volume_share_pct,
    ROUND(SUM(gross_sales), 2) AS gross_sales_usd,
    ROUND(SUM(discount_amount), 2) AS total_discount_concession_usd,
    ROUND(SUM(sales), 2) AS net_sales_usd,
    ROUND(SUM(profit), 2) AS total_net_profit_usd,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100.0, 2) AS net_profit_margin_pct,
    ROUND(AVG(discount) * 100.0, 2) AS avg_discount_pct,
    ROUND((SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 2) AS unprofitable_order_lines_pct,
    ROUND((SUM(is_returned) * 100.0) / COUNT(*), 2) AS return_rate_pct
FROM discount_binned
GROUP BY discount_tier
ORDER BY discount_tier ASC;

-- ----------------------------------------------------------------------------
-- 2. Category Discount Elasticity & Margin Degradation Matrix
-- ----------------------------------------------------------------------------
WITH cat_discount AS (
    SELECT
        p.category,
        CASE
            WHEN f.discount = 0.00 THEN '01. No Discount (0%)'
            WHEN f.discount <= 0.20 THEN '02. Low/Moderate (0.01% - 20%)'
            ELSE '03. Aggressive/Deep (> 20%)'
        END AS discount_bracket,
        f.sales,
        f.profit,
        f.discount,
        f.is_returned
    FROM fact_orders f
    JOIN dim_products p ON f.product_key = p.product_key
)
SELECT
    category,
    discount_bracket,
    COUNT(*) AS total_line_items,
    ROUND(SUM(sales), 2) AS net_sales_usd,
    ROUND(SUM(profit), 2) AS net_profit_usd,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100.0, 2) AS profit_margin_pct,
    ROUND(AVG(discount) * 100.0, 2) AS avg_discount_applied_pct,
    ROUND((SUM(is_returned) * 100.0) / COUNT(*), 2) AS return_rate_pct
FROM cat_discount
GROUP BY category, discount_bracket
ORDER BY category, discount_bracket;
