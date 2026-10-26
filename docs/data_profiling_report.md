# Data Profiling & Quality Audit Report
## E-Commerce Profitability Intelligence Platform
**Generated:** Automatically by `src/data_profiler.py`

---
### 1. Dataset Overview & Dimensions
- **Orders Table:** 51,290 rows, 24 columns
- **Returns Table:** 1,079 rows, 3 columns
- **Orders Primary Key Candidate (`Row ID`):** 51,290 unique values (100% unique = True)
- **Distinct Orders (`Order ID`):** 25,728 unique order IDs
- **Distinct Customers (`Customer ID`):** 17,415 unique customer accounts
- **Distinct Products (`Product ID`):** 3,788 unique catalog items

### 2. Missing Value & Nullity Audit
| Table | Column Name | Data Type | Null Count | Null % | Remediation Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Orders | `Row ID` | `int64` | 0 | 0.00% | Clean (0 nulls) |
| Orders | `Order ID` | `str` | 0 | 0.00% | Clean (0 nulls) |
| Orders | `Order Date` | `str` | 0 | 0.00% | Clean (0 nulls) |
| Orders | `Ship Date` | `str` | 0 | 0.00% | Clean (0 nulls) |
| Orders | `Ship Mode` | `str` | 0 | 0.00% | Clean (0 nulls) |
| Orders | `Customer ID` | `str` | 0 | 0.00% | Clean (0 nulls) |
| Orders | `Customer Name` | `str` | 0 | 0.00% | Clean (0 nulls) |
| Orders | `Segment` | `str` | 0 | 0.00% | Clean (0 nulls) |
| Orders | `Postal Code` | `float64` | 41,296 | 80.51% | Retain; impute 'UNKNOWN' for non-US records (expected geographic limitation) |
| Orders | `City` | `str` | 0 | 0.00% | Clean (0 nulls) |
| Orders | `State` | `str` | 0 | 0.00% | Clean (0 nulls) |
| Orders | `Country` | `str` | 0 | 0.00% | Clean (0 nulls) |
| Orders | `Region` | `str` | 0 | 0.00% | Clean (0 nulls) |
| Orders | `Market` | `str` | 0 | 0.00% | Clean (0 nulls) |
| Orders | `Product ID` | `str` | 0 | 0.00% | Clean (0 nulls) |
| Orders | `Category` | `str` | 0 | 0.00% | Clean (0 nulls) |
| Orders | `Sub-Category` | `str` | 0 | 0.00% | Clean (0 nulls) |
| Orders | `Product Name` | `str` | 0 | 0.00% | Clean (0 nulls) |
| Orders | `Sales` | `float64` | 0 | 0.00% | Clean (0 nulls) |
| Orders | `Quantity` | `int64` | 0 | 0.00% | Clean (0 nulls) |
| Orders | `Discount` | `float64` | 0 | 0.00% | Clean (0 nulls) |
| Orders | `Profit` | `float64` | 0 | 0.00% | Clean (0 nulls) |
| Orders | `Shipping Cost` | `float64` | 0 | 0.00% | Clean (0 nulls) |
| Orders | `Order Priority` | `str` | 0 | 0.00% | Clean (0 nulls) |
| Returns | `Returned` | `str` | 0 | 0.00% | Clean (0 nulls) |
| Returns | `Order ID` | `str` | 0 | 0.00% | Clean (0 nulls) |
| Returns | `Region` | `str` | 0 | 0.00% | Clean (0 nulls) |

### 3. Duplicate Record Audit
- **Exact Row Duplicates in Orders:** 0
- **Order ID + Product ID Multi-Line Occurrences:** 42 (Multiple units or split shipments for same SKU in single order)
- **Exact Row Duplicates in Returns:** 0

### 4. Date Logic & Fulfillment Lifecycle Audit
- **Temporal Span:** 2012-01-01 to 2015-12-31 (4 full fiscal years)
- **Order Date Parsing Nulls:** 0
- **Ship Date Parsing Nulls:** 0
- **Logical Violations (Ship Date < Order Date):** 0 (Must be 0)
- **Fulfillment Lead Time (Days):** Min = 0 days, Median = 4 days, Mean = 3.97 days, Max = 7 days

