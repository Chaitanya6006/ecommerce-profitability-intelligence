# E-Commerce Profitability Intelligence Platform
## Technical Architecture & Project Implementation Blueprint

---

## 1. Executive Summary & Business Context

In contemporary e-commerce operations, top-line revenue growth frequently masks severe underlying margin degradation—a phenomenon commonly described as **"profitless growth."** Businesses often scale gross merchandise value (GMV) by expanding promotions, absorbing customer shipping expenses, and widening product selections. However, without granular unit economics tracking, aggressive discounting, hidden return logistics costs, and regional supply chain overhead quietly cannibalize operating income.

The **E-Commerce Profitability Intelligence Platform** is designed as an end-to-end analytics engineering and business intelligence solution. It transitions an organization from basic transactional tracking to **unit-level margin transparency**. The project integrates a normalized PostgreSQL data warehouse, automated Python validation and exploratory pipelines, advanced analytical SQL modeling (CTEs, window functions, cohort retention), rigorous statistical hypothesis testing, and an executive-ready Power BI business intelligence dashboard.

```
       +-------------------------------------------------------------+
       |                     RAW DATA SOURCES                        |
       |  (Orders, Line Items, Returns, Geography, Customers, Cost)   |
       +------------------------------+------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |               PYTHON INGESTION & DATA QUALITY               |
       |   * Type Enforcement   * Missing Value Audit                |
       |   * Range Validation   * Deduplication & Integrity Checks    |
       +------------------------------+------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |               POSTGRESQL ANALYTICS WAREHOUSE                |
       |   * Star Schema (Facts: Orders, Returns; Dims: Customers,   |
       |     Products, Geography, Date, Shipping)                    |
       |   * Analytical Views (RFM, Discount Elasticity, Bleeders)   |
       +------------------------------+------------------------------+
                                      |
                     +----------------+----------------+
                     |                                 |
                     v                                 v
       +----------------------------+   +----------------------------+
       |      PYTHON ADVANCED       |   |      POWER BI DECISION     |
       |    STATISTICAL MODELING    |   |         DASHBOARD          |
       | * Hypothesis Testing       |   | * Executive KPI Scorecard  |
       | * Margin Elasticity        |   | * Discount Degradation     |
       | * Correlation & Outliers   |   | * Category Profit Bleeders |
       | * Customer Cohorts         |   | * Customer RFM & Logistics |
       +----------------------------+   +----------------------------+
```

---

## 2. Stakeholders & Business Questions

### 2.1 Primary Stakeholders
| Stakeholder | Key Interest | Primary Deliverable |
| :--- | :--- | :--- |
| **Chief Commercial / Financial Officer (CCO/CFO)** | Operating margin health, margin erosion from promotions, net profit by channel. | Executive Scorecard & Profitability Waterfall |
| **Head of Merchandising / Category Managers** | Sub-category unit economics, identify "bleeders" (negative-margin items), pricing elasticity. | Product & Category Deep-Dive, Pareto Analysis |
| **VP of Supply Chain & Logistics** | Fulfillment cycle time, shipping cost ratio vs. order value, regional shipping cost anomalies. | Regional Logistics & Shipping Efficiency View |
| **Director of Customer Growth & Marketing** | Customer segment profitability, repeat vs. one-time buyer economics, discount-seeking behavior. | Customer RFM Matrix & Cohort Retention Analysis |

### 2.2 Core Business Questions
1. **Discount Degradation & Margin Cannibalization:**
   * At what discount threshold does transaction volume fail to compensate for margin loss?
   * Are certain categories generating substantial volume while operating at a net loss due to excessive discounting?
2. **Product Margin Bleeders (Pareto Analysis):**
   * Which bottom 10%–20% of SKUs or sub-categories account for the bulk of negative profit contribution?
   * How do manufacturing costs (COGS) vs. shipping overhead drive SKU unprofitability?
3. **Customer Cohort Economics & Retention:**
   * Are repeat customers substantially more profitable than one-time discount shoppers?
   * What is the average customer lifetime value (CLV proxy) across customer segments (Consumer, Corporate, Home Office)?
