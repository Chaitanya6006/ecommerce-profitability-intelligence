-- ============================================================================
-- 09_data_reconciliation.sql
-- Automated Analytical Quality Gate & Data Reconciliation Assertions
-- Verifies zero row multiplication, foreign key integrity, and financial balance
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Test 1: Enterprise Totals Reconciliation against Raw Verified Benchmarks
-- Expected: Exactly $12,642,501.91 Sales, $1,467,457.29 Profit, 51,290 Rows
-- ----------------------------------------------------------------------------
SELECT
    'Reconciliation Test 1: Enterprise Financials' AS test_name,
    COUNT(*) AS fact_rows,
    51290 AS expected_rows,
    ROUND(SUM(sales), 2) AS fact_sales,
    12642501.91 AS expected_sales,
    ROUND(ABS(ROUND(SUM(sales), 2) - 12642501.91), 2) AS sales_discrepancy,
    ROUND(SUM(profit), 2) AS fact_profit,
    1467457.29 AS expected_profit,
    ROUND(ABS(ROUND(SUM(profit), 2) - 1467457.29), 2) AS profit_discrepancy,
    CASE
        WHEN COUNT(*) = 51290
         AND ROUND(ABS(ROUND(SUM(sales), 2) - 12642501.91), 2) < 0.05
         AND ROUND(ABS(ROUND(SUM(profit), 2) - 1467457.29), 2) < 0.05
        THEN 'PASS'
        ELSE 'FAIL'
    END AS test_status
FROM fact_orders;

-- ----------------------------------------------------------------------------
-- Test 2: Unintended Row Multiplication Audit (Star Schema Join Integrity)
-- Ensure multi-table dimensional joins produce exactly 51,290 rows without duplication
-- ----------------------------------------------------------------------------
WITH joined_orders AS (
    SELECT
        f.row_id,
        c.customer_id,
        p.product_id,
        g.city,
        s.ship_mode,
        d.full_date
    FROM fact_orders f
    JOIN dim_customers c ON f.customer_key = c.customer_key
    JOIN dim_products p ON f.product_key = p.product_key
    JOIN dim_geography g ON f.geography_key = g.geography_key
    JOIN dim_shipping_mode s ON f.shipping_mode_key = s.shipping_mode_key
    JOIN dim_date d ON f.order_date_key = d.date_key
)
SELECT
    'Reconciliation Test 2: Join Cardinality' AS test_name,
    COUNT(*) AS joined_row_count,
    COUNT(DISTINCT row_id) AS distinct_row_ids,
    CASE
        WHEN COUNT(*) = 51290 AND COUNT(DISTINCT row_id) = 51290
        THEN 'PASS'
        ELSE 'FAIL'
    END AS test_status
FROM joined_orders;

-- ----------------------------------------------------------------------------
-- Test 3: Returns Double-Counting & Match Rate Audit
-- ----------------------------------------------------------------------------
WITH return_validation AS (
    SELECT
        COUNT(DISTINCT r.order_id) AS raw_returned_orders,
        COUNT(DISTINCT f.order_id) AS matched_orders,
        SUM(f.is_returned) AS total_returned_lines
    FROM fact_returns r
    LEFT JOIN fact_orders f ON r.order_id = f.order_id
)
SELECT
    'Reconciliation Test 3: Returns Isolation' AS test_name,
    raw_returned_orders,
    matched_orders,
    total_returned_lines,
    CASE
        WHEN raw_returned_orders = 1079 AND matched_orders = 1079
        THEN 'PASS'
        ELSE 'FAIL'
    END AS test_status
FROM return_validation;

-- ----------------------------------------------------------------------------
-- Test 4: Financial Equation Mathematical Balance
-- Evaluates COGS = Sales - Profit - Shipping Cost on every single record
-- ----------------------------------------------------------------------------
SELECT
    'Reconciliation Test 4: Unit Economics Formula' AS test_name,
    COUNT(*) AS total_rows_audited,
    SUM(CASE WHEN ABS(cogs - (sales - profit - shipping_cost)) > 0.05 THEN 1 ELSE 0 END) AS formula_violations,
    CASE
        WHEN SUM(CASE WHEN ABS(cogs - (sales - profit - shipping_cost)) > 0.05 THEN 1 ELSE 0 END) = 0
        THEN 'PASS'
        ELSE 'FAIL'
    END AS test_status
FROM fact_orders;