### 5. Financial & Quantity Numeric Range Audit
| Metric Column | Min | 25th % | Median | 75th % | Max | Mean | Negative Count | Suspicious Values / Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Sales` | 0.44 | 30.76 | 85.05 | 251.05 | 22638.48 | 246.49 | 0 | Valid |
| `Quantity` | 1.00 | 2.00 | 3.00 | 5.00 | 14.00 | 3.48 | 0 | Valid |
| `Discount` | 0.00 | 0.00 | 0.00 | 0.20 | 0.85 | 0.14 | 0 | Valid |
| `Profit` | -6599.98 | 0.00 | 9.24 | 36.81 | 8399.98 | 28.61 | 12,544 | Normal business losses (12,544 unprofitable transactions, 24.5%) |
| `Shipping Cost` | 1.00 | 2.61 | 7.79 | 24.45 | 933.57 | 26.48 | 0 | Valid |

### 6. Returns Data Integration & Order Matching
- **Distinct Order IDs in Returns Table:** 1,079
- **Matched Order IDs in Orders Table:** 1,079 (100.0% match rate)
- **Total Order Line Items Impacted by Returns:** 2,220 (4.33% of all line items)
- **Gross Sales Exposed to Returns:** $525,932.23 (4.16% of total enterprise GMV)

### 7. Explicit Metric Feasibility Matrix
Strictly separates fields available in the actual dataset from derived metrics and highlights external business metrics that cannot be calculated without speculation.

#### A. Fully Feasible Metrics (Directly Calculable from Available Columns)
| Proposed Metric | Source Columns | Mathematical Calculation | Feasibility Status |
| :--- | :--- | :--- | :--- |
| **Net Sales Revenue** | `Sales` | `SUM(Sales)` | 100% Feasible |
| **Gross Sales (List Price)** | `Sales`, `Discount` | `Sales / (1 - Discount)` | 100% Feasible |
| **Discount Dollar Concession** | `Sales`, `Discount` | `Gross Sales - Sales` | 100% Feasible |
| **COGS (Cost of Goods Sold)** | `Sales`, `Profit`, `Shipping Cost` | `Sales - Profit - Shipping Cost` | 100% Feasible (Unit Economics Balance) |
| **Gross Profit** | `Sales`, `COGS` | `Sales - COGS` | 100% Feasible |
| **Net Profit** | `Profit` | `SUM(Profit)` | 100% Feasible |
| **Net Profit Margin %** | `Profit`, `Sales` | `(SUM(Profit) / SUM(Sales)) * 100` | 100% Feasible |
| **Shipping Cost Burden %** | `Shipping Cost`, `Sales` | `(SUM(Shipping Cost) / SUM(Sales)) * 100` | 100% Feasible |
| **Fulfillment Lead Time (Days)**| `Order Date`, `Ship Date` | `Ship Date - Order Date` | 100% Feasible |
| **Return Rate % (by Order)** | `Order ID`, `Returns.Order ID`| `Count(Returned Orders) / Count(Total Orders)` | 100% Feasible |
| **Customer RFM Scores** | `Customer ID`, `Order Date`, `Profit` | Window/Quantile Recency, Frequency, Monetary | 100% Feasible |
| **Customer Cohort Retention** | `Customer ID`, `Order Date` | Min(Order Date) partition by customer | 100% Feasible |
| **Category Profit Bleeders** | `Product ID`, `Sub-Category`, `Profit` | Running cumulative profit loss | 100% Feasible |

#### B. Infeasible Metrics (Data Limitations - Not Present in Dataset)
| Metric | Required But Missing Data | Analytical Alternative / Recommendation |
| :--- | :--- | :--- |
| **Customer Acquisition Cost (CAC)** | Marketing advertising spend, campaign costs by channel | **Do NOT invent marketing spend.** Evaluate customer acquisition by cohort vintage and repeat order organic conversion instead. |
| **Return Restocking & Reverse Freight Fee** | Return carrier shipping invoices, restocking labor expense | **Do NOT invent reverse freight cost.** Quantify return impact via forfeited revenue and gross profit margin at risk. |
| **Warehouse Inventory Turnover & Stockouts**| Beginning/ending inventory count, stockout logs | **Do NOT invent warehouse stock.** Focus logistics analysis on fulfillment lead times and carrier shipping tier performance. |
| **Customer Demographic Profiling** | Age, gender, household income | Use native **`Segment`** (`Consumer`, `Corporate`, `Home Office`) and geographical markets. |