4. **Logistics & Regional Friction:**
   * Which geographic regions or shipping tiers have disproportionately high freight costs relative to order basket size?
   * How does shipping delay (fulfillment cycle time) correlate with high return rates?
5. **Returns Impact on Net Realized Revenue:**
   * What proportion of gross sales is forfeited due to order returns, and which specific product lines suffer from high return velocity?

---

## 3. Dataset Evaluation & Recommendation

### 3.1 Dataset Evaluation Matrix
To ensure realistic analysis without fabricating data, two leading public e-commerce datasets were evaluated:

| Criteria | Brazilian E-Commerce (Olist) | Global Superstore E-Commerce Dataset |
| :--- | :--- | :--- |
| **Order-Level Granularity** | Yes (99k orders) | Yes (51k+ order lines) |
| **Product Cost (COGS) / Profit** | **Missing** (Requires synthetic modeling) | **Native** (Explicit Sales, Profit, Cost) |
| **Discount Tracking** | **Missing** (Vouchers present, no % discount) | **Native** (Order-line discount %: 0.0 to 0.8) |
| **Shipping Costs** | Native (`freight_value`) | Native (`shipping_cost`) |
| **Customer Segments** | Limited (Geo only) | Rich (Consumer, Corporate, Home Office) |
| **Returns Data** | Partial (`order_status = canceled`) | Explicit (`fact_returns` relational table) |
| **Suitability for Interview** | Good for SQL joins, poor for profitability | **Optimal for End-to-End Profitability Analysis** |

### 3.2 Recommended Dataset: Global Superstore Transactional Dataset
* **Source:** Publicly validated benchmark e-commerce dataset (51,290 records spanning multi-year global retail transactions).
* **Rationale:** It natively contains every attribute necessary to analyze unit economics, price elasticity, returns, shipping costs, and customer segments **without creating artificial profit numbers**.

### 3.3 Data Dictionary: Actual vs. Derived Fields

#### A. Actual Raw Dataset Fields
* `Row ID` / `Order ID`: Unique identifiers.
* `Order Date` / `Ship Date`: Transaction and fulfillment timestamps.
* `Ship Mode`: Standard Class, Second Class, First Class, Same Day.
* `Customer ID`, `Customer Name`, `Segment`: Customer attributes.
* `City`, `State`, `Country`, `Postal Code`, `Market`, `Region`: Geographic attributes.
* `Product ID`, `Category`, `Sub-Category`, `Product Name`: Product catalog.
* `Sales`: Net transaction revenue.
* `Quantity`: Units purchased.
* `Discount`: Applied promotional rate ($0.0$ to $0.85$).
* `Profit`: Net profit earned on the transaction line.
* `Shipping Cost`: Operational expense incurred to deliver the order line.
* `Order Priority`: Critical, High, Medium, Low.
* `Returned` (Returns table): Boolean flag identifying returned orders.

#### B. Derived Fields & Explicit Formulas
To maintain analytical transparency, all calculated fields are defined mathematically:

| Derived Field | Exact Mathematical Formula | Business Purpose |
| :--- | :--- | :--- |
| **Gross Sales (Undiscounted)** | $\text{Gross Sales} = \frac{\text{Sales}}{1 - \text{Discount}} \quad (\text{if Discount} < 1)$ | Establishes the baseline list price before promotional intervention. |
| **Discount Dollar Value** | $\text{Discount Amount} = \text{Gross Sales} - \text{Sales}$ | Quantifies the total dollar revenue conceded to promotions. |
| **Cost of Goods Sold (COGS)** | $\text{COGS} = \text{Sales} - \text{Profit} - \text{Shipping Cost}$ | Isolates true product acquisition/manufacturing cost. |
| **Gross Profit Margin (%)** | $\text{Gross Margin} = \left(\frac{\text{Sales} - \text{COGS}}{\text{Sales}}\right) \times 100$ | Measures product markup viability before shipping. |
| **Net Profit Margin (%)** | $\text{Net Margin} = \left(\frac{\text{Profit}}{\text{Sales}}\right) \times 100$ | Evaluates bottom-line line profitability. |
| **Shipping Cost Ratio (%)** | $\text{Shipping Ratio} = \left(\frac{\text{Shipping Cost}}{\text{Sales}}\right) \times 100$ | Detects freight margin erosion on low-value items. |
| **Fulfillment Lead Time** | $\text{Lead Time (Days)} = \text{Ship Date} - \text{Order Date}$ | Measures supply chain fulfillment cycle. |
| **Is Returned Flag** | $\text{CASE WHEN r.Returned = 'Yes' THEN 1 ELSE 0 END}$ | Identifies order cancellation/return impact. |

