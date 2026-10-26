# E-Commerce Profitability Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%20%7C%20SQLite-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Pandas](https://img.shields.io/badge/Data%20Engineering-Pandas%20%7C%20NumPy-150458?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Power BI](https://img.shields.io/badge/Business%20Intelligence-Power%20BI-F2C811?style=flat&logo=powerbi&logoColor=black)](https://powerbi.microsoft.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade analytics engineering and business intelligence platform designed to diagnose **"profitless growth"** in e-commerce operations. By decomposing retail transactions into unit-level economics, this platform isolates margin erosion driven by excessive discounting, high return frequencies, and logistics freight overhead.

---

## 📌 Executive Architecture & Data Flow

```
                      +------------------------------------------+
                      |         RAW TRANSACTION DATA             |
                      |  * Orders (51,290 lines)                 |
                      |  * Returns (1,079 orders)                |
                      +--------------------+---------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |       PYTHON INGESTION & QUALITY GATE    |
                      |  * Schema & Type Validation              |
                      |  * Nullity & Duplicate Auditing          |
                      |  * Automated Sales/Profit Reconciliation |
                      +--------------------+---------------------+
                                           |
                                           v
                      +------------------------------------------+
                      |         ANALYTICS DATA WAREHOUSE         |
                      |           (Star Schema Design)           |
                      |  * 5 Dimensions (Customer, Product, Geo, |
                      |    Date, Shipping Mode)                  |
                      |  * 2 Facts (Orders, Returns)             |
                      |  * SQLite (Zero-config portability)      |
                      |  * PostgreSQL (Enterprise DDL)           |
                      +--------------------+---------------------+
                                           |
                        +------------------+------------------+
                        |                                     |
                        v                                     v
+------------------------------------------+ +------------------------------------------+
|       PYTHON ADVANCED ANALYTICS          | |       POWER BI EXECUTIVE DASHBOARD       |
| * Statistical Hypothesis Testing         | | * Executive KPI Scorecard                |
| * Price & Discount Elasticity of Demand  | | * Discount Erosion Waterfall             |
| * Category Profit Bleeders (Pareto)      | | * Merchandising Bleeders Matrix          |
| * Customer RFM & Cohort Retention        | | * Logistics Lead Time & Carrier Heatmap  |
+------------------------------------------+ +------------------------------------------+
```

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
* Python 3.10+ (Tested on Python 3.13)
* Git

### 2. Environment Setup
Clone the repository and install the minimal dependencies:

```bash
# Clone the repository
git clone https://github.com/your-username/Ecommerce-Profitability-Intelligence.git
cd Ecommerce-Profitability-Intelligence

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 3. Run Data Ingestion & Quality Audit
The automated ingestion pipeline downloads and caches the benchmark Global Superstore dataset (51,290 order lines + 1,079 return records) and generates a granular data profiling report:

```bash
# Ingest raw dataset and generate docs/data_profiling_report.md
python -m src.data_profiler
```

### 4. Build the Analytical Data Warehouse
Transform the raw denormalized data into a normalized Star Schema with full referential integrity and automated reconciliation checks:

```bash
# Executes dimensional modeling and populates SQLite database
python -m src.db_connector
```

*Output:* Populates `data/ecommerce_profitability.db` with 5 dimensions and 2 fact tables, verifying that database totals match raw source transactions to $0.00 delta.

---

## 📊 Dimensional Star Schema Model

The data warehouse conforms to a Kimball-style dimensional star schema:

```
                  +--------------------+
                  |   dim_customers    |
                  +--------------------+
                  | PK customer_key    |
                  |    customer_id     |
                  |    customer_name   |
                  |    segment         |
                  +---------+----------+
                            | 1
                            |
                            | N
+-------------------+     +--+-----------------+     +--------------------+
|   dim_products    |     |    fact_orders     |     |   dim_geography    |
+-------------------+     +--------------------+     +--------------------+
| PK product_key    |<----+ PK row_id          +---->| PK geography_key   |
|    product_id     | 1  N| FK customer_key    |N   1|    city            |
|    product_name   |     | FK product_key     |     |    state           |
|    category       |     | FK geography_key   |     |    country         |
|    sub_category   |     | FK order_date_key  |     |    region          |
+-------------------+     | FK ship_date_key   |     |    market          |
                          | FK shipping_mode_k |     |    postal_code     |
