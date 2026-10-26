-- ============================================================================
-- 03_product_category_profitability.sql
-- Product Catalog & Category Unit Economics Analysis
-- Identifies top margin contributors, margin bleeders, and Pareto distribution
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. Category & Sub-Category Performance Summary
-- ----------------------------------------------------------------------------
SELECT
    p.category,
    p.sub_category,
    COUNT(DISTINCT f.order_id) AS distinct_orders,
    COUNT(*) AS total_line_items,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.cogs), 2) AS total_cogs,
    ROUND(SUM(f.shipping_cost), 2) AS total_shipping_cost,
    ROUND(SUM(f.profit), 2) AS total_net_profit,
    ROUND((SUM(f.profit) / NULLIF(SUM(f.sales), 0)) * 100.0, 2) AS net_profit_margin_pct,
    ROUND(AVG(f.discount) * 100.0, 2) AS avg_discount_pct,
    ROUND((SUM(CASE WHEN f.profit < 0 THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 2) AS unprofitable_line_item_pct,
    ROUND((SUM(f.is_returned) * 100.0) / COUNT(*), 2) AS line_return_rate_pct
FROM fact_orders f
JOIN dim_products p ON f.product_key = p.product_key
GROUP BY p.category, p.sub_category
ORDER BY total_net_profit DESC;

-- ----------------------------------------------------------------------------
-- 2. Top 10 High-Volume Margin Bleeders (Sales > $10,000 with Negative Profit)
-- ----------------------------------------------------------------------------
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.sub_category,
    COUNT(DISTINCT f.order_id) AS order_count,
    SUM(f.quantity) AS total_quantity,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_net_loss,
    ROUND((SUM(f.profit) / NULLIF(SUM(f.sales), 0)) * 100.0, 2) AS profit_margin_pct,
    ROUND(AVG(f.discount) * 100.0, 2) AS avg_discount_rate_pct,
    ROUND(SUM(f.shipping_cost), 2) AS total_shipping_incurred
FROM fact_orders f
JOIN dim_products p ON f.product_key = p.product_key
GROUP BY p.product_id, p.product_name, p.category, p.sub_category
HAVING SUM(f.sales) >= 5000 AND SUM(f.profit) < 0
ORDER BY total_net_loss ASC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- 3. Top 10 Most Profitable SKUs
-- ----------------------------------------------------------------------------
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.sub_category,
    COUNT(DISTINCT f.order_id) AS order_count,
    SUM(f.quantity) AS total_quantity,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_net_profit,
    ROUND((SUM(f.profit) / NULLIF(SUM(f.sales), 0)) * 100.0, 2) AS profit_margin_pct,
    ROUND(AVG(f.discount) * 100.0, 2) AS avg_discount_rate_pct
FROM fact_orders f
JOIN dim_products p ON f.product_key = p.product_key
GROUP BY p.product_id, p.product_name, p.category, p.sub_category
ORDER BY total_net_profit DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- 4. Pareto Loss Analysis (Cumulative Contribution of Unprofitable Products)
-- ----------------------------------------------------------------------------
WITH unprofitable_products AS (
    SELECT
        p.product_id,
        p.product_name,
        p.sub_category,
        ROUND(SUM(f.profit), 2) AS product_loss,
        ROUND(SUM(f.sales), 2) AS product_sales
    FROM fact_orders f
    JOIN dim_products p ON f.product_key = p.product_key
    GROUP BY p.product_id, p.product_name, p.sub_category
    HAVING SUM(f.profit) < 0
),
ranked_losses AS (
    SELECT
        product_id,
        product_name,
        sub_category,
        product_loss,
        product_sales,
        SUM(product_loss) OVER (ORDER BY product_loss ASC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_loss,
        SUM(product_loss) OVER () AS total_loss_pool
    FROM unprofitable_products
)
SELECT
    product_id,
    product_name,
    sub_category,
    product_loss,
    product_sales,
    cumulative_loss,
    ROUND((cumulative_loss / total_loss_pool) * 100.0, 2) AS cumulative_loss_share_pct
FROM ranked_losses
LIMIT 20;