---

## 4. Proposed Database Architecture (PostgreSQL)

To demonstrate industry-standard analytics engineering, the data is normalized into a **Star Schema Data Warehouse** optimized for analytical queries (OLAP) and Power BI ingestion.

```
                  +-----------------------+
                  |     dim_customers     |
                  +-----------------------+
                  | PK  customer_key      |
                  |     customer_id       |
                  |     customer_name     |
                  |     segment           |
                  +-----------+-----------+
                              |
                              | 1
                              |
                              | N
+-----------------------+     +-----------------------+     +-----------------------+
|     dim_products      |     |      fact_orders      |     |     dim_geography     |
+-----------------------+     +-----------------------+     +-----------------------+
| PK  product_key       |<----+ PK  order_item_key    +---->| PK  geography_key     |
|     product_id        | 1  N| FK  customer_key      |N   1|     city              |
|     product_name      |     | FK  product_key       |     |     state             |
|     category          |     | FK  geography_key     |     |     country           |
|     sub_category      |     | FK  order_date_key    |     |     postal_code       |
+-----------------------+     | FK  ship_date_key     |     |     region            |
                              | FK  shipping_mode_key |     |     market            |
                              |     order_id          |     +-----------------------+
+-----------------------+     |     sales             |
|       dim_date        |     |     quantity          |     +-----------------------+
+-----------------------+     |     discount          |     |   dim_shipping_mode   |
| PK  date_key          |<----+     profit            |     +-----------------------+
|     full_date         | 1  N|     shipping_cost     |---->| PK  shipping_mode_key |
|     day_of_month      |     |     cogs              |N   1|     ship_mode         |
|     month             |     |     gross_sales       |     +-----------------------+
|     quarter           |     |     discount_amount   |
|     year              |     |     is_returned       |
|     is_weekend        |     +-----------+-----------+
+-----------------------+                 |
                                          | 1
                                          |
                                          | N
                              +-----------+-----------+
                              |      fact_returns     |
                              +-----------------------+
                              | PK  return_key        |
                              |     order_id          |
                              |     return_status     |
                              |     region            |
                              +-----------------------+
```

### 4.1 Schema DDL Overview (PostgreSQL)
* **`dim_customers`**: Surrogate key `customer_key`, natural `customer_id`, customer profile, segment.
* **`dim_products`**: Surrogate key `product_key`, natural `product_id`, category hierarchy.
* **`dim_geography`**: Spatial reference table with clean postal codes and regional markets.
* **`dim_date`**: Calendar dimensional table containing fiscal quarters, day of week, and holiday indicators.
* **`dim_shipping_mode`**: Fulfillment tier dimensional mapping.
* **`fact_orders`**: Grain = **1 row per Order Line Item**. Contains transactional measures, foreign keys, and precomputed unit economics.
* **`fact_returns`**: Grain = **1 row per Returned Order**.

### 4.2 Database Performance & Integrity
* **B-Tree Indexes:** Built on foreign keys (`customer_key`, `product_key`, `order_date_key`) and high-cardinality filters.
* **Integrity Constraints:**
  * `CHECK (discount >= 0.0 AND discount <= 1.0)`
  * `CHECK (quantity > 0)`
  * `CHECK (ship_date >= order_date)`

---

## 5. Data Cleaning & Quality Assurance Strategy

### 5.1 Data Quality Dimensions & Verification Gates

