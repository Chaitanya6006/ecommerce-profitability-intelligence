-- ============================================================================
-- 08_shipping_regional_analysis.sql
-- Logistics, Fulfillment Performance & Regional Supply Chain Economics
-- Evaluates carrier SLA adherence, freight margin drag, and geographic profitability
-- 
-- DATA LIMITATIONS:
-- 1. Postal codes are natively present only for US transactions, whereas international
--    regions rely on Market, Region, Country, and State geographic hierarchies.
-- 2. Reverse carrier freight fees are not recorded in raw data, so return drag is
--    measured by forfeited sales and standard outward shipping costs incurred.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. Carrier Shipping Mode Efficiency & Economics
-- ----------------------------------------------------------------------------
SELECT
    s.ship_mode,
    COUNT(DISTINCT f.order_id) AS distinct_orders,
    COUNT(*) AS total_line_items,
    ROUND(SUM(f.sales), 2) AS total_sales_usd,
    ROUND(SUM(f.shipping_cost), 2) AS total_shipping_cost_usd,
    ROUND((SUM(f.shipping_cost) / NULLIF(SUM(f.sales), 0)) * 100.0, 2) AS shipping_burden_pct,
    ROUND(AVG(f.shipping_cost), 2) AS avg_shipping_cost_per_item,
    ROUND(AVG(f.lead_time_days), 2) AS avg_fulfillment_lead_time_days,
    MIN(f.lead_time_days) AS min_lead_time_days,
    MAX(f.lead_time_days) AS max_lead_time_days,
    ROUND(SUM(f.profit), 2) AS total_profit_usd,
    ROUND((SUM(f.profit) / NULLIF(SUM(f.sales), 0)) * 100.0, 2) AS net_profit_margin_pct,
    ROUND((SUM(f.is_returned) * 100.0) / COUNT(*), 2) AS return_rate_pct
FROM fact_orders f
JOIN dim_shipping_mode s ON f.shipping_mode_key = s.shipping_mode_key
GROUP BY s.ship_mode
ORDER BY avg_fulfillment_lead_time_days ASC;

-- ----------------------------------------------------------------------------
-- 2. Regional & Market Supply Chain Footprint
-- ----------------------------------------------------------------------------
SELECT
    g.market,
    g.region,
    COUNT(DISTINCT g.country) AS country_count,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.sales), 2) AS total_sales_usd,
    ROUND(SUM(f.shipping_cost), 2) AS total_shipping_cost_usd,
    ROUND((SUM(f.shipping_cost) / NULLIF(SUM(f.sales), 0)) * 100.0, 2) AS shipping_ratio_pct,
    ROUND(SUM(f.profit), 2) AS total_net_profit_usd,
    ROUND((SUM(f.profit) / NULLIF(SUM(f.sales), 0)) * 100.0, 2) AS regional_margin_pct,
    ROUND(AVG(f.lead_time_days), 2) AS avg_fulfillment_days,
    ROUND((SUM(f.is_returned) * 100.0) / COUNT(*), 2) AS line_return_rate_pct
FROM fact_orders f
JOIN dim_geography g ON f.geography_key = g.geography_key
GROUP BY g.market, g.region
ORDER BY total_sales_usd DESC;

-- ----------------------------------------------------------------------------
-- 3. Fulfillment Lead Time SLA Distribution
-- ----------------------------------------------------------------------------
WITH lead_time_buckets AS (
    SELECT
        order_id,
        lead_time_days,
        sales,
        profit,
        is_returned,
        CASE
            WHEN lead_time_days = 0 THEN '0 Days (Same Day Dispatch)'
            WHEN lead_time_days BETWEEN 1 AND 2 THEN '1 - 2 Days (Expedited)'
            WHEN lead_time_days BETWEEN 3 AND 5 THEN '3 - 5 Days (Standard SLA)'
            ELSE '> 5 Days (Delayed Dispatch)'
        END AS sla_bracket
    FROM fact_orders
)
SELECT
    sla_bracket,
    COUNT(DISTINCT order_id) AS distinct_orders,
    COUNT(*) AS total_line_items,
    ROUND((COUNT(*) * 100.0) / (SELECT COUNT(*) FROM fact_orders), 2) AS line_item_share_pct,
    ROUND(SUM(sales), 2) AS total_sales_usd,
    ROUND(SUM(profit), 2) AS total_profit_usd,
    ROUND((SUM(profit) / NULLIF(SUM(sales), 0)) * 100.0, 2) AS profit_margin_pct,
    ROUND((SUM(is_returned) * 100.0) / COUNT(*), 2) AS return_rate_pct
FROM lead_time_buckets
GROUP BY sla_bracket
ORDER BY MIN(lead_time_days) ASC;
