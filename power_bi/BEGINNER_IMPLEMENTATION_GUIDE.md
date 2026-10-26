# Beginner's Step-by-Step Power BI Implementation Guide
## E-Commerce Profitability Intelligence Platform

This guide provides click-by-click instructions to build the complete, interactive **5-page E-Commerce Profitability Intelligence** dashboard in Microsoft Power BI Desktop from scratch.

No prior advanced Power BI experience is required. Every menu name, button, and field name matches the official Microsoft Power BI Desktop interface.

---

## 📋 Table of Contents
1. [Which CSV Files to Import (and What NOT to Import)](#1-which-csv-files-to-import-and-what-not-to-import)
2. [Step 1: Import the Clean Star Schema Tables](#step-1-import-the-clean-star-schema-tables)
3. [Step 2: Verify & Configure Data Types](#step-2-verify--configure-data-types)
4. [Step 3: Build the Data Model Relationships (Model View)](#step-3-build-the-data-model-relationships-model-view)
5. [Step 4: Configure the Date Table & Month Sorting](#step-4-configure-the-date-table--month-sorting)
6. [Step 5: Import the Corporate Color Theme](#step-5-import-the-corporate-color-theme)
7. [Step 6: Create the Centralized DAX Measures Table](#step-6-create-the-centralized-dax-measures-table)
8. [Step 7: Add the What-If Discount Cap Parameter](#step-7-add-the-what-if-discount-cap-parameter)
9. [Step 8: Build the 5 Dashboard Pages (Visual by Visual)](#step-8-build-the-5-dashboard-pages-visual-by-visual)
10. [Step 9: Save the Report & Export Screenshots](#step-9-save-the-report--export-screenshots)
11. [Step 10: Compare Power BI Values Against Validated SQL Benchmarks](#step-10-compare-power-bi-values-against-validated-sql-benchmarks)

---

## 1. Which CSV Files to Import (and What NOT to Import)

### ✅ The 6 Files You MUST Import
Navigate to your project folder: `data/processed/` and import **ONLY** these 6 dimensional and fact files:

| File Name | Table Type | Rows | Why It Is Required |
| :--- | :---: | :---: | :--- |
| **`fact_orders.csv`** | Fact | 51,290 | Contains every transaction line item, revenue, cost, discount, and the `is_returned` flag. |
| **`dim_customers.csv`** | Dimension | 17,415 | Contains customer IDs, names, and market segments (`Consumer`, `Corporate`, `Home Office`). |
| **`dim_products.csv`** | Dimension | 3,788 | Contains product IDs, catalog names, categories, and sub-categories. |
| **`dim_geography.csv`** | Dimension | 3,856 | Contains city, state, country, region, and market hierarchies. |
| **`dim_date.csv`** | Dimension | 1,468 | Continuous calendar table from 2012 to 2016 for time intelligence. |
| **`dim_shipping_mode.csv`**| Dimension | 4 | Carrier delivery tiers (`Standard Class`, `Second Class`, `First Class`, `Same Day`). |

---

### ❌ What NOT to Import (and Why)

1. **DO NOT import `data/processed/fact_returns.csv`:**
   * *Why:* `fact_orders.csv` already contains the `is_returned` column (1 = returned, 0 = retained) pre-joined during ETL. If you import `fact_returns.csv` and attempt to link it on `order_id`, Power BI will create a **Many-to-Many bidirectional relationship**, which causes non-deterministic totals, duplicate row counts, and severe performance slowdowns. All return metrics in this project are computed safely and directly on `fact_orders`.
2. **DO NOT import any file from `data/processed/analytics/`:**
   * *Why:* The 12 files in `data/processed/analytics/` (such as `category_profitability.csv` or `executive_kpis.csv`) are **pre-aggregated SQL summary exports**. Importing pre-aggregated summaries into a star-schema model causes circular dependencies, duplicate numbers, and breaks dynamic slicer filtering (for example, slicing by Year will not filter a pre-aggregated category table). Power BI calculates all aggregations dynamically on the star schema using DAX!

---

## Step 1: Import the Clean Star Schema Tables

1. Open **Microsoft Power BI Desktop**.
2. If a splash screen appears, close it or click **Get data**.
3. On the **Home** ribbon at the top, click **Get data** > **Text/CSV**.
4. Browse to your local project folder:
   `c:\Users\Admin\Desktop\Ecommerce-Profitability-Intelligence\data\processed\`
5. Select `fact_orders.csv` and click **Open**.
6. In the preview window, look at the bottom right:
   * **Do NOT click Load yet.**
   * Click **Transform Data** (this opens Power Query Editor).
7. Now, inside the **Power Query Editor**:
   * Click **New Source** (top left on the Home ribbon) > **Text/CSV**.
   * Import each of the remaining 5 files one by one:
     * `dim_customers.csv`
     * `dim_products.csv`
     * `dim_geography.csv`
     * `dim_date.csv`
     * `dim_shipping_mode.csv`
8. You will now see 6 queries listed in the left pane of Power Query Editor.

---

## Step 2: Verify & Configure Data Types

Power Query usually detects column types automatically, but we must ensure financial and key columns are typed correctly to prevent calculation errors.

In the Power Query Editor, click on each table in the left pane and check the icon in the column headers:
* `123` = Whole Number
* `1.2` = Decimal Number
* `$` = Fixed Decimal Number (Currency)
* `ABC` = Text
* 📅 = Date

### Configure Table Columns:

1. **`fact_orders`**:
   * `row_id`, `customer_key`, `product_key`, `geography_key`, `order_date_key`, `ship_date_key`, `shipping_mode_key`: **Whole Number (`123`)**
   * `order_id`, `order_priority`: **Text (`ABC`)**
   * `sales`, `profit`, `shipping_cost`, `gross_sales`, `discount_amount`, `cogs`: **Fixed Decimal Number (`$`)** or **Decimal Number (`1.2`)**
   * `discount`: **Decimal Number (`1.2`)**
   * `quantity`, `lead_time_days`, `is_returned`: **Whole Number (`123`)**
2. **`dim_customers`**:
   * `customer_key`: **Whole Number (`123`)**
   * `customer_id`, `customer_name`, `segment`: **Text (`ABC`)**
3. **`dim_products`**:
   * `product_key`: **Whole Number (`123`)**
   * `product_id`, `product_name`, `category`, `sub_category`: **Text (`ABC`)**
4. **`dim_geography`**:
   * `geography_key`: **Whole Number (`123`)**
   * `city`, `state`, `country`, `region`, `market`, `postal_code`: **Text (`ABC`)**
5. **`dim_date`**:
   * `date_key`, `day_of_month`, `month`, `quarter`, `year`, `is_weekend`: **Whole Number (`123`)**
   * `full_date`: **Date (📅)**
   * `month_name`, `day_of_week`: **Text (`ABC`)**
6. **`dim_shipping_mode`**:
   * `shipping_mode_key`: **Whole Number (`123`)**
   * `ship_mode`: **Text (`ABC`)**

When finished, click **Close & Apply** (top left on the Home ribbon). Power BI will load the tables into memory.

---

## Step 3: Build the Data Model Relationships (Model View)

1. On the far left vertical navigation bar of Power BI Desktop, click the **Model view** icon (the 3rd icon down, showing connected tables).
2. Look at the diagram canvas. If Power BI automatically created any relationships, review them. If any relationship connects to the wrong column, right-click the line and select **Delete**.
3. Arrange your tables so that `fact_orders` is in the center, and the 5 dimension tables are surrounding it.
4. Create the **6 relationships** by clicking a column in `fact_orders` and dragging it onto the matching column in the dimension table:

| From (`fact_orders`) | To (Dimension Table) | Cardinality | Cross filter direction | Active? |
| :--- | :--- | :---: | :---: | :---: |
| `customer_key` | `dim_customers[customer_key]` | Many to one (`*:1`) | Single | **Yes** |
| `product_key` | `dim_products[product_key]` | Many to one (`*:1`) | Single | **Yes** |
| `geography_key` | `dim_geography[geography_key]` | Many to one (`*:1`) | Single | **Yes** |
| `order_date_key` | `dim_date[date_key]` | Many to one (`*:1`) | Single | **Yes** |
| `ship_date_key` | `dim_date[date_key]` | Many to one (`*:1`) | Single | **No (Inactive)** |
| `shipping_mode_key` | `dim_shipping_mode[shipping_mode_key]`| Many to one (`*:1`) | Single | **Yes** |

> **How to make the 5th relationship Inactive:** Double-click the relationship line between `fact_orders[ship_date_key]` and `dim_date[date_key]`. In the Edit Relationship dialog, **uncheck** the box labeled *"Make this relationship active"* and click **OK**. The line will become a dotted line. (This inactive relationship is invoked in DAX when analyzing dispatch dates rather than order dates).

---

## Step 4: Configure the Date Table & Month Sorting

To ensure time-intelligence functions work reliably and months appear chronologically (January, February...) rather than alphabetically:

1. Switch to the **Table view** (the 2nd icon on the left bar).
2. In the **Data** pane on the right, click `dim_date`.
3. In the top ribbon, click the **Table tools** tab > click **Mark as date table** > **Mark as date table**.
   * In the dialog, set **Date column** to `full_date`.
   * Click **OK**.
4. In the `dim_date` table, click the column header for **`month_name`**.
5. In the top ribbon, click the **Column tools** tab > click **Sort by column** > select **`month`**.
   *(Now charts will display January to December in chronological order!)*

---

## Step 5: Import the Corporate Color Theme

1. Switch to the **Report view** (the 1st icon on the left bar, canvas view).
2. In the top ribbon, click the **View** tab.
3. In the **Themes** dropdown gallery, click the small down arrow > select **Browse for themes**.
4. Browse to:
   `c:\Users\Admin\Desktop\Ecommerce-Profitability-Intelligence\power_bi\theme\corporate_theme.json`
5. Click **Open**. A dialog will confirm: *"Theme imported successfully."*

---

## Step 6: Create the Centralized DAX Measures Table

To keep all business logic organized in one place, we create a dedicated measure storage table called `_Measures`:

1. On the **Home** ribbon, click **Enter Data** (an empty grid will pop up).
2. At the bottom, change the table name from `Table` to **`_Measures`**.
3. Click **Load** (do not type anything into the grid).
4. In the **Data** pane on the right, right-click `_Measures` and select **New measure**.
5. In the formula bar that appears at the top, paste each measure below and press **Enter**.
6. Set the **Format** in the **Measure tools** ribbon for each measure as listed.

---

### Group A: Core Financial Measures

#### 1. `Total Sales`
```dax
Total Sales = SUM(fact_orders[sales])
```
* **Format:** Currency (`$#,##0.00`)
* **Expected Value:** `$12,642,501.91`

#### 2. `Gross Sales`
```dax
Gross Sales = SUM(fact_orders[gross_sales])
```
* **Format:** Currency (`$#,##0.00`)
* **Expected Value:** `$15,006,490.23`

#### 3. `Total COGS`
```dax
Total COGS = SUM(fact_orders[cogs])
```
* **Format:** Currency (`$#,##0.00`)
* **Expected Value:** `$9,816,960.80`

#### 4. `Net Profit`
```dax
Net Profit = SUM(fact_orders[profit])
```
* **Format:** Currency (`$#,##0.00`)
* **Expected Value:** `$1,467,457.29`

#### 5. `Profit Margin %`
```dax
Profit Margin % = DIVIDE([Net Profit], [Total Sales], 0)
```
* **Format:** Percentage (`0.0%`)
* **Expected Value:** `11.6%`

#### 6. `Discount Concession $`
```dax
Discount Concession $ = SUM(fact_orders[discount_amount])
```
* **Format:** Currency (`$#,##0.00`)
* **Expected Value:** `$2,363,988.32`

#### 7. `Effective Discount Rate %`
```dax
Effective Discount Rate % = DIVIDE([Discount Concession $], [Gross Sales], 0)
```
* **Format:** Percentage (`0.0%`)
* **Expected Value:** `15.8%`

---

### Group B: Order Volume & Basket Size Metrics

#### 8. `Total Line Items`
```dax
Total Line Items = COUNTROWS(fact_orders)
```
* **Format:** Whole Number (`#,##0`)
* **Expected Value:** `51,290`

#### 9. `Distinct Orders`
```dax
Distinct Orders = DISTINCTCOUNT(fact_orders[order_id])
```
* **Format:** Whole Number (`#,##0`)
* **Expected Value:** `25,728`

#### 10. `Total Quantity Sold`
```dax
Total Quantity Sold = SUM(fact_orders[quantity])
```
* **Format:** Whole Number (`#,##0`)
* **Expected Value:** `178,312`

#### 11. `Average Order Value`
```dax
Average Order Value = DIVIDE([Total Sales], [Distinct Orders], 0)
```
* **Format:** Currency (`$#,##0.00`)
* **Expected Value:** `$491.39`

#### 12. `Average Basket Size`
```dax
Average Basket Size = DIVIDE([Total Quantity Sold], [Distinct Orders], 0)
```
* **Format:** Decimal Number (`0.0`)
* **Expected Value:** `6.9`

---

### Group C: Returns Intelligence

#### 13. `Returned Orders`
```dax
Returned Orders = 
CALCULATE(
    DISTINCTCOUNT(fact_orders[order_id]),
    fact_orders[is_returned] = 1
)
```
* **Format:** Whole Number (`#,##0`)
* **Expected Value:** `1,079`

#### 14. `Order Return Rate %`
```dax
Order Return Rate % = DIVIDE([Returned Orders], [Distinct Orders], 0)
```
* **Format:** Percentage (`0.00%`)
* **Expected Value:** `4.19%`

#### 15. `Returned Line Items`
```dax
Returned Line Items = 
CALCULATE(
    COUNTROWS(fact_orders),
    fact_orders[is_returned] = 1
)
```
* **Format:** Whole Number (`#,##0`)
* **Expected Value:** `2,220`

#### 16. `Line Item Return Rate %`
```dax
Line Item Return Rate % = DIVIDE([Returned Line Items], [Total Line Items], 0)
```
* **Format:** Percentage (`0.00%`)
* **Expected Value:** `4.33%`

#### 17. `Sales Exposed to Returns $`
```dax
Sales Exposed to Returns $ = 
CALCULATE(
    [Total Sales],
    fact_orders[is_returned] = 1
)
```
* **Format:** Currency (`$#,##0.00`)
* **Expected Value:** `$525,932.23`

---

### Group D: Logistics & Lead Time Metrics

#### 18. `Total Shipping Cost`
```dax
Total Shipping Cost = SUM(fact_orders[shipping_cost])
```
* **Format:** Currency (`$#,##0.00`)
* **Expected Value:** `$1,358,085.70`

#### 19. `Freight Burden %`
```dax
Freight Burden % = DIVIDE([Total Shipping Cost], [Total Sales], 0)
```
* **Format:** Percentage (`0.0%`)
* **Expected Value:** `10.7%`

#### 20. `Average Lead Time (Days)`
```dax
Average Lead Time (Days) = AVERAGE(fact_orders[lead_time_days])
```
* **Format:** Decimal Number (`0.0`)
* **Expected Value:** `3.97`

---

### Group E: What-If Discount Simulation Measures

#### 21. `Simulated Profit (Static 20% Cap)`
```dax
Simulated Profit (Static 20% Cap) = 
SUMX(
    fact_orders,
    VAR OriginalDiscount = fact_orders[discount]
    VAR CappedDiscount = MIN(OriginalDiscount, 0.20)
    VAR PriceLiftRatio = IF(OriginalDiscount > 0.20, (1 - CappedDiscount) / (1 - OriginalDiscount), 1)
    VAR SimulatedSales = fact_orders[sales] * PriceLiftRatio
    RETURN SimulatedSales - fact_orders[cogs] - fact_orders[shipping_cost]
)
```
* **Format:** Currency (`$#,##0.00`)
* **Expected Value:** `$2,499,943.84`
* **Note:** This represents the **theoretical maximum static profit** assuming unit sales volume remains 100% constant.

#### 22. `Static Profit Lift`
```dax
Static Profit Lift = [Simulated Profit (Static 20% Cap)] - [Net Profit]
```
* **Format:** Currency (`$#,##0.00`)
* **Expected Value:** `+$1,032,486.55`

#### 23. `Simulated Profit (Elasticity-Adjusted)`
```dax
Simulated Profit (Elasticity-Adjusted) = 
[Net Profit] + ([Static Profit Lift] * 0.24)
```
* **Format:** Currency (`$#,##0.00`)
* **Expected Value:** `$1,715,254.06`
* **Note:** This represents the **realistic recovery estimate** assuming price elasticity reduces customer order volume, capturing ~24% of the static price lift.

#### 24. `Realistic Profit Lift`
```dax
Realistic Profit Lift = [Simulated Profit (Elasticity-Adjusted)] - [Net Profit]
```
* **Format:** Currency (`$#,##0.00`)
* **Expected Value:** `+$247,796.77` (~`+$248.5K`)

---

### Cleaning Up the `_Measures` Table:
Once you have created your measures, right-click `Column1` inside the `_Measures` table in the Data pane and select **Delete from model**.
*(The table icon will transform into a calculator icon and jump to the very top of your Data pane!)*

---

## Step 7: Add the What-If Discount Cap Parameter

To enable the interactive discount slider on Page 4:

1. In the top ribbon, click the **Modeling** tab.
2. Click **New parameter** > select **Numeric range**.
3. In the dialog box that appears, enter:
   * **Name:** `Discount Cap`
   * **Data type:** `Decimal number`
   * **Minimum:** `0`
   * **Maximum:** `0.50`
   * **Increment:** `0.05`
   * **Default:** `0.20`
   * Ensure the checkbox **Add slicer to this page** is checked.
4. Click **Create**.
5. Power BI will create a calculated table with a slicer on your canvas. Cut this slicer (`Ctrl + X`) and save it for Page 4.

---

## Step 8: Build the 5 Dashboard Pages (Visual by Visual)

At the bottom of the canvas, double-click the page tab `Page 1` and rename it to **Executive Overview**. Use the `+` button to create 4 more pages:
* Page 1: `Executive Overview`
* Page 2: `Profitability Intelligence`
* Page 3: `Customer Intelligence`
* Page 4: `Discount Impact`
* Page 5: `Regional Logistics`

---

### 📄 PAGE 1: EXECUTIVE OVERVIEW

#### A. Top Slicers (Top Right of Page)
1. Add a **Slicer** visual (Visualizations pane > Slicer icon).
   * **Field:** Drag `dim_date[year]` into the **Field** well.
   * Format visual > Slicer settings > Style: **Dropdown** or **Tile**.
2. Add a second **Slicer** visual.
   * **Field:** Drag `dim_geography[market]` into the **Field** well.
   * Style: **Dropdown**.

#### B. Top KPI Card Row (5 Card Visuals)
Add 5 **Card** visuals across the top:
* **Card 1:** Field = `[Total Sales]` (Displays `$12.64M`)
* **Card 2:** Field = `[Net Profit]` (Displays `$1.47M`)
* **Card 3:** Field = `[Profit Margin %]` (Displays `11.6%`)
* **Card 4:** Field = `[Distinct Orders]` (Displays `25,728`)
* **Card 5:** Field = `[Order Return Rate %]` (Displays `4.19%`)

#### C. Monthly Sales vs. Profit Trend (Area / Line Chart)
1. Add an **Area chart** or **Line chart** visual.
2. Drag fields into the wells:
   * **X-axis:** `dim_date[year]` and `dim_date[month_name]`
   * **Y-axis:** `[Total Sales]` and `[Net Profit]`
3. In **Format visual** > Lines > Color: Set `[Total Sales]` to Corporate Navy (`#1B365D`) and `[Net Profit]` to Emerald Green (`#2CA02C`).

#### D. Category P&L Contribution (Clustered Bar Chart)
1. Add a **Clustered bar chart** visual.
2. Drag fields:
   * **Y-axis:** `dim_products[category]`
   * **X-axis:** `[Total Sales]` and `[Net Profit]`

#### E. Sales by Global Market (Clustered Column Chart)
1. Add a **Clustered column chart** visual.
2. Drag fields:
   * **X-axis:** `dim_geography[market]`
   * **Y-axis:** `[Total Sales]` and `[Net Profit]`

---

### 📄 PAGE 2: PROFITABILITY INTELLIGENCE & BLEEDERS

#### A. Sub-Category Profitability Waterfall / Ranking (Bar Chart)
1. Add a **Clustered bar chart** visual.
2. Drag fields:
   * **Y-axis:** `dim_products[sub_category]`
   * **X-axis:** `[Net Profit]`
3. **Conditional Formatting for Profit vs Loss:**
   * In the **Format visual** pane, go to **Bars** > click the **fx** button next to **Color**.
   * Format style: **Rules**.
   * What field should we base this on? `[Net Profit]`.
   * Rule 1: If value `>= Minimum` and `< 0 Number` $\to$ choose **Crimson Red** (`#D62728`).
   * Rule 2: If value `>= 0 Number` and `<= Maximum` $\to$ choose **Emerald Green** (`#2CA02C`).
   * Click **OK**.
   *(Notice that Tables immediately displays in Red with -$64K loss!)*

#### B. Volume vs. Margin Elasticity (Scatter Chart)
1. Add a **Scatter chart** visual.
2. Drag fields:
   * **Values:** `dim_products[sub_category]`
   * **X-axis:** `[Total Sales]`
   * **Y-axis:** `[Profit Margin %]`
   * **Size:** `[Total Quantity Sold]`
   * **Tooltips:** `[Discount Concession $]` and `[Total Line Items]`

#### C. High-Volume Loss Leader SKU Audit Table (Table Visual)
1. Add a **Table** visual across the bottom.
2. Drag fields into **Columns**:
   * `dim_products[product_id]`
   * `dim_products[product_name]`
   * `dim_products[sub_category]`
   * `[Total Quantity Sold]`
   * `[Total Sales]`
   * `[Net Profit]`
   * `[Profit Margin %]`
3. Click the column header for **`Net Profit`** to sort ascending. The worst loss-making products appear at the top.

---

### 📄 PAGE 3: CUSTOMER INTELLIGENCE & SEGMENT ECONOMICS

#### A. Customer Segment Breakdown (Donut Chart)
1. Add a **Donut chart** visual.
2. Drag fields:
   * **Legend:** `dim_customers[segment]`
   * **Values:** `[Total Sales]`

#### B. Profit by Segment (Clustered Column Chart)
1. Add a **Clustered column chart**.
2. Drag fields:
   * **X-axis:** `dim_customers[segment]`
   * **Y-axis:** `[Net Profit]` and `[Profit Margin %]`

#### C. Customer Summary Table
1. Add a **Table** visual.
2. Drag fields into **Columns**:
   * `dim_customers[customer_id]`
   * `dim_customers[customer_name]`
   * `dim_customers[segment]`
   * `[Distinct Orders]`
   * `[Total Sales]`
   * `[Net Profit]`
   * `[Profit Margin %]`

---

### 📄 PAGE 4: DISCOUNT IMPACT & WHAT-IF POLICY SIMULATION

#### A. Paste the What-If Slicer
Paste the `Discount Cap` slider created in Step 7 at the top of this page.

#### B. Comparison KPI Cards
Add 4 **Card** visuals side-by-side:
* **Card 1:** Current Net Profit = `[Net Profit]` (`$1.47M`)
* **Card 2:** Static Simulated Profit (20% Cap) = `[Simulated Profit (Static 20% Cap)]` (`$2.50M`)
* **Card 3:** Static Profit Opportunity = `[Static Profit Lift]` (`+$1.03M`)
* **Card 4:** Realistic Elasticity-Adjusted Lift = `[Realistic Profit Lift]` (`+$248.5K`)

#### C. Margin Collapse by Discount Tier (Column Chart)
1. To group discount tiers on the visual, use `fact_orders[discount]`.
2. Add a **Line and clustered column chart**.
   * **X-axis:** `fact_orders[discount]`
   * **Column Y-axis:** `[Total Sales]`
   * **Line Y-axis:** `[Profit Margin %]`
*(Notice how the line drops below zero once discounts exceed 0.20!)*

#### D. Dollar Discount Concessions by Sub-Category (Bar Chart)
1. Add a **Clustered bar chart**.
2. Drag fields:
   * **Y-axis:** `dim_products[sub_category]`
   * **X-axis:** `[Discount Concession $]`

---

### 📄 PAGE 5: REGIONAL LOGISTICS & FULFILLMENT ANALYTICS

#### A. Logistics KPI Cards
Add 3 **Card** visuals:
* **Card 1:** `[Total Shipping Cost]` (`$1.36M`)
* **Card 2:** `[Freight Burden %]` (`10.7%`)
* **Card 3:** `[Average Lead Time (Days)]` (`3.97 Days`)

#### B. Shipping Mode SLA & Cost Ratio (Clustered Bar Chart)
1. Add a **Clustered bar chart**.
2. Drag fields:
   * **Y-axis:** `dim_shipping_mode[ship_mode]`
   * **X-axis:** `[Average Lead Time (Days)]` and `[Freight Burden %]`

#### C. Regional Profitability & Return Intensity (Table / Matrix)
1. Add a **Matrix** visual.
2. Drag fields:
   * **Rows:** `dim_geography[market]` and `dim_geography[region]`
   * **Values:** `[Total Sales]`, `[Net Profit]`, `[Profit Margin %]`, `[Order Return Rate %]`

---

## Step 9: Save the Report & Export Screenshots

1. Click **File** > **Save As**.
2. Save the file in the project directory as:
   `ecommerce_profitability.pbix`
3. Export high-resolution screenshots for your portfolio or interview presentation:
   * Navigate to each page in Power BI Desktop.
   * Press `Win + Shift + S` on your keyboard (Windows Snipping Tool).
   * Capture each full page and save the PNG files into:
     `c:\Users\Admin\Desktop\Ecommerce-Profitability-Intelligence\power_bi\screenshots\`
   * Suggested names:
     * `01_executive_overview.png`
     * `02_profitability_bleeders.png`
     * `03_customer_intelligence.png`
     * `04_discount_impact.png`
     * `05_regional_logistics.png`

---

## Step 10: Compare Power BI Values Against Validated SQL Benchmarks

To ensure your implementation is 100% accurate, make sure **all slicers on Page 1 are cleared/reset**, then check that your Card visuals display the exact numbers below:

| KPI Card | Expected Power BI Display | Source Verification File | Status |
| :--- | :---: | :--- | :---: |
| **Total Sales** | **$12,642,501.91** | `data/processed/analytics/executive_kpis.csv` | [ ] Match |
| **Gross Sales** | **$15,006,490.23** | Derived formula $\sum \text{sales} / (1 - \text{discount})$ | [ ] Match |
| **Net Profit** | **$1,467,457.29** | `data/processed/analytics/executive_kpis.csv` | [ ] Match |
| **Profit Margin %** | **11.61%** | `data/processed/analytics/executive_kpis.csv` | [ ] Match |
| **Total Distinct Orders** | **25,728** | `data/processed/analytics/executive_kpis.csv` | [ ] Match |
| **Total Line Items** | **51,290** | `data/processed/analytics/executive_kpis.csv` | [ ] Match |
| **Total Quantity Sold** | **178,312** | `data/processed/analytics/executive_kpis.csv` | [ ] Match |
| **Average Order Value (AOV)** | **$491.39** | `data/processed/analytics/executive_kpis.csv` | [ ] Match |
| **Total Returned Orders** | **1,079** | `data/processed/analytics/executive_kpis.csv` | [ ] Match |
| **Order Return Rate %** | **4.19%** | `data/processed/analytics/executive_kpis.csv` | [ ] Match |
| **Sales Exposed to Returns** | **$525,932.23** | `data/processed/analytics/executive_kpis.csv` | [ ] Match |
| **Total Shipping Cost** | **$1,358,085.70** | `data/processed/analytics/executive_kpis.csv` | [ ] Match |
| **Freight Burden %** | **10.74%** | `data/processed/analytics/executive_kpis.csv` | [ ] Match |
| **Average Lead Time** | **3.97 Days** | `data/processed/analytics/executive_kpis.csv` | [ ] Match |
| **Static Simulated Profit (20% Cap)** | **$2,499,943.84** | Static zero-elasticity model ($+$1.03M lift) | [ ] Match |
| **Elasticity-Adjusted Profit** | **$1,715,254.06** | Conservative 24% capture model ($+$248.5K lift) | [ ] Match |

If all numbers match, your Power BI implementation is **100% verified, reconciled to the cent, and ready for interview presentation!**