| Quality Dimension | Potential Flaw in Raw Data | Remediation / Validation Rule |
| :--- | :--- | :--- |
| **Completeness** | Missing Postal Codes in non-US records | Impute with `'UNKNOWN'` or Country Capital Code; never drop rows. |
| **Uniqueness** | Duplicate line items with identical `Order ID` + `Product ID` | Aggregate duplicates or isolate surrogate line sequence. |
| **Validity** | Impossible discount percentages ($> 100\%$ or $< 0\%$) | Assert $0 \le \text{Discount} \le 1$; flag anomalies. |
| **Logical Consistency** | `Ship Date` precedes `Order Date` | Filter or log discrepancies; assert $\text{Ship Date} \ge \text{Order Date}$. |
| **Financial Integrity** | Negative Sales values | Verify if negative sales represent returns or logging anomalies. |
| **Referential Integrity** | Orphaned foreign keys between returns and orders | Ensure left joins retain all valid order records with 0 for return flag. |

### 5.2 Automated Validation Pipeline (Python & SQL)
A dedicated script (`scripts/data_validator.py`) will execute pre-load and post-load assertions:
1. **Schema Check:** Assert column datatypes match target specifications.
2. **Null Value Audit:** Zero nulls allowed in primary keys or core financial metrics (`Sales`, `Quantity`, `Profit`).
3. **Distribution Audit:** Flag statistical anomalies (e.g., $Z\text{-score} > 4$ on shipping fees).
4. **Reconciliation Check:** Reconcile aggregate raw sales against database fact table sales to ensure zero data leakage.

---

## 6. Advanced SQL Analytics Plan

The SQL layer will demonstrate intermediate and advanced concepts (CTEs, Window Functions, Self-Joins, Conditional Aggregation, and Cohort Analysis).

### 6.1 Planned Query Portfolio
1. **Discount Elasticity & Profit Threshold Analysis (CTE + NTILE + Window Functions):**
   * Classify transactions into discount brackets: `No Discount (0%)`, `Low (1-10%)`, `Moderate (11-20%)`, `Aggressive (21-40%)`, and `Deep (>40%)`.
   * Measure aggregate profit margin, transaction frequency, and total profit erosion per tier.
2. **Category & Sub-Category Profit Bleeders (Pareto Principle):**
   * Calculate cumulative profit contribution using `SUM(profit) OVER (ORDER BY profit ASC)`.
   * Identify the specific SKUs and sub-categories accounting for 80% of aggregate enterprise losses.
3. **Customer Cohort Retention & Lifetime Profitability:**
   * Determine each customer's cohort acquisition month using `MIN(order_date) OVER (PARTITION BY customer_id)`.
   * Track subsequent purchasing activity across 30, 60, 90, 180, and 365-day intervals.
4. **Logistics Bottleneck & Freight Drag Query:**
   * Evaluate `AVG(ship_date - order_date)` and `AVG(shipping_cost / sales)` by carrier mode and destination market.
   * Highlight shipping tiers where logistics cost exceeds net product gross profit.
5. **Customer RFM Segmentation (Recency, Frequency, Monetary):**
   * Calculate Recency (days since last purchase), Frequency (distinct order count), and Monetary value (total profit generated).
   * Assign quintile scores using `NTILE(5)` and map customers to actionable business personas: *Champions, Loyal Customers, Potential Loyalists, At Risk, Hibernating, Margin Drainers*.

---

## 7. Python & Statistical Analysis Plan

Rather than superficial chart plotting, the Python layer will focus on **scientific data validation and statistical hypothesis testing**.

### 7.1 Statistical Hypotheses & Methodology
* **Hypothesis 1 (Discount vs. Margin Degradation):**
  * *Null Hypothesis ($H_0$):* There is no significant difference in net profit margin between discounted and undiscounted transactions.
  * *Alternative ($H_1$):* Discounted transactions exhibit significantly lower net profit margins.
  * *Test:* Two-sample Welch’s t-test (or Mann-Whitney U test given non-normal financial distributions).
