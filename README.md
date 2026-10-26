# E-Commerce Profitability Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%20%7C%20SQLite-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Pandas](https://img.shields.io/badge/Data%20Engineering-Pandas%20%7C%20NumPy-150458?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![SciPy](https://img.shields.io/badge/Statistics-SciPy%201.18-8CAAE6?style=flat&logo=scipy&logoColor=white)](https://scipy.org/)
[![Tests](https://img.shields.io/badge/Tests-18%2F18%20Passing-brightgreen?style=flat&logo=pytest&logoColor=white)](tests/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade analytics engineering, statistical intelligence, and business intelligence platform designed to diagnose **"profitless growth"** in e-commerce operations. By decomposing retail transactions into unit-level economics, this platform isolates margin erosion driven by excessive discounting, high return frequencies, and logistics freight overhead.

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
|       PYTHON STATISTICAL ENGINE          | |       POWER BI EXECUTIVE DASHBOARD       |
| * Welch's t-test (t=127.1, p<0.001)      | | * Executive KPI Scorecard                |
| * Kruskal-Wallis (H=25,991, eta^2=0.683) | | * Discount Erosion Waterfall             |
| * Games-Howell Pairwise Post-Hoc Tests   | | * Merchandising Bleeders Matrix          |
| * Spearman Rank (rho=-0.669, p<0.001)    | | * Logistics Lead Time & Carrier Heatmap  |
| * Chi-Square Returns (chi2=4.31, p=0.116)| | * What-If Discount Cap Simulator         |
+------------------------------------------+ +------------------------------------------+
```

---

## 🚀 Quickstart & Reproduction Guide

### 1. Prerequisites
* Python 3.10+ (Tested on Python 3.13)
* Git

### 2. Environment Setup
```bash
# Clone the repository
git clone https://github.com/Chaitanya6006/ecommerce-profitability-intelligence.git
cd ecommerce-profitability-intelligence

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 3. Build Warehouse & Run Quality Audit
The automated ingestion pipeline caches the benchmark Global Superstore dataset (51,290 order lines + 1,079 return records) and builds the Star Schema database with zero financial discrepancy ($0.00 delta):

```bash
# Ingest raw dataset and generate docs/data_profiling_report.md
python -m src.data_profiler

# Build Star Schema analytical warehouse and export clean dimensional tables
python -m src.db_connector
```

### 4. Execute Advanced SQL Analytics Suite
Executes all 8 analytical SQL modules (Executive KPIs, Category Unit Economics, Discount Tiers, RFM Segmentation, Cohort Retention, Window Functions, and Logistics):

```bash
# Executes SQL suite and exports 12 analytical datasets to data/processed/analytics/
python -m src.run_sql_analytics
```

### 5. Run Advanced Python Statistical Analysis
Executes parametric and non-parametric hypothesis tests, contingency evaluations, and generates scientific visual reports:

```bash
# Runs Welch's t-test, ANOVA/Kruskal-Wallis, Games-Howell, Spearman, and Chi-Square
python -m src.statistical_analysis
```

### 6. Generate Executive Visualizations
Generates publication-quality operational and executive charts saved to `reports/figures/`:

```bash
# Generates trend lines, margin bar charts, RFM distributions, and cohort heatmaps
python -m src.visualizations
```

### 7. Run Complete Test Suite
Executes the automated unit tests covering pipeline integrity, financial balance, statistical validity, boundary limits, and figure generation:

```bash
# Runs all 18 automated unit tests
python -m unittest discover tests
```

---

## 📈 Executive KPI Scorecard (Source-Reconciled)

| Metric | Historical Value (2012–2015) | Business Interpretation |
| :--- | :--- | :--- |
| **Gross Merchandise Value (GMV)** | **\$12,642,501.91** | Reconciled net transactional revenue collected |
| **Total Net Profit** | **\$1,467,457.29** | Net operating profit earned across all product lines |
| **Net Profit Margin %** | **11.61%** | Baseline operating profitability efficiency |
| **Total Distinct Orders** | **25,728** | Discrete shopping transactions completed |
| **Average Order Value (AOV)** | **\$491.39** | Mean gross basket size per order |
| **Total Line Items** | **51,290** | Individual SKU order line items fulfilled |
| **Total Unique Customers** | **17,415** | Distinct consumer, corporate, and home-office accounts |
| **Order Return Rate %** | **4.19%** | Denominator: 25,728 distinct orders (1,079 returned) |
| **Line Item Return Rate %** | **4.33%** | Denominator: 51,290 line items (2,220 returned lines) |
| **GMV Exposed to Returns** | **\$525,932.23 (4.16%)**| Top-line sales volume impacted by return requests |
| **Average Lead Time** | **3.97 Days** | Mean fulfillment latency from order placement to dispatch |

---

## 🔬 Scientific Hypothesis Testing & Statistical Findings

Comprehensive statistical analysis was conducted with strictly separated units of analysis to safeguard against pseudo-replication (detailed in [`reports/statistical_analysis_report.md`](reports/statistical_analysis_report.md)):

### Summary of Statistical Tests

| Hypothesis / Research Question | Unit of Analysis | Statistical Test Used | Test Statistic | p-value | Effect Size | Empirical Conclusion |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **H1: Undiscounted vs. Discounted Margins** | Line Item ($n=51,290$) | Welch's t-test & Mann-Whitney U | $t(24,595) = 127.11$ | $p < 10^{-300}$ | Hedges' $g = 1.270$ | **Reject $H_0$:** Undiscounted mean is $+26.49\%$, discounted is $-23.57\%$. Massive divergence. |
| **H2: Multi-Tier Margin Degradation** | Line Item ($n=51,290$) | Kruskal-Wallis & ANOVA | $H(4) = 25,991.51$ | $p < 10^{-300}$ | $\eta^2 = 0.6829$ | **Reject $H_0$:** $68.3\%$ of margin variance explained by discount tier. All pairs differ significantly. |
| **H3: Discount Depth vs. Order Returns** | Order Level ($n=25,728$) | Chi-Square ($\chi^2$) Contingency | $\chi^2(2) = 4.3103$ | $p = 0.1159$ | Cramér's $V = 0.0129$ | **Fail to Reject $H_0$:** Return rates ($3.98\%$ vs $4.32\%$) are independent of discount depth. |
| **Association: Discount vs. Margin** | Line & Order Levels | Spearman Rank Correlation | $\rho_{\text{line}} = -0.6691$, $\rho_{\text{order}} = -0.6898$ | $p < 10^{-300}$ | $95\%\text{ CI: } [-0.68, -0.66]$ | Intense monotonic negative association between discounts and profit margins. |

### Statistical Visualizations

| Figure Preview | Description |
| :--- | :--- |
| ![Discount Group Distributions](reports/figures/statistical/discount_group_distributions.png) | **Profit Margin Distributions Across Discount Tiers:** Boxplot showing severe downward shift into negative margins once discounts exceed 20%. |
| ![Profit Margin Means with 95% CIs](reports/figures/statistical/profit_margin_ci_comparison.png) | **Mean Margin with 95% Confidence Intervals:** Group means with Welch error bars illustrating margin degradation from $+26.5\%$ to $-86.8\%$. |
| ![Discount vs Margin Spearman Density](reports/figures/statistical/discount_vs_profit_margin_spearman.png) | **Discount vs Profit Margin Spearman Association:** Hexbin density plot showing non-linear monotonic decay ($\rho = -0.6691$). |
| ![Order Return Rate by Discount](reports/figures/statistical/return_rate_by_discount_group.png) | **Order Return Rate by Discount Bracket:** Wilson score intervals proving return rates remain uniform ($3.98\%$–$4.53\%$) across discount tiers. |

---

## 📊 Analytical Visualizations & Executive Insights

### 1. Monthly Net Sales & Profit Pacing
Demonstrates steady multi-year growth with severe margin compression during promotional surges in Q4.
![Monthly Sales and Profit Trend](reports/figures/monthly_sales_profit_trend.png)

### 2. Category Profitability & Margin Bleeders
Isolates sub-categories that drive heavy volume but generate negative net profit (notably **Tables** at -\$64.1K net loss and **Bookcases** at -\$3.5K net loss).
![Sub-Category Profitability Breakdown](reports/figures/category_profitability_breakdown.png)

### 3. Customer RFM Persona Segmentation
Partitions the customer base into strategic personas. Reveals that 4,427 customers (**25.4%**) operate as **Margin Drainers**, accumulating -\$773,201 in net operating losses.
![Customer RFM Segments Distribution](reports/figures/customer_segments_distribution.png)

### 4. Multi-Year Customer Cohort Retention Heatmap
Visualizes customer retention across multi-year vintages.
![Cohort Retention Heatmap](reports/figures/cohort_retention_heatmap.png)

---

## 📐 Unit Economics & Metric Formulas

To preserve analytical rigor, all derived metrics are clearly distinguished from raw dataset attributes:

| Metric | Exact Mathematical Formula | Business Rationale |
| :--- | :--- | :--- |
| **Gross Sales (List Price)** | $\text{Sales} / (1 - \text{Discount}) \quad (\text{if Discount} < 1)$ | Recovers the pre-promotional baseline revenue. |
| **Discount Concession ($)** | $\text{Gross Sales} - \text{Sales}$ | Quantifies the dollar value surrendered to discounts. |
| **Cost of Goods Sold (COGS)**| $\text{Sales} - \text{Profit} - \text{Shipping Cost}$ | Isolates product acquisition cost from fulfillment expenses. |
| **Net Profit Margin %** | $(\text{Profit} / \text{Sales}) \times 100$ | Measures true bottom-line profitability per order line. |
| **Shipping Cost Ratio %** | $(\text{Shipping Cost} / \text{Sales}) \times 100$ | Detects freight drag on low-ticket orders. |
| **Fulfillment Lead Time** | $\text{Ship Date} - \text{Order Date}$ | Measures supply chain dispatch and delivery speed. |
| **Return Status Flag** | $1 \text{ if Order ID exists in Returns else } 0$ | Quantifies net sales exposed to order cancellation. |

> **Data Limitation Note:** External commercial variables such as paid advertising Customer Acquisition Cost (CAC) and warehouse inventory stockout counts are **not** present in the source dataset and are deliberately not fabricated.

---

## 🗂️ Project Directory Structure

```
Ecommerce-Profitability-Intelligence/
├── data/
│   ├── raw/                           # Original immutable raw files (Orders & Returns)
│   ├── processed/                     # Normalized dimensional CSV exports for Power BI
│   │   └── analytics/                 # Exported SQL analytical summary datasets
│   └── ecommerce_profitability.db     # Populated SQLite analytical data warehouse
├── sql/
│   ├── 01_schema_ddl.sql              # ANSI/SQLite star schema DDL with indexes
│   ├── 01_schema_postgresql.sql       # Enterprise PostgreSQL DDL with check constraints
│   ├── 02_executive_kpis.sql          # Enterprise Scorecard (GMV, Profit, AOV, Returns)
│   ├── 03_product_category_profitability.sql # Sub-Category unit economics & Pareto bleeders
│   ├── 04_discount_analysis.sql       # Discount tiers & margin degradation matrix
│   ├── 05_customer_rfm.sql            # RFM quintiles & customer personas
│   ├── 06_customer_cohorts.sql        # Annual & monthly customer cohort retention
│   ├── 07_window_functions.sql        # RANK, DENSE_RANK, LAG growth & basket quartiles
│   ├── 08_shipping_regional_analysis.sql # Logistics SLAs, shipping tiers & regional margin
│   └── 09_data_reconciliation.sql     # Automated SQL assertion tests (100% pass)
├── src/
│   ├── config.py                      # Centralized configuration & directory paths
│   ├── data_loader.py                 # File ingestion, download resilience & CSV caching
│   ├── data_profiler.py               # Automated data quality profiling report generator
│   ├── db_connector.py                # Star schema ETL, transformation & assertions
│   ├── run_sql_analytics.py           # Automated SQL suite runner & analytics exporter
│   ├── statistical_analysis.py        # Advanced Python statistical testing & report generator
│   └── visualizations.py              # Publication-quality figure generation module
├── reports/
│   ├── statistical_analysis_report.md # Comprehensive hypothesis testing & scientific report
│   └── figures/                       # Exported PNG visual reporting charts
│       └── statistical/               # Focused statistical distribution & correlation charts
├── docs/
│   ├── data_profiling_report.md       # Comprehensive data audit & nullity report
│   └── interview_talking_points.md    # Placement interview prep guide (STAR method)
├── tests/
│   ├── test_data_integrity.py         # Pipeline & schema verification tests (6/6 passing)
│   ├── test_analytics.py              # Analytical output & KPI verification tests (6/6 passing)
│   └── test_statistical_analysis.py   # Statistical tests & hypothesis assertions (6/6 passing)
├── requirements.txt                   # Frozen production dependencies (including SciPy)
├── PROJECT_PLAN.md                    # Technical blueprint & milestone roadmap
└── README.md                          # Repository presentation & reproduction guide
```

---

## 🚦 Implementation Milestones & Roadmap

- [x] **Milestone 1: Planning & Data Foundation**
  - [x] Workspace inspection and architecture blueprint ([PROJECT_PLAN.md](PROJECT_PLAN.md)).
  - [x] Dataset identification, download, and raw caching (51,290 Orders + 1,079 Returns).
  - [x] Automated data profiling script and audit report ([docs/data_profiling_report.md](docs/data_profiling_report.md)).
  - [x] Dual-database schema design (PostgreSQL & SQLite compatible).
  - [x] Automated Star Schema ETL pipeline with 100% financial reconciliation ($0.00 delta).
  - [x] Public GitHub repository initialization ([Chaitanya6006/ecommerce-profitability-intelligence](https://github.com/Chaitanya6006/ecommerce-profitability-intelligence)).
- [x] **Milestone 2: Advanced SQL Analytics & Visualization Suite**
  - [x] Complete SQL analytics portfolio (KPIs, Products, Discounts, RFM, Cohorts, Windows, Logistics).
  - [x] Automated reconciliation quality gate (`sql/09_data_reconciliation.sql` - 4/4 passing).
  - [x] Automated Python analytics runner exporting 12 datasets to `data/processed/analytics/`.
  - [x] Executive visual reporting suite producing 5 high-resolution charts in `reports/figures/`.
  - [x] Automated test suite: 12/12 unit tests passing in 0.14s.
- [x] **Milestone 3: Python Statistical Analysis & Econometric Hypothesis Testing**
  - [x] Welch's t-test and Mann-Whitney U on undiscounted vs discounted margins ($t=127.11, p<0.001$).
  - [x] Kruskal-Wallis multi-tier test ($H=25,991, \eta^2=0.683$) and Games-Howell post-hoc.
  - [x] Spearman rank correlation ($\rho_{\text{line}}=-0.6691, \rho_{\text{order}}=-0.6898$).
  - [x] Order-level Chi-Square contingency test ($\chi^2=4.31, p=0.116$) evaluating return rate independence.
  - [x] 4 publication-quality statistical charts in `reports/figures/statistical/`.
  - [x] Comprehensive research report in `reports/statistical_analysis_report.md`.
  - [x] Complete test suite passing: 18/18 tests in 5.05s.
- [ ] **Milestone 4: Power BI Enterprise Dashboard Application (.pbix)**
- [ ] **Milestone 5: Executive Business Synthesis & Placement Interview Prep**

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
