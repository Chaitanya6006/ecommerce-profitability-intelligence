# Power BI Model Audit & Validation Checklist
## E-Commerce Profitability Intelligence Platform

This validation protocol establishes an exhaustive quality gate for the **E-Commerce Profitability Intelligence** Power BI report. Every metric, relationship, filter propagation, and visual must reconcile with 100% precision against the analytical database benchmarks (PostgreSQL and SQLite) and the Python statistical analysis engine.

---

## 📋 Executive Quality Gate Summary

* **Source Database:** PostgreSQL 15+ / SQLite analytical warehouse (`data/ecommerce_profitability.db`)
* **Reference Python Scripts:** `src.data_profiler`, `src.db_connector`, `src.run_sql_analytics`, `src.statistical_analysis`
* **Target Precision:** **$0.00 dollar variance** across financial totals; **0.00% variance** across percentage metrics; **0 record discrepancy** across dimensional keys.

---

## 🗄️ Section 1: Data Model & Schema Verification

Verify that all tables and relationships in the **Model View** conform strictly to the star schema specifications:

| Check Item | Target Expected Specification | Verified Status | Notes / Diagnostic |
| :--- | :--- | :---: | :--- |
| **`fact_orders` Row Count** | Exactly **51,290 rows** | [ ] PASS | Transactional line item level. |
| **`fact_returns` Row Count** | Exactly **1,079 rows** | [ ] PASS | Distinct returned order events. |
| **`dim_customers` Row Count** | Exactly **17,415 rows** | [ ] PASS | Unique customer entities. |
| **`dim_products` Row Count** | Exactly **3,788 rows** | [ ] PASS | Distinct SKU catalog items. |
| **`dim_geography` Row Count** | Exactly **3,856 rows** | [ ] PASS | Distinct market/region/city entities. |
| **`dim_date` Row Count** | Exactly **1,468 rows** | [ ] PASS | 2012-01-01 through 2016-01-07 continuous calendar. |
| **`dim_shipping_mode` Row Count** | Exactly **4 rows** | [ ] PASS | Standard, Second, First, Same Day. |
| **Relationship R1 (`customer_key`)** | `fact_orders` $*:1$ `dim_customers` (Single) | [ ] PASS | Active, single-direction filter. |
| **Relationship R2 (`product_key`)** | `fact_orders` $*:1$ `dim_products` (Single) | [ ] PASS | Active, single-direction filter. |
| **Relationship R3 (`geography_key`)** | `fact_orders` $*:1$ `dim_geography` (Single) | [ ] PASS | Active, single-direction filter. |
| **Relationship R4 (`order_date_key`)**| `fact_orders` $*:1$ `dim_date` (Single) | [ ] PASS | Active, primary date filter. |
| **Relationship R5 (`ship_date_key`)** | `fact_orders` $*:1$ `dim_date` (Single) | [ ] PASS | **Inactive**, invoked via `USERELATIONSHIP()`. |
| **Relationship R6 (`shipping_mode`)** | `fact_orders` $*:1$ `dim_shipping_mode` (Single)| [ ] PASS | Active, single-direction filter. |
| **Returns Isolation Policy** | Zero bidirectional joins between facts | [ ] PASS | `fact_returns` isolated; order returns modeled via `is_returned`. |
| **Calendar Hierarchy Sort** | `dim_date[month_name]` sorted by `[month]` | [ ] PASS | Prevents alphabetical month sorting. |

---

## 💰 Section 2: Core KPI Measure Reconciliation

With all page slicers cleared (unfiltered state), compare the Power BI DAX card values against the database ground truth:

| DAX Measure | Power BI Card Display | Benchmark Ground Truth | Variance | Status |
| :--- | :---: | :---: | :---: | :---: |
| `[Total Sales]` | **\$12,642,501.91** | \$12,642,501.91 | **\$0.00** | [ ] PASS |
| `[Gross Sales]` | **\$15,006,490.23** | \$15,006,490.23 | **\$0.00** | [ ] PASS |
| `[Total COGS]` | **\$9,816,960.80** | \$9,816,960.80 | **\$0.00** | [ ] PASS |
| `[Total Shipping Cost]` | **\$1,358,085.70** | \$1,358,085.70 | **\$0.00** | [ ] PASS |
| `[Net Profit]` | **\$1,467,457.29** | \$1,467,457.29 | **\$0.00** | [ ] PASS |
| `[Profit Margin %]` | **11.61%** | 11.6073% | **0.00%** | [ ] PASS |
| `[Discount Concession $]` | **\$2,363,988.32** | \$2,363,988.32 | **\$0.00** | [ ] PASS |
| `[Effective Discount Rate %]` | **15.75%** | 15.7531% | **0.00%** | [ ] PASS |
| `[Total Line Items]` | **51,290** | 51,290 | **0** | [ ] PASS |
| `[Distinct Orders]` | **25,728** | 25,728 | **0** | [ ] PASS |
| `[Total Quantity Sold]` | **178,312** | 178,312 | **0** | [ ] PASS |
| `[Average Order Value]` | **\$491.39** | \$491.3908 | **\$0.00** | [ ] PASS |
| `[Total Customers]` | **17,415** | 17,415 | **0** | [ ] PASS |
| `[Returned Orders]` | **1,079** | 1,079 | **0** | [ ] PASS |
| `[Order Return Rate %]` | **4.19%** | 4.1939% | **0.00%** | [ ] PASS |
| `[Line Return Rate %]` | **4.33%** | 4.3283% | **0.00%** | [ ] PASS |
| `[Sales Exposed to Returns $]`| **\$525,932.23** | \$525,932.23 | **\$0.00** | [ ] PASS |
| `[Average Lead Time Days]` | **3.97 Days** | 3.9691 Days | **0.00 Days** | [ ] PASS |