* **Hypothesis 2 (Return Propensity vs. Deep Discounting):**
  * *Null Hypothesis ($H_0$):* Return probability is independent of the discount tier.
  * *Alternative ($H_1$):* Deeply discounted items have a significantly higher return likelihood.
  * *Test:* Chi-Square Test of Independence ($\chi^2$).
* **Hypothesis 3 (Shipping Efficiency by Customer Segment):**
  * *Null Hypothesis ($H_0$):* Average fulfillment lead time is uniform across customer segments.
  * *Alternative ($H_1$):* Specific segments experience significantly longer fulfillment lead times.
  * *Test:* One-Way ANOVA or Kruskal-Wallis test.

### 7.2 Exploratory Data Analysis & Econometrics
* **Price & Discount Elasticity of Demand:** Calculate point elasticity:
  $$\epsilon = \frac{\% \Delta \text{ Quantity}}{\% \Delta \text{ Price}}$$
  to evaluate whether promotional price cuts generate sufficient volume expansion.
* **Distributional Diagnostics:** Skewness, Kurtosis, and Log-transformation of skewed financial metrics.
* **Correlation Matrix:** Spearman rank correlation assessing relationships between Unit Cost, Discount %, Shipping Cost, and Final Margin.

---

## 8. Power BI Dashboard Architecture & UI/UX Design

The dashboard will be organized into an intuitive, multi-page business intelligence application with unified cross-filtering and drill-through capabilities.

```
+-----------------------------------------------------------------------------------------+
| PAGE 1: EXECUTIVE PROFITABILITY SCORECARD                                               |
| [Date Slicer] [Market Slicer] [Segment Slicer] [Category Slicer]                        |
| +----------------+ +----------------+ +----------------+ +----------------+            |
| | Gross Revenue  | | Net Profit     | | Net Margin %   | | Return Rate %  |            |
| | $12.64M (▲8%)  | | $1.47M (▼2%)   | | 11.6% (-120bp) | | 5.8% (▲40bp)   |            |
| +----------------+ +----------------+ +----------------+ +----------------+            |
| +-----------------------------------------+ +-----------------------------------------+ |
| | Monthly Revenue vs. Net Profit Trend    | | Global Market Profitability Heatmap     | |
| | (Dual-axis area & line chart)           | | (Choropleth map with margin bubbles)    | |
| +-----------------------------------------+ +-----------------------------------------+ |
+-----------------------------------------------------------------------------------------+
| PAGE 2: DISCOUNT & MARGIN ELASTICITY INTELLIGENCE                                       |
| +-----------------------------------------+ +-----------------------------------------+ |
| | Margin % by Discount Bracket (Boxplot)  | | Discount Drag vs. Incremental Sales     | |
| | (Visualizes margin cliff at >20% disc)  | | (Scatter plot: Vol vs Margin colored)   | |
| +-----------------------------------------+ +-----------------------------------------+ |
| +-------------------------------------------------------------------------------------+ |
| | What-If Parameter Simulator: "Cap Maximum Discount at [  20%  ]"                     | |
| | Projected Profit Recovered: +$248,500 | Projected Retained Volume: 94.2%            | |
| +-------------------------------------------------------------------------------------+ |
+-----------------------------------------------------------------------------------------+
| PAGE 3: MERCHANDISING PARETO & PROFIT BLEEDERS                                          |
| +-----------------------------------------+ +-----------------------------------------+ |
| | Sub-Category Profit Waterfall           | | Top 10 Margin Drainers (Bleeders Table)  | |
| | (Identifies tables/binders margin loss) | | SKU | Sales | Profit | Margin% | Return% | |
| +-----------------------------------------+ +-----------------------------------------+ |
+-----------------------------------------------------------------------------------------+
| PAGE 4: CUSTOMER RFM & COHORT VALUE                                                     |
| +-----------------------------------------+ +-----------------------------------------+ |
| | Customer Segment Profit Matrix          | | RFM Segment Distribution Treemap        | |
| | (Consumer vs Corporate vs Home Office)  | | (Champions, At-Risk, Drainers)          | |
| +-----------------------------------------+ +-----------------------------------------+ |
+-----------------------------------------------------------------------------------------+
| PAGE 5: LOGISTICS & SUPPLY CHAIN EFFICIENCY                                             |
| +-----------------------------------------+ +-----------------------------------------+ |
| | Shipping Cost as % of Sales by Region   | | Fulfillment Lead Time vs. Return Rate   | |
| +-----------------------------------------+ +-----------------------------------------+ |
+-----------------------------------------------------------------------------------------+
```

