-- ============================================================================
-- E-Commerce Profitability Intelligence Platform
-- DDL Schema Definition (ANSI SQL / SQLite / PostgreSQL Compatible)
-- Star Schema Architecture for High-Performance Analytical Querying
-- ============================================================================

-- Drop tables if re-initializing (in reverse dependency order)
DROP TABLE IF EXISTS fact_returns;
DROP TABLE IF EXISTS fact_orders;
DROP TABLE IF EXISTS dim_shipping_mode;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_geography;
DROP TABLE IF EXISTS dim_products;
DROP TABLE IF EXISTS dim_customers;

-- ----------------------------------------------------------------------------
-- 1. Dimension: Customers
-- ----------------------------------------------------------------------------
CREATE TABLE dim_customers (
    customer_key INTEGER PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL UNIQUE,
    customer_name VARCHAR(150) NOT NULL,
    segment VARCHAR(50) NOT NULL
);

-- ----------------------------------------------------------------------------
-- 2. Dimension: Products
-- ----------------------------------------------------------------------------
CREATE TABLE dim_products (
    product_key INTEGER PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL UNIQUE,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    sub_category VARCHAR(50) NOT NULL
);

-- ----------------------------------------------------------------------------
-- 3. Dimension: Geography
-- ----------------------------------------------------------------------------
CREATE TABLE dim_geography (
    geography_key INTEGER PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    market VARCHAR(50) NOT NULL,
    postal_code VARCHAR(30) NOT NULL
);

-- ----------------------------------------------------------------------------
-- 4. Dimension: Date (Calendar Hierarchy)
-- ----------------------------------------------------------------------------
CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,      -- Format: YYYYMMDD
    full_date DATE NOT NULL UNIQUE,
    day_of_month INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    quarter INTEGER NOT NULL,
    year INTEGER NOT NULL,
    day_of_week VARCHAR(15) NOT NULL,
    is_weekend INTEGER NOT NULL        -- 1 = Weekend, 0 = Weekday
);

-- ----------------------------------------------------------------------------
-- 5. Dimension: Shipping Mode
-- ----------------------------------------------------------------------------
CREATE TABLE dim_shipping_mode (
    shipping_mode_key INTEGER PRIMARY KEY,
    ship_mode VARCHAR(50) NOT NULL UNIQUE
);

-- ----------------------------------------------------------------------------
-- 6. Fact Table: Orders (Granularity = 1 row per order line item)
-- ----------------------------------------------------------------------------
CREATE TABLE fact_orders (
    row_id INTEGER PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    customer_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    geography_key INTEGER NOT NULL,
    order_date_key INTEGER NOT NULL,
    ship_date_key INTEGER NOT NULL,
    shipping_mode_key INTEGER NOT NULL,
    
    -- Transactional Measures
    sales NUMERIC(12, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    discount NUMERIC(5, 4) NOT NULL,
    profit NUMERIC(12, 2) NOT NULL,
    shipping_cost NUMERIC(12, 2) NOT NULL,
    
    -- Derived Unit Economics Measures
    gross_sales NUMERIC(12, 2) NOT NULL,
    discount_amount NUMERIC(12, 2) NOT NULL,
    cogs NUMERIC(12, 2) NOT NULL,
    lead_time_days INTEGER NOT NULL,
    order_priority VARCHAR(20) NOT NULL,
    is_returned INTEGER NOT NULL DEFAULT 0,  -- 1 = Returned, 0 = Retained
    
    FOREIGN KEY (customer_key) REFERENCES dim_customers(customer_key),
    FOREIGN KEY (product_key) REFERENCES dim_products(product_key),
    FOREIGN KEY (geography_key) REFERENCES dim_geography(geography_key),
    FOREIGN KEY (order_date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (ship_date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (shipping_mode_key) REFERENCES dim_shipping_mode(shipping_mode_key)
);

-- ----------------------------------------------------------------------------
-- 7. Fact Table: Returns
-- ----------------------------------------------------------------------------
CREATE TABLE fact_returns (
    return_id INTEGER PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    returned_flag VARCHAR(10) NOT NULL DEFAULT 'Yes'
);

-- ----------------------------------------------------------------------------
-- Indexes for Analytical Query Performance
-- ----------------------------------------------------------------------------
CREATE INDEX idx_orders_customer ON fact_orders(customer_key);
CREATE INDEX idx_orders_product ON fact_orders(product_key);
CREATE INDEX idx_orders_geography ON fact_orders(geography_key);
CREATE INDEX idx_orders_order_date ON fact_orders(order_date_key);
CREATE INDEX idx_orders_order_id ON fact_orders(order_id);
CREATE INDEX idx_orders_discount ON fact_orders(discount);
CREATE INDEX idx_orders_profit ON fact_orders(profit);
CREATE INDEX idx_returns_order_id ON fact_returns(order_id);
