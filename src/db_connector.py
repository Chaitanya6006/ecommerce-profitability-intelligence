"""
Database ETL & Pipeline Engine.
Builds and populates the SQLite analytics database (with full PostgreSQL compatibility).
Transforms raw denormalized transactions into an optimized Star Schema.
Performs rigorous data integrity reconciliation assertions.
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from src.config import SQLITE_DB_PATH, SQL_DIR, PROCESSED_DATA_DIR
from src.data_loader import load_raw_data


def get_sqlite_connection() -> sqlite3.Connection:
    """Returns a connection to the SQLite database with Foreign Key support enabled."""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def initialize_schema(conn: sqlite3.Connection) -> None:
    """Executes the DDL schema definition script."""
    ddl_path = SQL_DIR / "01_schema_ddl.sql"
    with open(ddl_path, "r", encoding="utf-8") as f:
        ddl_script = f.read()
    
    cursor = conn.cursor()
    cursor.executescript(ddl_script)
    conn.commit()
    print("[OK] Initialized database schema successfully.")


def build_and_populate_star_schema() -> None:
    """
    Orchestrates extraction, transformation, dimensional modeling, loading,
    and post-load reconciliation assertions.
    """
    print("\n--- Starting Data Warehouse ETL Pipeline ---")
    df_orders, df_returns = load_raw_data()

    # Pre-cleaning and date standardization
    df_orders["Order Date Clean"] = pd.to_datetime(df_orders["Order Date"])
    df_orders["Ship Date Clean"] = pd.to_datetime(df_orders["Ship Date"])
    df_orders["Postal Code Clean"] = (
        df_orders["Postal Code"]
        .astype(object)
        .fillna("UNKNOWN")
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
    )

    conn = get_sqlite_connection()
    initialize_schema(conn)

    # -------------------------------------------------------------------------
    # 1. Build & Populate Dimension: Customers
    # -------------------------------------------------------------------------
    print("Building dim_customers...")
    # Deduplicate by Customer ID (take latest name/segment if conflict)
    dim_cust = (
        df_orders[["Customer ID", "Customer Name", "Segment"]]
        .drop_duplicates(subset=["Customer ID"])
        .reset_index(drop=True)
    )
    dim_cust["customer_key"] = dim_cust.index + 1
    dim_cust = dim_cust.rename(
        columns={
            "Customer ID": "customer_id",
            "Customer Name": "customer_name",
            "Segment": "segment",
        }
    )[["customer_key", "customer_id", "customer_name", "segment"]]
    dim_cust.to_sql("dim_customers", conn, if_exists="append", index=False)
    print(f"  -> dim_customers loaded: {len(dim_cust):,} records")

    # -------------------------------------------------------------------------
    # 2. Build & Populate Dimension: Products
    # -------------------------------------------------------------------------
    print("Building dim_products...")
    dim_prod = (
        df_orders[["Product ID", "Product Name", "Category", "Sub-Category"]]
        .drop_duplicates(subset=["Product ID"])
        .reset_index(drop=True)
    )
    dim_prod["product_key"] = dim_prod.index + 1
    dim_prod = dim_prod.rename(
        columns={
            "Product ID": "product_id",
            "Product Name": "product_name",
            "Category": "category",
            "Sub-Category": "sub_category",
        }
    )[["product_key", "product_id", "product_name", "category", "sub_category"]]
    dim_prod.to_sql("dim_products", conn, if_exists="append", index=False)
    print(f"  -> dim_products loaded: {len(dim_prod):,} records")

    # -------------------------------------------------------------------------
    # 3. Build & Populate Dimension: Geography
    # -------------------------------------------------------------------------
    print("Building dim_geography...")
    dim_geo = (
        df_orders[["City", "State", "Country", "Region", "Market", "Postal Code Clean"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    dim_geo["geography_key"] = dim_geo.index + 1
    dim_geo = dim_geo.rename(
        columns={
            "City": "city",
            "State": "state",
            "Country": "country",
            "Region": "region",
            "Market": "market",
            "Postal Code Clean": "postal_code",
        }
    )[["geography_key", "city", "state", "country", "region", "market", "postal_code"]]
    dim_geo.to_sql("dim_geography", conn, if_exists="append", index=False)
    print(f"  -> dim_geography loaded: {len(dim_geo):,} records")

    # -------------------------------------------------------------------------
    # 4. Build & Populate Dimension: Shipping Mode
    # -------------------------------------------------------------------------
    print("Building dim_shipping_mode...")
    dim_ship = (
        df_orders[["Ship Mode"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    dim_ship["shipping_mode_key"] = dim_ship.index + 1
    dim_ship = dim_ship.rename(columns={"Ship Mode": "ship_mode"})[
        ["shipping_mode_key", "ship_mode"]
    ]
    dim_ship.to_sql("dim_shipping_mode", conn, if_exists="append", index=False)
    print(f"  -> dim_shipping_mode loaded: {len(dim_ship):,} records")

    # -------------------------------------------------------------------------
    # 5. Build & Populate Dimension: Date
    # -------------------------------------------------------------------------
    print("Building dim_date...")
    min_date = min(df_orders["Order Date Clean"].min(), df_orders["Ship Date Clean"].min())
    max_date = max(df_orders["Order Date Clean"].max(), df_orders["Ship Date Clean"].max())
    date_range = pd.date_range(start=min_date, end=max_date, freq="D")
    
    dim_date = pd.DataFrame({"full_date": date_range})
    dim_date["date_key"] = dim_date["full_date"].dt.strftime("%Y%m%d").astype(int)
    dim_date["day_of_month"] = dim_date["full_date"].dt.day
    dim_date["month"] = dim_date["full_date"].dt.month
    dim_date["month_name"] = dim_date["full_date"].dt.strftime("%B")
    dim_date["quarter"] = dim_date["full_date"].dt.quarter
    dim_date["year"] = dim_date["full_date"].dt.year
    dim_date["day_of_week"] = dim_date["full_date"].dt.strftime("%A")
    dim_date["is_weekend"] = dim_date["full_date"].dt.day_of_week.isin([5, 6]).astype(int)
    dim_date["full_date"] = dim_date["full_date"].dt.strftime("%Y-%m-%d")

    dim_date.to_sql("dim_date", conn, if_exists="append", index=False)
    print(f"  -> dim_date loaded: {len(dim_date):,} records")

    # -------------------------------------------------------------------------
    # 6. Build & Populate Fact Table: Returns
    # -------------------------------------------------------------------------
    print("Building fact_returns...")
    fact_returns = df_returns.copy()
    fact_returns["return_id"] = fact_returns.index + 1
    fact_returns = fact_returns.rename(
        columns={
            "Order ID": "order_id",
            "Region": "region",
            "Returned": "returned_flag",
        }
    )[["return_id", "order_id", "region", "returned_flag"]]
    fact_returns.to_sql("fact_returns", conn, if_exists="append", index=False)
    print(f"  -> fact_returns loaded: {len(fact_returns):,} records")

    # -------------------------------------------------------------------------
    # 7. Build & Populate Fact Table: Orders
    # -------------------------------------------------------------------------
    print("Transforming and populating fact_orders...")
    returned_orders_set = set(df_returns["Order ID"].unique())

    # Map Surrogate Foreign Keys
    cust_map = dict(zip(dim_cust["customer_id"], dim_cust["customer_key"]))
    prod_map = dict(zip(dim_prod["product_id"], dim_prod["product_key"]))
    ship_map = dict(zip(dim_ship["ship_mode"], dim_ship["shipping_mode_key"]))

    # Geography mapping via tuple key
    geo_lookup = {
        (r.city, r.state, r.country, r.region, r.market, r.postal_code): r.geography_key
        for r in dim_geo.itertuples(index=False)
    }

    fact = pd.DataFrame()
    fact["row_id"] = df_orders["Row ID"]
    fact["order_id"] = df_orders["Order ID"]
    fact["customer_key"] = df_orders["Customer ID"].map(cust_map)
    fact["product_key"] = df_orders["Product ID"].map(prod_map)

    # Map geography
    geo_keys = [
        geo_lookup.get((c, s, co, reg, m, p))
        for c, s, co, reg, m, p in zip(
            df_orders["City"],
            df_orders["State"],
            df_orders["Country"],
            df_orders["Region"],
            df_orders["Market"],
            df_orders["Postal Code Clean"],
        )
    ]
    fact["geography_key"] = geo_keys

    # Map Date Keys (YYYYMMDD)
    fact["order_date_key"] = df_orders["Order Date Clean"].dt.strftime("%Y%m%d").astype(int)
    fact["ship_date_key"] = df_orders["Ship Date Clean"].dt.strftime("%Y%m%d").astype(int)
    fact["shipping_mode_key"] = df_orders["Ship Mode"].map(ship_map)

    # Financial and Transactional Measures (preserve full precision)
    fact["sales"] = df_orders["Sales"]
    fact["quantity"] = df_orders["Quantity"]
    fact["discount"] = df_orders["Discount"]
    fact["profit"] = df_orders["Profit"]
    fact["shipping_cost"] = df_orders["Shipping Cost"]

    # Derived Unit Economics Measures
    fact["gross_sales"] = np.where(
        fact["discount"] < 1.0,
        (fact["sales"] / (1.0 - fact["discount"])),
        fact["sales"],
    ).round(2)
    fact["discount_amount"] = (fact["gross_sales"] - fact["sales"]).round(2)
    fact["cogs"] = (fact["sales"] - fact["profit"] - fact["shipping_cost"]).round(2)
    fact["lead_time_days"] = (
        df_orders["Ship Date Clean"] - df_orders["Order Date Clean"]
    ).dt.days
    fact["order_priority"] = df_orders["Order Priority"]
    fact["is_returned"] = df_orders["Order ID"].isin(returned_orders_set).astype(int)

    fact.to_sql("fact_orders", conn, if_exists="append", index=False)
    print(f"  -> fact_orders loaded: {len(fact):,} records")

    # -------------------------------------------------------------------------
    # 8. Automated Post-Load Reconciliation Audit
    # -------------------------------------------------------------------------
    print("\n--- Executing Post-Load Reconciliation Checks ---")
    cursor = conn.cursor()

    # Check 1: Row count assertion
    db_rows = cursor.execute("SELECT COUNT(*) FROM fact_orders;").fetchone()[0]
    assert db_rows == len(df_orders), f"Row count mismatch! Raw: {len(df_orders)}, DB: {db_rows}"
    print(f"[PASS] Fact Row Count: {db_rows:,} == Raw Rows: {len(df_orders):,}")

    # Check 2: Sales volume reconciliation
    db_sales = cursor.execute("SELECT ROUND(SUM(sales), 2) FROM fact_orders;").fetchone()[0]
    raw_sales = round(float(df_orders["Sales"].sum()), 2)
    diff_sales = abs(db_sales - raw_sales)
    assert diff_sales < 1.0, f"Sales total deviation exceeded threshold: {diff_sales}"
    print(f"[PASS] Reconciled Sales: DB=${db_sales:,.2f} vs Raw=${raw_sales:,.2f} (delta=${diff_sales:.2f})")

    # Check 3: Profit volume reconciliation
    db_profit = cursor.execute("SELECT ROUND(SUM(profit), 2) FROM fact_orders;").fetchone()[0]
    raw_profit = round(float(df_orders["Profit"].sum()), 2)
    diff_profit = abs(db_profit - raw_profit)
    assert diff_profit < 1.0, f"Profit total deviation exceeded threshold: {diff_profit}"
    print(f"[PASS] Reconciled Profit: DB=${db_profit:,.2f} vs Raw=${raw_profit:,.2f} (delta=${diff_profit:.2f})")

    # Check 4: Foreign Key Integrity Check
    fk_orphans = cursor.execute("""
        SELECT COUNT(*) FROM fact_orders f
        LEFT JOIN dim_customers c ON f.customer_key = c.customer_key
        WHERE c.customer_key IS NULL;
    """).fetchone()[0]
    assert fk_orphans == 0, f"Foreign key integrity failure: {fk_orphans} orphaned customers found."
    print(f"[PASS] Referential Integrity: 0 orphaned customer foreign keys.")

    # -------------------------------------------------------------------------
    # 9. Export Clean Processed Dimensional CSVs (for Power BI ingestion)
    # -------------------------------------------------------------------------
    print("\n--- Exporting Clean Processed Dimensional Tables to CSV ---")
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    tables = [
        "dim_customers",
        "dim_products",
        "dim_geography",
        "dim_date",
        "dim_shipping_mode",
        "fact_orders",
        "fact_returns",
    ]
    for tbl in tables:
        df_tbl = pd.read_sql_query(f"SELECT * FROM {tbl};", conn)
        out_csv = PROCESSED_DATA_DIR / f"{tbl}.csv"
        df_tbl.to_csv(out_csv, index=False)
        print(f"  -> Exported {tbl}: {len(df_tbl):,} rows -> {out_csv.name}")

    conn.close()
    print("\n[SUCCESS] SQLite Database fully built and validated at:")
    print(f"          {SQLITE_DB_PATH.resolve()} ({SQLITE_DB_PATH.stat().st_size:,} bytes)\n")


if __name__ == "__main__":
    build_and_populate_star_schema()