### 8.1 Key DAX Measures Planned
* `Total Sales = SUM(fact_orders[sales])`
* `Total Profit = SUM(fact_orders[profit])`
* `Profit Margin % = DIVIDE([Total Profit], [Total Sales], 0)`
* `Discount Drag = SUMX(fact_orders, fact_orders[gross_sales] - fact_orders[sales])`
* `Return Rate % = DIVIDE(CALCULATE(COUNTROWS(fact_orders), fact_orders[is_returned] = 1), COUNTROWS(fact_orders), 0)`
* `Shipping Overhead % = DIVIDE(SUM(fact_orders[shipping_cost]), [Total Sales], 0)`

---

## 9. Business KPI Reference Library

| KPI Name | Mathematical Formula | DAX Expression | Business Interpretation | Target Benchmark |
| :--- | :--- | :--- | :--- | :--- |
| **Gross Revenue** | $\sum \text{Gross Sales}$ | `SUM(fact_orders[gross_sales])` | Total list-price value before promotions. | Positive YoY Growth |
| **Net Revenue** | $\sum \text{Sales}$ | `SUM(fact_orders[sales])` | Actual top-line income collected. | Positive YoY Growth |
| **Cost of Goods Sold** | $\sum \text{COGS}$ | `SUM(fact_orders[cogs])` | Direct product sourcing cost. | Minimize as % of Sales |
| **Net Profit** | $\sum \text{Profit}$ | `SUM(fact_orders[profit])` | Net earnings after COGS and shipping. | Maximized |
| **Net Margin %** | $\frac{\text{Net Profit}}{\text{Net Revenue}}$ | `DIVIDE([Total Profit], [Total Sales], 0)` | Overall profitability efficiency. | $> 12\%$ |
| **Discount Rate %** | $\frac{\text{Discount Amount}}{\text{Gross Revenue}}$ | `DIVIDE([Discount Drag], [Gross Revenue], 0)` | Average promotional discount applied. | $< 15\%$ |
| **Discount Margin Erosion** | $\sum (\text{Gross Sales} - \text{Sales})$ | `[Gross Revenue] - [Total Sales]` | Dollar volume forfeited to discounts. | Monitored |
| **Return Rate %** | $\frac{\text{Returned Orders}}{\text{Total Orders}}$ | `DIVIDE([Returned Orders], [Total Orders], 0)` | Operational and customer dissatisfaction indicator. | $< 5\%$ |
| **Shipping-to-Sales Ratio** | $\frac{\text{Shipping Cost}}{\text{Net Revenue}}$ | `DIVIDE([Total Shipping], [Total Sales], 0)` | Freight burden on unit economics. | $< 8\%$ |
| **Fulfillment Lead Time** | $\text{Ship Date} - \text{Order Date}$ | `AVERAGE(fact_orders[lead_time_days])` | Operational speed and logistics SLA adherence. | $\le 4 \text{ Days}$ |

---

## 10. Proposed Project Directory Structure

