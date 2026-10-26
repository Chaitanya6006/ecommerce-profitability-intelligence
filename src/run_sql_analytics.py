"""
Automated SQL Analytics Suite Runner.
Executes analytical SQL queries against the star schema warehouse, validates results,
and exports structured business intelligence datasets to data/processed/analytics/.
"""

import sqlite3
import pandas as pd
from pathlib import Path

from src.config import SQLITE_DB_PATH, SQL_DIR, PROCESSED_DATA_DIR
from src.db_connector import get_sqlite_connection

ANALYTICS_OUTPUT_DIR = PROCESSED_DATA_DIR / "analytics"


def split_sql_queries(sql_content: str) -> list[str]:
    """
    Splits multi-query SQL scripts by semicolon while stripping line comments beforehand.
    """
    clean_lines = [line for line in sql_content.splitlines() if not line.strip().startswith("--")]
    stripped_sql = "\n".join(clean_lines)
    raw_statements = stripped_sql.split(";")
    valid_queries = []
    for stmt in raw_statements:
        cleaned = stmt.strip()
        if cleaned:
            valid_queries.append(cleaned)
    return valid_queries


def run_analytics_suite() -> dict[str, pd.DataFrame]:
    """
    Executes the comprehensive analytical SQL suite and exports results.
    """
    ANALYTICS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = get_sqlite_connection()
    results = {}

    print("\n" + "=" * 70)
    print("EXECUTING ADVANCED SQL ANALYTICS SUITE")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # 1. Executive Business KPIs (sql/02_executive_kpis.sql)
    # -------------------------------------------------------------------------
    print("\n[1/7] Running Executive Business KPIs (sql/02_executive_kpis.sql)...")
    sql_kpi = (SQL_DIR / "02_executive_kpis.sql").read_text(encoding="utf-8")
    df_kpis = pd.read_sql_query(sql_kpi, conn)
    kpi_file = ANALYTICS_OUTPUT_DIR / "executive_kpis.csv"
    df_kpis.to_csv(kpi_file, index=False)
    results["executive_kpis"] = df_kpis

    kpi_row = df_kpis.iloc[0]
    print(f"  * Gross Merchandise Value: ${kpi_row['total_sales_usd']:,.2f}")
    print(f"  * Total Net Profit:        ${kpi_row['net_profit_usd']:,.2f} ({kpi_row['profit_margin_pct']}% margin)")
    print(f"  * Distinct Orders:         {kpi_row['total_distinct_orders']:,} (AOV: ${kpi_row['aov_per_order_usd']:,.2f})")
    print(f"  * Order Return Rate:       {kpi_row['order_return_rate_pct']}% (Denominator: {kpi_row['total_distinct_orders']:,} orders)")
    print(f"  * Total Line Items:        {kpi_row['total_line_items']:,}")
    print(f"  -> Exported to: {kpi_file.name}")

    # -------------------------------------------------------------------------
    # 2. Product & Category Profitability (sql/03_product_category_profitability.sql)
    # -------------------------------------------------------------------------
    print("\n[2/7] Running Product & Category Profitability (sql/03_product_category_profitability.sql)...")
    cat_queries = split_sql_queries((SQL_DIR / "03_product_category_profitability.sql").read_text(encoding="utf-8"))
    
    # Query 1: Category & Sub-Category
    df_cat = pd.read_sql_query(cat_queries[0], conn)
    cat_file = ANALYTICS_OUTPUT_DIR / "category_profitability.csv"
    df_cat.to_csv(cat_file, index=False)
    results["category_profitability"] = df_cat
    print(f"  * Sub-Categories Analyzed: {len(df_cat)} rows")
    print(f"  -> Exported to: {cat_file.name}")

    # Query 2: Margin Bleeders
    df_bleeders = pd.read_sql_query(cat_queries[1], conn)
    bleeders_file = ANALYTICS_OUTPUT_DIR / "top_margin_bleeders.csv"
    df_bleeders.to_csv(bleeders_file, index=False)
    results["top_margin_bleeders"] = df_bleeders
    print(f"  * High-Volume Bleeders:   {len(df_bleeders)} SKUs")
    print(f"  -> Exported to: {bleeders_file.name}")

    # -------------------------------------------------------------------------
    # 3. Discount Analysis (sql/04_discount_analysis.sql)
    # -------------------------------------------------------------------------
    print("\n[3/7] Running Discount Analysis (sql/04_discount_analysis.sql)...")
    disc_queries = split_sql_queries((SQL_DIR / "04_discount_analysis.sql").read_text(encoding="utf-8"))
    
    # Query 1: Discount Tiers
    df_disc = pd.read_sql_query(disc_queries[0], conn)
    disc_file = ANALYTICS_OUTPUT_DIR / "discount_tier_analysis.csv"
    df_disc.to_csv(disc_file, index=False)
    results["discount_tiers"] = df_disc
    for _, r in df_disc.iterrows():
        print(f"  * Tier '{r['discount_tier']}': Sales=${r['net_sales_usd']:,.0f}, Margin={r['net_profit_margin_pct']}%, Unprofitable Lines={r['unprofitable_order_lines_pct']}%")
    print(f"  -> Exported to: {disc_file.name}")

    # Query 2: Category Discount Elasticity
    df_cat_disc = pd.read_sql_query(disc_queries[1], conn)
    cat_disc_file = ANALYTICS_OUTPUT_DIR / "category_discount_elasticity.csv"
    df_cat_disc.to_csv(cat_disc_file, index=False)
    results["category_discount_elasticity"] = df_cat_disc
    print(f"  -> Exported to: {cat_disc_file.name}")

    # -------------------------------------------------------------------------
    # 4. Customer RFM Segmentation (sql/05_customer_rfm.sql)
    # -------------------------------------------------------------------------
    print("\n[4/7] Running Customer RFM Segmentation (sql/05_customer_rfm.sql)...")
    sql_rfm = (SQL_DIR / "05_customer_rfm.sql").read_text(encoding="utf-8")
    df_rfm = pd.read_sql_query(sql_rfm, conn)
    rfm_file = ANALYTICS_OUTPUT_DIR / "customer_rfm_segments.csv"
    df_rfm.to_csv(rfm_file, index=False)
    results["customer_rfm"] = df_rfm
    for _, r in df_rfm.iterrows():
        print(f"  * Persona '{r['rfm_segment']}': {r['customer_count']:,} customers ({r['customer_share_pct']}%), Total Profit=${r['total_segment_profit_usd']:,.0f}")
    print(f"  -> Exported to: {rfm_file.name}")

    # -------------------------------------------------------------------------
    # 5. Customer Cohort Retention (sql/06_customer_cohorts.sql)
    # -------------------------------------------------------------------------
    print("\n[5/7] Running Customer Cohort Retention (sql/06_customer_cohorts.sql)...")
    cohort_queries = split_sql_queries((SQL_DIR / "06_customer_cohorts.sql").read_text(encoding="utf-8"))
    
    # Query 1: Annual Cohort Retention
    df_annual_cohort = pd.read_sql_query(cohort_queries[0], conn)
    annual_cohort_file = ANALYTICS_OUTPUT_DIR / "cohort_retention_annual.csv"
    df_annual_cohort.to_csv(annual_cohort_file, index=False)
    results["cohort_annual"] = df_annual_cohort
    print(f"  -> Exported to: {annual_cohort_file.name}")

    # Query 2: Monthly Cohort Retention
    df_monthly_cohort = pd.read_sql_query(cohort_queries[1], conn)
    monthly_cohort_file = ANALYTICS_OUTPUT_DIR / "cohort_retention_monthly.csv"
    df_monthly_cohort.to_csv(monthly_cohort_file, index=False)
    results["cohort_monthly"] = df_monthly_cohort
    print(f"  -> Exported to: {monthly_cohort_file.name}")

    # -------------------------------------------------------------------------
    # 6. Window Function Analysis (sql/07_window_functions.sql)
    # -------------------------------------------------------------------------
    print("\n[6/7] Running Window Function Analysis (sql/07_window_functions.sql)...")
    win_queries = split_sql_queries((SQL_DIR / "07_window_functions.sql").read_text(encoding="utf-8"))
    
    # Query 2: Monthly Pacing & MoM Growth
    df_monthly_pacing = pd.read_sql_query(win_queries[1], conn)
    pacing_file = ANALYTICS_OUTPUT_DIR / "monthly_sales_growth.csv"
    df_monthly_pacing.to_csv(pacing_file, index=False)
    results["monthly_growth"] = df_monthly_pacing
    print(f"  * Monthly Time Series:    {len(df_monthly_pacing)} months (2012-01 to 2015-12)")
    print(f"  -> Exported to: {pacing_file.name}")

    # Query 3: Order Basket Quartiles
    df_baskets = pd.read_sql_query(win_queries[2], conn)
    baskets_file = ANALYTICS_OUTPUT_DIR / "order_basket_quartiles.csv"
    df_baskets.to_csv(baskets_file, index=False)
    results["order_baskets"] = df_baskets
    print(f"  -> Exported to: {baskets_file.name}")

    # -------------------------------------------------------------------------
    # 7. Shipping & Regional Logistics (sql/08_shipping_regional_analysis.sql)
    # -------------------------------------------------------------------------
    print("\n[7/7] Running Logistics & Regional Analysis (sql/08_shipping_regional_analysis.sql)...")
    ship_queries = split_sql_queries((SQL_DIR / "08_shipping_regional_analysis.sql").read_text(encoding="utf-8"))
    
    # Query 1: Shipping Modes
    df_ship_modes = pd.read_sql_query(ship_queries[0], conn)
    ship_modes_file = ANALYTICS_OUTPUT_DIR / "shipping_mode_performance.csv"
    df_ship_modes.to_csv(ship_modes_file, index=False)
    results["shipping_modes"] = df_ship_modes
    print(f"  -> Exported to: {ship_modes_file.name}")

    # Query 2: Regional Profitability
    df_regions = pd.read_sql_query(ship_queries[1], conn)
    regions_file = ANALYTICS_OUTPUT_DIR / "regional_profitability.csv"
    df_regions.to_csv(regions_file, index=False)
    results["regional_profitability"] = df_regions
    print(f"  -> Exported to: {regions_file.name}")

    # -------------------------------------------------------------------------
    # Verification: Execute 09_data_reconciliation.sql
    # -------------------------------------------------------------------------
    print("\n" + "-" * 70)
    print("VERIFYING ANALYTICAL DATA RECONCILIATION")
    print("-" * 70)
    recon_queries = split_sql_queries((SQL_DIR / "09_data_reconciliation.sql").read_text(encoding="utf-8"))
    for idx, q in enumerate(recon_queries, start=1):
        df_recon = pd.read_sql_query(q, conn)
        status = df_recon.iloc[0]["test_status"]
        test_name = df_recon.iloc[0]["test_name"]
        assert status == "PASS", f"Reconciliation Failed on Test {idx}: {test_name}"
        print(f"  [PASS] Test {idx}: {test_name}")

    conn.close()
    print("\n" + "=" * 70)
    print("[SUCCESS] All 7 Analytical SQL Modules Executed & Verified!")
    print(f"Selected results exported to: {ANALYTICS_OUTPUT_DIR.resolve()}")
    print("=" * 70 + "\n")

    return results


if __name__ == "__main__":
    run_analytics_suite()
