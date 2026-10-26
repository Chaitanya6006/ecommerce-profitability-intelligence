-- ============================================================================
-- E-Commerce Profitability Intelligence Platform
-- PostgreSQL Enterprise DDL Specification
-- ============================================================================

-- Create dedicated analytics schema
CREATE SCHEMA IF NOT EXISTS analytics;
SET search_path TO analytics, public;

-- Drop existing tables
DROP TABLE IF EXISTS analytics.fact_returns CASCADE;
DROP TABLE IF EXISTS analytics.fact_orders CASCADE;
DROP TABLE IF EXISTS analytics.dim_shipping_mode CASCADE;
DROP TABLE IF EXISTS analytics.dim_date CASCADE;
DROP TABLE IF EXISTS analytics.dim_geography CASCADE;
DROP TABLE IF EXISTS analytics.dim_products CASCADE;
DROP TABLE IF EXISTS analytics.dim_customers CASCADE;

-- ----------------------------------------------------------------------------
-- 1. Dimension: Customers
-- ----------------------------------------------------------------------------
CREATE TABLE analytics.dim_customers (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL UNIQUE,
    customer_name VARCHAR(150) NOT NULL,
    segment VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 2. Dimension: Products
-- ----------------------------------------------------------------------------
CREATE TABLE analytics.dim_products (
    product_key SERIAL PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL UNIQUE,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    sub_category VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 3. Dimension: Geography
-- ----------------------------------------------------------------------------
CREATE TABLE analytics.dim_geography (
    geography_key SERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    market VARCHAR(50) NOT NULL,
    postal_code VARCHAR(30) NOT NULL DEFAULT 'UNKNOWN',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_geography UNIQUE (city, state, country, postal_code)
);

-- ----------------------------------------------------------------------------
-- 4. Dimension: Date
-- ----------------------------------------------------------------------------
CREATE TABLE analytics.dim_date (
    date_key INTEGER PRIMARY KEY,      -- Format: YYYYMMDD
    full_date DATE NOT NULL UNIQUE,
    day_of_month SMALLINT NOT NULL,
    month SMALLINT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    quarter SMALLINT NOT NULL,
    year SMALLINT NOT NULL,
    day_of_week VARCHAR(15) NOT NULL,
    is_weekend SMALLINT NOT NULL CHECK (is_weekend IN (0, 1))
);

-- ----------------------------------------------------------------------------
-- 5. Dimension: Shipping Mode
-- ----------------------------------------------------------------------------
CREATE TABLE analytics.dim_shipping_mode (
    shipping_mode_key SERIAL PRIMARY KEY,
    ship_mode VARCHAR(50) NOT NULL UNIQUE
);

-- ----------------------------------------------------------------------------
-- 6. Fact Table: Orders
-- ----------------------------------------------------------------------------
CREATE TABLE analytics.fact_orders (
    row_id INTEGER PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    customer_key INTEGER NOT NULL REFERENCES analytics.dim_customers(customer_key),
    product_key INTEGER NOT NULL REFERENCES analytics.dim_products(product_key),
    geography_key INTEGER NOT NULL REFERENCES analytics.dim_geography(geography_key),
    order_date_key INTEGER NOT NULL REFERENCES analytics.dim_date(date_key),
    ship_date_key INTEGER NOT NULL REFERENCES analytics.dim_date(date_key),
    shipping_mode_key INTEGER NOT NULL REFERENCES analytics.dim_shipping_mode(shipping_mode_key),
    
    -- Financial Measures
    sales NUMERIC(12, 2) NOT NULL CHECK (sales >= 0),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    discount NUMERIC(5, 4) NOT NULL CHECK (discount >= 0.0 AND discount <= 1.0),
    profit NUMERIC(12, 2) NOT NULL,
    shipping_cost NUMERIC(12, 2) NOT NULL CHECK (shipping_cost >= 0),
    
    -- Derived Metrics
    gross_sales NUMERIC(12, 2) NOT NULL,
    discount_amount NUMERIC(12, 2) NOT NULL,
    cogs NUMERIC(12, 2) NOT NULL,
    lead_time_days INTEGER NOT NULL CHECK (lead_time_days >= 0),
    order_priority VARCHAR(20) NOT NULL,
    is_returned SMALLINT NOT NULL DEFAULT 0 CHECK (is_returned IN (0, 1)),
    
    loaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 7. Fact Table: Returns
-- ----------------------------------------------------------------------------
CREATE TABLE analytics.fact_returns (
    return_id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    returned_flag VARCHAR(10) NOT NULL DEFAULT 'Yes'
);

-- ----------------------------------------------------------------------------
-- B-Tree Performance Indexes
-- ----------------------------------------------------------------------------
CREATE INDEX idx_pg_orders_customer ON analytics.fact_orders(customer_key);
CREATE INDEX idx_pg_orders_product ON analytics.fact_orders(product_key);
CREATE INDEX idx_pg_orders_geography ON analytics.fact_orders(geography_key);
CREATE INDEX idx_pg_orders_order_date ON analytics.fact_orders(order_date_key);
CREATE INDEX idx_pg_orders_order_id ON analytics.fact_orders(order_id);
CREATE INDEX idx_pg_orders_discount ON analytics.fact_orders(discount);
CREATE INDEX idx_pg_orders_profit ON analytics.fact_orders(profit);
CREATE INDEX idx_pg_returns_order_id ON analytics.fact_returns(order_id);
