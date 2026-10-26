-- ============================================================================
-- 02_executive_kpis.sql
-- Executive Business KPI Scorecard
-- High-level enterprise metrics across sales, profitability, volume, and returns
-- ============================================================================

WITH summary_metrics AS (
    SELECT
        ROUND(SUM(sales), 2) AS total_gross_merchandise_value,
        ROUND(SUM(profit), 2) AS total_net_profit,
        ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS overall_profit_margin_pct,
        COUNT(DISTINCT order_id) AS total_distinct_orders,
        COUNT(*) AS total_line_items,
        COUNT(DISTINCT customer_key) AS total_unique_customers,
        SUM(quantity) AS total_units_sold,
        ROUND(SUM(shipping_cost), 2) AS total_shipping_cost,
        ROUND((SUM(shipping_cost) / SUM(sales)) * 100.0, 2) AS shipping_burden_pct,
        ROUND(SUM(gross_sales) - SUM(sales), 2) AS total_discount_concession,
        ROUND((SUM(gross_sales) - SUM(sales)) / SUM(gross_sales) * 100.0, 2) AS average_effective_discount_pct,
        ROUND(AVG(lead_time_days), 2) AS avg_fulfillment_lead_time_days
    FROM fact_orders
),
return_metrics AS (
    SELECT
        COUNT(DISTINCT order_id) AS total_returned_orders,
        COUNT(*) AS total_returned_line_items,
        ROUND(SUM(sales), 2) AS total_sales_exposed_to_returns,
        ROUND(SUM(profit), 2) AS total_profit_exposed_to_returns
    FROM fact_orders
    WHERE is_returned = 1
)
SELECT
    s.total_gross_merchandise_value AS total_sales_usd,
    s.total_net_profit AS net_profit_usd,
    s.overall_profit_margin_pct AS profit_margin_pct,
    s.total_distinct_orders,
    s.total_line_items,
    s.total_unique_customers,
    s.total_units_sold,
    ROUND(s.total_gross_merchandise_value / s.total_distinct_orders, 2) AS aov_per_order_usd,
    ROUND(s.total_gross_merchandise_value / s.total_line_items, 2) AS average_line_item_value_usd,
    ROUND(s.total_units_sold * 1.0 / s.total_distinct_orders, 2) AS avg_units_per_order,
    s.total_shipping_cost,
    s.shipping_burden_pct,
    s.total_discount_concession,
    s.average_effective_discount_pct,
    s.avg_fulfillment_lead_time_days,
    
    -- Returns Analysis with Explicit Denominators
    r.total_returned_orders,
    ROUND((r.total_returned_orders * 100.0) / s.total_distinct_orders, 2) AS order_return_rate_pct, -- Denominator: Distinct Orders
    r.total_returned_line_items,
    ROUND((r.total_returned_line_items * 100.0) / s.total_line_items, 2) AS line_item_return_rate_pct, -- Denominator: Line Items
    r.total_sales_exposed_to_returns,
    ROUND((r.total_sales_exposed_to_returns * 100.0) / s.total_gross_merchandise_value, 2) AS sales_at_return_risk_pct -- Denominator: Total GMV
FROM summary_metrics s
CROSS JOIN return_metrics r;