```
Ecommerce-Profitability-Intelligence/
│
├── data/
│   ├── raw/                           # Pristine original dataset files
│   │   ├── global_superstore_orders.csv
│   │   └── global_superstore_returns.csv
│   ├── processed/                     # Cleaned, standardized dimensional CSVs
│   │   ├── dim_customers.csv
│   │   ├── dim_products.csv
│   │   ├── dim_geography.csv
│   │   ├── dim_date.csv
│   │   ├── dim_shipping_mode.csv
│   │   ├── fact_orders.csv
│   │   └── fact_returns.csv
│   └── data_dictionary.md             # Granular metadata and column descriptions
│
├── sql/
│   ├── 01_schema_ddl.sql              # Star schema table definitions, constraints, indexes
│   ├── 02_data_staging_load.sql       # Ingestion and copy commands
│   ├── 03_data_quality_assertions.sql # Automated validation assertions (nulls, ranges)
│   ├── 04_discount_elasticity.sql     # CTEs & window queries for discount thresholds
│   ├── 05_profit_bleeders_pareto.sql  # Cumulative margin and SKU loss analysis
│   ├── 06_customer_rfm_cohorts.sql    # RFM segmentation and cohort retention
│   └── 07_logistics_performance.sql   # Freight drag and fulfillment lead time queries
│
├── src/                               # Production Python codebase
│   ├── __init__.py
│   ├── config.py                      # Centralized directory paths and DB configs
│   ├── data_loader.py                 # File ingestion and parsing
│   ├── data_cleaner.py                # Type casting, missing values, deduplication
│   ├── data_validator.py              # Automated data quality checks
│   └── db_connector.py                # PostgreSQL connection engine (SQLAlchemy/psycopg2)
│
├── notebooks/                         # Interactive exploratory & statistical notebooks
│   ├── 01_data_audit_and_cleaning.ipynb
│   ├── 02_exploratory_data_analysis.ipynb
│   ├── 03_statistical_hypothesis_testing.ipynb
│   └── 04_econometric_discount_elasticity.ipynb
│
├── power_bi/
│   ├── dashboard_specification.md     # Wireframes, layout grid, color palette, DAX measures
│   ├── ecommerce_profitability.pbix   # Ready-to-publish Power BI dashboard file
│   └── screenshots/                   # Exported high-resolution UI views for portfolio
│
├── tests/                             # Unit tests for automated pipeline verification
│   ├── test_cleaning.py
│   └── test_metrics_calculation.py
│
├── docs/                              # Business documentation & interview presentation
│   ├── executive_summary.md           # C-level findings and strategic narrative
│   ├── business_recommendations.md    # Concrete, evidence-based operational interventions
│   └── interview_talking_points.md    # Step-by-step interview guide (STAR method)
│
├── requirements.txt                   # Frozen Python environment dependencies
├── .gitignore                         # Standard exclusion rules (caches, credentials, pyc)
├── PROJECT_PLAN.md                    # Master blueprint (this document)
└── README.md                          # High-impact GitHub portfolio presentation
```

---

## 11. Testing & Quality Assurance Strategy

1. **Pipeline Unit Testing (`tests/`):**
   * Verification of derived metric formulas (e.g., ensuring `COGS + Profit + Shipping Cost == Sales`).
   * Asserting zero negative quantities or discount values $> 1.0$.
2. **SQL vs. Python Reconciliation:**
   * Run parallel aggregation scripts in Python (pandas) and PostgreSQL to confirm identical totals for Gross Sales, Net Profit, and Order Counts across both systems.
3. **Power BI Model Testing:**
   * Validate DAX measure performance with Power BI Performance Analyzer.
   * Ensure star schema relationships are strictly $1:\text{Many}$ with single-directional cross-filtering to prevent circular dependency bugs or double-counting.

---

## 12. Deliverables & Interview Presentation Strategy

To ensure maximum impact during job placement interviews, the project provides:
1. **GitHub-Ready Codebase:** Clean, PEP8-compliant code, clear commit history, and professional directory structure.
2. **Executive Business Narrative:** Clear business recommendations (e.g., establishing a 20% discount cap on low-margin sub-categories like Tables and Binders; renegotiating freight contracts for remote zones).
3. **Interactive Power BI File (`.pbix`):** A modern, enterprise-grade business dashboard ready for live presentation.
4. **Interview Talking Points (`docs/interview_talking_points.md`):** Structured answers using the **STAR** (Situation, Task, Action, Result) methodology explaining technical architecture, analytical trade-offs, and business outcomes.

---

## 13. Implementation Milestones & Progress Tracking