+-------------------+     |    sales           |     +--------------------+
|     dim_date      |     |    quantity        |
+-------------------+     |    discount        |     +--------------------+
| PK date_key       |<----+    profit          |---->| dim_shipping_mode  |
|    full_date      | 1  N|    shipping_cost   |N   1+--------------------+
|    year / quarter |     |    gross_sales     |     | PK shipping_mode_k |
|    month / day    |     |    cogs            |     |    ship_mode       |
+-------------------+     |    is_returned     |     +--------------------+
                          +---------+----------+
                                    | 1
                                    |
                                    | N
                          +---------+----------+
                          |    fact_returns    |
                          +--------------------+
                          | PK return_id       |
                          |    order_id        |
                          |    returned_flag   |
                          |    region          |
                          +--------------------+
```

---

## 📐 Unit Economics & Metric Formulas

To preserve analytical rigor, all derived metrics are clearly distinguished from source data:

| Metric | Calculation / Formula | Business Rationale |
| :--- | :--- | :--- |
| **Gross Sales (List Price)** | $\text{Sales} / (1 - \text{Discount})$ | Recovers the pre-promotional baseline revenue. |
| **Discount Concession ($)** | $\text{Gross Sales} - \text{Sales}$ | Quantifies the dollar value surrendered to discounts. |
| **Cost of Goods Sold (COGS)**| $\text{Sales} - \text{Profit} - \text{Shipping Cost}$ | Isolates product acquisition cost from fulfillment expenses. |
| **Net Profit Margin %** | $(\text{Profit} / \text{Sales}) \times 100$ | Measures true bottom-line profitability per order line. |
| **Shipping Cost Ratio %** | $(\text{Shipping Cost} / \text{Sales}) \times 100$ | Detects freight drag on low-ticket orders. |
| **Fulfillment Lead Time** | $\text{Ship Date} - \text{Order Date}$ | Measures supply chain dispatch and delivery speed. |
| **Return Status Flag** | $1 \text{ if Order ID exists in Returns else } 0$ | Quantifies net sales exposed to order cancellation. |

> **Data Limitation Note:** External commercial variables such as paid Customer Acquisition Cost (CAC) and warehouse inventory stockout counts are **not** present in the source dataset and are deliberately not fabricated.

---

## 🗂️ Project Directory Structure

```
Ecommerce-Profitability-Intelligence/
├── data/
│   ├── raw/                           # Original immutable raw files (Orders & Returns)
│   ├── processed/                     # Normalized dimensional CSV exports
│   └── ecommerce_profitability.db     # Populated SQLite analytical data warehouse
├── sql/
│   ├── 01_schema_ddl.sql              # ANSI/SQLite star schema DDL with indexes
│   ├── 01_schema_postgresql.sql       # Enterprise PostgreSQL DDL with check constraints
│   ├── 02_discount_elasticity.sql     # (Milestone 2) Discount tier margin queries
│   ├── 03_profit_bleeders_pareto.sql  # (Milestone 2) Cumulative SKU loss analysis
│   └── 04_customer_rfm.sql            # (Milestone 2) RFM quintiles & cohort retention
├── src/
│   ├── config.py                      # Centralized project configuration & paths
│   ├── data_loader.py                 # Dataset download, validation & CSV caching
│   ├── data_profiler.py               # Automated audit & data profiling report generator
│   └── db_connector.py                # Star schema ETL, transformation & assertions
├── docs/
│   ├── data_profiling_report.md       # Detailed data quality & audit report
│   ├── executive_summary.md           # Business narrative and strategic findings
│   └── interview_talking_points.md    # Placement interview prep guide (STAR method)
├── requirements.txt                   # Minimal project dependencies
├── PROJECT_PLAN.md                    # Complete project blueprint & specifications
└── README.md                          # Repository overview and execution guide
```

---

## 🚦 Implementation Milestones

- [x] **Milestone 1: Planning & Data Foundation**
  - [x] Workspace inspection and architecture blueprint ([PROJECT_PLAN.md](PROJECT_PLAN.md)).
  - [x] Dataset identification, download, and raw caching (51,290 Orders + 1,079 Returns).
  - [x] Automated data profiling script and audit report ([docs/data_profiling_report.md](docs/data_profiling_report.md)).
  - [x] Dual-database schema design (PostgreSQL & SQLite compatible).
  - [x] Automated Star Schema ETL pipeline with 100% financial reconciliation ($0.00 delta).
- [ ] **Milestone 2: Advanced SQL Analytics Suite** (CTEs, Window Functions, RFM, Cohorts)
- [ ] **Milestone 3: Python Statistical Modeling & Hypothesis Testing** (Welch's t-test, Elasticity)
- [ ] **Milestone 4: Power BI Dashboard Application & What-If Parameter Modeling**
- [ ] **Milestone 5: Documentation, Executive Synthesis & Placement Interview Guide**

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