---

## 🔍 Section 3: Visual & Analytical Cross-Checks

Audit specific analytical findings on each dashboard page to guarantee alignment with SQL and statistical conclusions:

### Page 1: Executive Overview
- [ ] **Sales vs Profit Trend:** Monthly peak occurs in November 2015 ($649.8K Sales, $72.4K Profit).
- [ ] **Category P&L Rankings:**
  * Technology: Sales **\$4,744,557**, Profit **\$663,779** (Margin: **14.0%**)
  * Office Supplies: Sales **\$3,787,070**, Profit **\$518,474** (Margin: **13.7%**)
  * Furniture: Sales **\$4,110,875**, Profit **\$285,205** (Margin: **6.9%**)
- [ ] **Global Market Slicing:** APAC leads sales with **\$3,585,744**, followed by EU with **\$2,938,298**.

### Page 2: Merchandising Profitability & Bleeders
- [ ] **Top Profitable Sub-Categories:**
  * Copiers: **+\$258,567.55** net profit (Margin: **17.2%**)
  * Phones: **+\$216,717.01** net profit (Margin: **12.7%**)
  * Bookcases: Positive overall (**+\$161,924.42**), but heavy margin erosion in select regions.
- [ ] **Top Profit Bleeder Sub-Category:**
  * Tables: **-\$64,083.39** net operating loss across the catalog (Margin: **-8.56%**).
- [ ] **Worst Bleeder SKU in Audit Table:**
  * `Lesro Conference Table` / `Chromcraft Conference Table` showing cumulative losses $> \$3,000$ each.

### Page 3: Customer Intelligence & Segment Economics
- [ ] **Customer Segment Revenue Share:**
  * Consumer: **\$6,507,949** (51.5% of GMV, Profit: **\$749,240**, Margin: **11.5%**)
  * Corporate: **\$3,824,696** (30.3% of GMV, Profit: **\$442,785**, Margin: **11.6%**)
  * Home Office: **\$2,309,857** (18.3% of GMV, Profit: **\$275,432**, Margin: **11.9%**)
- [ ] **Customer Persona Distribution:**
  * 4,427 customers classified as "Margin Drainers" generating aggregate operating losses of **-\$773,201**.

### Page 4: Discount Impact & Price Elasticity
- [ ] **Margin Collapse Threshold:**
  * Discount Tier `0%` (Undiscounted): Net Margin = **+26.49%**
  * Discount Tier `0.01 - 0.10`: Net Margin = **+16.32%**
  * Discount Tier `0.11 - 0.20`: Net Margin = **+9.45%**
  * Discount Tier `0.21 - 0.30`: Net Margin collapses to **-17.33%**
  * Discount Tier `> 0.30`: Severe deficit at **-86.77%**
- [ ] **Independence of Returns:**
  * Return rate across discount tiers remains tightly bounded between **3.98%** and **4.53%**, confirming that promotional pricing does not drive buyer remorse or excess returns ($\chi^2 = 4.31, p = 0.116$).
- [ ] **What-If Parameter Simulation:**
  * Setting `Discount Cap` slider to **20%** yields `[Simulated Profit (Static 20% Cap)]` of **\$2,499,943.84** (a static mathematical upper bound lift of **+\$1,032,486.55** assuming constant demand).
  * In the conservative elasticity-adjusted model, `[Simulated Profit (Elasticity-Adjusted)]` yields **\$1,715,254.06**, representing a realistic `[Realistic Profit Lift]` recovery of **+\$247,796.77 (~+\$248.5K)** after price-sensitivity volume attrition.

### Page 5: Regional Logistics & Shipping Analytics
- [ ] **Fulfillment Mode Distribution:**
  * Standard Class: **30,775 orders** (60.0%), Avg Lead Time: **5.01 Days**
  * Second Class: **10,309 orders** (20.1%), Avg Lead Time: **3.24 Days**
  * First Class: **7,505 orders** (14.6%), Avg Lead Time: **2.18 Days**
  * Same Day: **2,701 orders** (5.3%), Avg Lead Time: **0.04 Days**
- [ ] **Shipping Expense Ratio:** Overall logistics freight accounts for **10.74%** of net revenue (\$1.36M).

---

## ⚡ Section 4: Performance & Engine Governance

Verify report responsiveness and VertiPaq efficiency using Power BI Performance Analyzer:

- [ ] **Visual Render Latency:** Every visual on all 5 pages completes query execution in $< 500\text{ ms}$ under cold cache, and $< 100\text{ ms}$ under warm cache.
- [ ] **No Bi-Directional Cross-Filtering:** No ambiguous relationship paths exist; model contains zero circular dependencies.
- [ ] **DAX Measure Optimization:** No unbounded iterative functions (e.g., `SUMX` iterating over entire `fact_orders` when a simple `SUM` or pre-aggregated filter suffices).
- [ ] **Memory Footprint:** In-memory compressed size of `.pbix` remains under $35\text{ MB}$.

---

## ✍️ Section 5: Sign-Off Quality Gate

| Role | Reviewer | Sign-Off Date | Outcome |
| :--- | :--- | :---: | :---: |
| **Analytics Engineer** | Lead BI Developer | YYYY-MM-DD | [ ] APPROVED |
| **Commercial Finance Lead** | Senior Business Analyst | YYYY-MM-DD | [ ] APPROVED |
| **Technical Project Architect** | Solutions Architect | YYYY-MM-DD | [ ] APPROVED |