```
+-------------------------------------------------------------------------------------+
| IMPLEMENTATION ROADMAP & STATUS                                                     |
+-------------------------------------------------------------------------------------+
| [COMPLETED] Milestone 1: Planning, Data Architecture & Quality Gate                 |
|   - Master architecture blueprint & metric feasibility analysis (PROJECT_PLAN.md).  |
|   - Ingestion & validation of Global Superstore dataset (51,290 orders, 1,079 returns)|
|   - Automated data profiling script (docs/data_profiling_report.md).                |
|   - PostgreSQL & SQLite Star Schema DDL with referential integrity.                 |
|   - Automated warehouse ETL with 100% financial balance ($0.00 delta).              |
|   - Public GitHub repository created: Chaitanya6006/ecommerce-profitability-...     |
+-------------------------------------------------------------------------------------+
| [COMPLETED] Milestone 2: Advanced SQL Analytics & Visualization Suite               |
|   - Executive Business KPI Scorecard (sql/02_executive_kpis.sql).                   |
|   - Sub-Category Unit Economics & Pareto Bleeders (sql/03_product_category...).     |
|   - Discount Elasticity & Margin Degradation Tiers (sql/04_discount_analysis.sql).  |
|   - Customer RFM Persona Segmentation with NTILE (sql/05_customer_rfm.sql).         |
|   - Multi-Year Customer Cohort Retention Matrix (sql/06_customer_cohorts.sql).      |
|   - Window Function Suite: RANK, DENSE_RANK, LAG, NTILE (sql/07_window_functions.sql)|
|   - Logistics Lead Times & Regional Freight Performance (sql/08_shipping_regional..)|
|   - Automated Reconciliation Quality Gate (sql/09_data_reconciliation.sql).        |
|   - Python Analytics Runner exporting 12 datasets to data/processed/analytics/.     |
|   - Executive Python Visualization Suite generating 5 charts in reports/figures/.   |
|   - Automated unit test suite: 12/12 tests passing in 0.14s.                         |
| [COMPLETED] Milestone 3: Python Advanced Statistical Analysis & Hypothesis Testing |
|   - Clearly defined units of analysis: Line Level (n=51,290) vs Order Level (n=25,728).|
|   - Hypothesis 1: Welch's t-test (t=127.11, p<0.001) & Mann-Whitney U on discount margin.|
|   - Hypothesis 2: Kruskal-Wallis (H=25,991, p<0.001, eta^2=0.683) across 5 discount tiers.|
|   - Pairwise Games-Howell post-hoc tests confirming significant divergence across all pairs.|
|   - Spearman Rank Correlation: line-level rho=-0.6691 and order-level rho=-0.6898 (p<0.001).|
|   - Hypothesis 3: Contingency Chi-Square test (chi2=4.31, p=0.116, Cramér's V=0.013) on |
|     order returns, proving discount depth does NOT significantly drive return rates. |
|   - Focused statistical figures generated in reports/figures/statistical/.          |
|   - Comprehensive analysis report generated in reports/statistical_analysis_report.md. |
|   - Automated test suite: 18/18 tests passing in 5.05s.                              |
+-------------------------------------------------------------------------------------+
| [COMPLETED] Milestone 4: Power BI Enterprise Dashboard Application                 |
|   - Kimball Star Schema data model documentation with 6 clean relationships (R1-R6).|
|   - Production DAX measures library (25+ measures across 6 functional folders).     |
|   - Power Query (M) automated ingestion scripts with DataFolderPath parameter.       |
|   - Complete 5-page UI/UX dashboard specifications and wireframes.                  |
|   - Custom corporate visual theme JSON with WCAG-accessible palette.                 |
|   - Step-by-step Power BI Desktop setup instructions and validation checklist.      |
|   - 100% financial and statistical reconciliation ($0.00 delta against warehouse).   |
+-------------------------------------------------------------------------------------+
| [NEXT] Milestone 5: Executive Business Synthesis & Interview Placement Guide        |
|   - Actionable commercial recommendations and STAR interview presentation notes.    |
+-------------------------------------------------------------------------------------+
```
