"""
Data Profiling & Quality Assurance Script.
Performs comprehensive data auditing on raw Orders and Returns datasets.
Generates terminal diagnostic logs and exports a structured docs/data_profiling_report.md.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

from src.config import DOCS_DIR
from src.data_loader import load_raw_data


def run_profiling() -> str:
    """
    Executes automated data quality profiling and generates a Markdown report.
    """
    df_orders, df_returns = load_raw_data()
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    report_lines = []

    def p(line: str = "") -> None:
        print(line)
        report_lines.append(line)

    p("# Data Profiling & Quality Audit Report")
    p("## E-Commerce Profitability Intelligence Platform")
    p(f"**Generated:** Automatically by `src/data_profiler.py`\n")
    p("---")

    # 1. Dataset Dimensions & Basic Info
    p("### 1. Dataset Overview & Dimensions")
    p(f"- **Orders Table:** {df_orders.shape[0]:,} rows, {df_orders.shape[1]} columns")
    p(f"- **Returns Table:** {df_returns.shape[0]:,} rows, {df_returns.shape[1]} columns")
    p(f"- **Orders Primary Key Candidate (`Row ID`):** {df_orders['Row ID'].nunique():,} unique values (100% unique = {df_orders['Row ID'].nunique() == len(df_orders)})")
    p(f"- **Distinct Orders (`Order ID`):** {df_orders['Order ID'].nunique():,} unique order IDs")
    p(f"- **Distinct Customers (`Customer ID`):** {df_orders['Customer ID'].nunique():,} unique customer accounts")
    p(f"- **Distinct Products (`Product ID`):** {df_orders['Product ID'].nunique():,} unique catalog items\n")

    # 2. Missing Value Analysis
    p("### 2. Missing Value & Nullity Audit")
    p("| Table | Column Name | Data Type | Null Count | Null % | Remediation Strategy |")
    p("| :--- | :--- | :--- | :--- | :--- | :--- |")

    for col in df_orders.columns:
        null_count = df_orders[col].isna().sum()
        null_pct = (null_count / len(df_orders)) * 100
        strategy = "Clean (0 nulls)"
        if null_count > 0:
            if col == "Postal Code":
                strategy = "Retain; impute 'UNKNOWN' for non-US records (expected geographic limitation)"
            else:
                strategy = "Investigate & impute"
        p(f"| Orders | `{col}` | `{df_orders[col].dtype}` | {null_count:,} | {null_pct:.2f}% | {strategy} |")

    for col in df_returns.columns:
        null_count = df_returns[col].isna().sum()
        null_pct = (null_count / len(df_returns)) * 100
        strategy = "Clean (0 nulls)" if null_count == 0 else "Investigate"
        p(f"| Returns | `{col}` | `{df_returns[col].dtype}` | {null_count:,} | {null_pct:.2f}% | {strategy} |")
    p("")

    # 3. Duplicate Analysis
    p("### 3. Duplicate Record Audit")
    exact_order_dupes = df_orders.duplicated().sum()
    order_prod_dupes = df_orders.duplicated(subset=["Order ID", "Product ID"]).sum()
    returns_dupes = df_returns.duplicated().sum()

    p(f"- **Exact Row Duplicates in Orders:** {exact_order_dupes}")
    p(f"- **Order ID + Product ID Multi-Line Occurrences:** {order_prod_dupes:,} (Multiple units or split shipments for same SKU in single order)")
    p(f"- **Exact Row Duplicates in Returns:** {returns_dupes}\n")

    # 4. Date Integrity Checks
    p("### 4. Date Logic & Fulfillment Lifecycle Audit")
    df_orders["Order Date Clean"] = pd.to_datetime(df_orders["Order Date"], errors="coerce")
    df_orders["Ship Date Clean"] = pd.to_datetime(df_orders["Ship Date"], errors="coerce")
    
    order_date_nulls = df_orders["Order Date Clean"].isna().sum()
    ship_date_nulls = df_orders["Ship Date Clean"].isna().sum()
    min_order_date = df_orders["Order Date Clean"].min().strftime("%Y-%m-%d")
    max_order_date = df_orders["Order Date Clean"].max().strftime("%Y-%m-%d")
    
    lead_times = (df_orders["Ship Date Clean"] - df_orders["Order Date Clean"]).dt.days
    negative_lead_time_count = (lead_times < 0).sum()

    p(f"- **Temporal Span:** {min_order_date} to {max_order_date} (4 full fiscal years)")
    p(f"- **Order Date Parsing Nulls:** {order_date_nulls}")
    p(f"- **Ship Date Parsing Nulls:** {ship_date_nulls}")
    p(f"- **Logical Violations (Ship Date < Order Date):** {negative_lead_time_count} (Must be 0)")
    p(f"- **Fulfillment Lead Time (Days):** Min = {lead_times.min()} days, Median = {lead_times.median():.0f} days, Mean = {lead_times.mean():.2f} days, Max = {lead_times.max()} days\n")

    # 5. Numeric Range & Suspicious Values Audit
    p("### 5. Financial & Quantity Numeric Range Audit")
    p("| Metric Column | Min | 25th % | Median | 75th % | Max | Mean | Negative Count | Suspicious Values / Status |")
    p("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    numeric_cols = ["Sales", "Quantity", "Discount", "Profit", "Shipping Cost"]
    for col in numeric_cols:
        series = df_orders[col].astype(float)
        neg_count = (series < 0).sum()
        status = "Valid"
        if col == "Profit":
            status = f"Normal business losses ({neg_count:,} unprofitable transactions, {(neg_count/len(df_orders))*100:.1f}%)"
        elif neg_count > 0:
            status = f"WARNING: {neg_count} negative values detected"
        elif col == "Discount" and (series.max() > 1.0 or series.min() < 0):
            status = "WARNING: Discount outside [0.0, 1.0] range"
        elif col == "Quantity" and series.min() <= 0:
            status = "WARNING: Non-positive quantities detected"

        p(
            f"| `{col}` | {series.min():.2f} | {series.quantile(0.25):.2f} | "
            f"{series.median():.2f} | {series.quantile(0.75):.2f} | {series.max():.2f} | "
            f"{series.mean():.2f} | {neg_count:,} | {status} |"
        )
    p("")

    # 6. Returns Integration & Reconciliation
    p("### 6. Returns Data Integration & Order Matching")
    merged_returns = df_orders.merge(
        df_returns, on="Order ID", how="inner"
    )
    returned_orders_count = df_returns["Order ID"].nunique()
    matching_orders_in_fact = merged_returns["Order ID"].nunique()
    returned_lines_count = len(merged_returns)
    total_returned_sales = merged_returns["Sales"].sum()
    total_sales = df_orders["Sales"].sum()
    returned_sales_pct = (total_returned_sales / total_sales) * 100

    p(f"- **Distinct Order IDs in Returns Table:** {returned_orders_count:,}")
    p(f"- **Matched Order IDs in Orders Table:** {matching_orders_in_fact:,} ({(matching_orders_in_fact / returned_orders_count)*100:.1f}% match rate)")
    p(f"- **Total Order Line Items Impacted by Returns:** {returned_lines_count:,} ({returned_lines_count / len(df_orders):.2%} of all line items)")
    p(f"- **Gross Sales Exposed to Returns:** ${total_returned_sales:,.2f} ({returned_sales_pct:.2f}% of total enterprise GMV)\n")

    # 7. Explicit Metric Feasibility Mapping (Task 5)
    p("### 7. Explicit Metric Feasibility Matrix")
    p("Strictly separates fields available in the actual dataset from derived metrics and highlights external business metrics that cannot be calculated without speculation.\n")

    p("#### A. Fully Feasible Metrics (Directly Calculable from Available Columns)")
    p("| Proposed Metric | Source Columns | Mathematical Calculation | Feasibility Status |")
    p("| :--- | :--- | :--- | :--- |")
    p("| **Net Sales Revenue** | `Sales` | `SUM(Sales)` | 100% Feasible |")
    p("| **Gross Sales (List Price)** | `Sales`, `Discount` | `Sales / (1 - Discount)` | 100% Feasible |")
    p("| **Discount Dollar Concession** | `Sales`, `Discount` | `Gross Sales - Sales` | 100% Feasible |")
    p("| **COGS (Cost of Goods Sold)** | `Sales`, `Profit`, `Shipping Cost` | `Sales - Profit - Shipping Cost` | 100% Feasible (Unit Economics Balance) |")
    p("| **Gross Profit** | `Sales`, `COGS` | `Sales - COGS` | 100% Feasible |")
    p("| **Net Profit** | `Profit` | `SUM(Profit)` | 100% Feasible |")
    p("| **Net Profit Margin %** | `Profit`, `Sales` | `(SUM(Profit) / SUM(Sales)) * 100` | 100% Feasible |")
    p("| **Shipping Cost Burden %** | `Shipping Cost`, `Sales` | `(SUM(Shipping Cost) / SUM(Sales)) * 100` | 100% Feasible |")
    p("| **Fulfillment Lead Time (Days)**| `Order Date`, `Ship Date` | `Ship Date - Order Date` | 100% Feasible |")
    p("| **Return Rate % (by Order)** | `Order ID`, `Returns.Order ID`| `Count(Returned Orders) / Count(Total Orders)` | 100% Feasible |")
    p("| **Customer RFM Scores** | `Customer ID`, `Order Date`, `Profit` | Window/Quantile Recency, Frequency, Monetary | 100% Feasible |")
    p("| **Customer Cohort Retention** | `Customer ID`, `Order Date` | Min(Order Date) partition by customer | 100% Feasible |")
    p("| **Category Profit Bleeders** | `Product ID`, `Sub-Category`, `Profit` | Running cumulative profit loss | 100% Feasible |\n")

    p("#### B. Infeasible Metrics (Data Limitations - Not Present in Dataset)")
    p("| Metric | Required But Missing Data | Analytical Alternative / Recommendation |")
    p("| :--- | :--- | :--- |")
    p("| **Customer Acquisition Cost (CAC)** | Marketing advertising spend, campaign costs by channel | **Do NOT invent marketing spend.** Evaluate customer acquisition by cohort vintage and repeat order organic conversion instead. |")
    p("| **Return Restocking & Reverse Freight Fee** | Return carrier shipping invoices, restocking labor expense | **Do NOT invent reverse freight cost.** Quantify return impact via forfeited revenue and gross profit margin at risk. |")
    p("| **Warehouse Inventory Turnover & Stockouts**| Beginning/ending inventory count, stockout logs | **Do NOT invent warehouse stock.** Focus logistics analysis on fulfillment lead times and carrier shipping tier performance. |")
    p("| **Customer Demographic Profiling** | Age, gender, household income | Use native **`Segment`** (`Consumer`, `Corporate`, `Home Office`) and geographical markets. |\n")

    report_content = "\n".join(report_lines)
    report_file = DOCS_DIR / "data_profiling_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"\n[OK] Profiling complete! Structured report saved to: {report_file}")
    return report_content


if __name__ == "__main__":
    run_profiling()
