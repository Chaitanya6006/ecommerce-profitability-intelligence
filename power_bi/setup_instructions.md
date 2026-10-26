# Power BI Desktop Implementation & Setup Guide
## E-Commerce Profitability Intelligence Platform

This comprehensive implementation manual provides step-by-step instructions to assemble, configure, and validate the **E-Commerce Profitability Intelligence** Power BI report using the modular production assets provided in this repository.

---

## 🛠️ Prerequisites & Asset Inventory

### Software Requirements
* **Power BI Desktop:** August 2023 release or newer (64-bit recommended).
* **Local Data Files:** Clean, verified star-schema CSV files located in `data/processed/`.

### Repository Asset Reference
* **Power Query M Code:** [`power_bi/power_query_scripts.m`](power_query_scripts.m)
* **Data Model Architecture:** [`power_bi/data_model_documentation.md`](data_model_documentation.md)
* **DAX Measures Library:** [`power_bi/dax_measures.md`](dax_measures.md)
* **Visual Specifications & Wireframes:** [`power_bi/dashboard_specification.md`](dashboard_specification.md)
* **Corporate Visual Theme:** [`power_bi/theme/corporate_theme.json`](theme/corporate_theme.json)
* **Validation & Audit Checklist:** [`power_bi/validation_checklist.md`](validation_checklist.md)

---

## 🚀 Step 1: Initialize Power BI & Configure Global Parameter

1. Launch **Power BI Desktop**.
2. Create a blank report (`File` > `New`).
3. Open Power Query Editor by clicking **Transform Data** on the Home ribbon.
4. Create the folder path parameter:
   * On the **Home** ribbon of Power Query, click **Manage Parameters** > **New Parameter**.
   * Configure the parameter:
     * **Name:** `DataFolderPath`
     * **Description:** Absolute directory path containing the processed CSV tables.
     * **Type:** `Text`
     * **Suggested Values:** `Any value`
     * **Current Value:** `C:\Users\Admin\Desktop\Ecommerce-Profitability-Intelligence\data\processed` *(or your local clone path)*
   * Click **OK**.

---

## 📥 Step 2: Ingest Star Schema Tables via Power Query

In Power Query Editor, create each table using the provided M scripts:

1. For each table below:
   * Click **New Source** > **Blank Query**.
   * In the **Home** ribbon, click **Advanced Editor**.
   * Replace the existing code with the corresponding section from [`power_bi/power_query_scripts.m`](power_query_scripts.m).
   * Rename the query in the **Query Settings** pane to match the table name:
     1. `dim_customers` (17,415 rows)
     2. `dim_products` (3,788 rows)
     3. `dim_geography` (3,856 rows)
     4. `dim_date` (1,468 rows)
     5. `dim_shipping_mode` (4 rows)
     6. `fact_orders` (51,290 rows)
     7. `fact_returns` (1,079 rows)
2. Verify Data Types:
   * Ensure `fact_orders[sales]`, `cogs`, `profit`, `shipping_cost`, `gross_sales`, and `discount_amount` are typed as **Fixed Decimal Number (Currency)**.
   * Ensure `fact_orders[discount]` is typed as **Percentage / Decimal Number**.
   * Ensure `fact_orders[quantity]`, `lead_time_days`, and `is_returned` are typed as **Whole Number**.
   * Ensure `dim_date[full_date]` is typed as **Date**.
3. Click **Close & Apply** on the Home ribbon to load tables into the VertiPaq engine.

---

## 🔗 Step 3: Establish Star Schema Relationships

Navigate to the **Model View** (left navigation bar):

1. Position `fact_orders` centrally, surrounded by dimension tables.
2. Establish the **6 standard relationships** as detailed in [`power_bi/data_model_documentation.md`](data_model_documentation.md):

| From Table (Foreign Key) | To Table (Primary Key) | Cardinality | Cross-Filter | Active |
| :--- | :--- | :---: | :---: | :---: |
| `fact_orders[customer_key]` | `dim_customers[customer_key]` | Many to One ($*:1$) | Single | **Yes** |
| `fact_orders[product_key]` | `dim_products[product_key]` | Many to One ($*:1$) | Single | **Yes** |
| `fact_orders[geography_key]` | `dim_geography[geography_key]` | Many to One ($*:1$) | Single | **Yes** |
| `fact_orders[order_date_key]` | `dim_date[date_key]` | Many to One ($*:1$) | Single | **Yes** |
| `fact_orders[ship_date_key]` | `dim_date[date_key]` | Many to One ($*:1$) | Single | **No** (Inactive) |
| `fact_orders[shipping_mode_key]` | `dim_shipping_mode[shipping_mode_key]` | Many to One ($*:1$) | Single | **Yes** |

> [!IMPORTANT]
> Keep `fact_returns` as an isolated audit table or link via explicit DAX lookup. **Do not** create a bidirectional relationship between `fact_orders[order_id]` and `fact_returns[order_id]`. Order returns are already modeled via `fact_orders[is_returned]`.

3. Configure Table Settings:
   * Select `dim_date` in the Fields list > **Table Tools** ribbon > **Mark as Date Table** > Select `full_date`.
   * Select column `dim_date[month_name]` > **Column Tools** ribbon > **Sort by Column** > Select `dim_date[month]`.

---

## 🎨 Step 4: Import Enterprise Corporate Theme

1. In the **Report View**, navigate to the **View** ribbon.
2. Click the dropdown arrow in the **Themes** gallery and select **Browse for themes**.
3. Select the file [`power_bi/theme/corporate_theme.json`](theme/corporate_theme.json).
4. Confirm the palette applies clean corporate navy (`#1B365D`), emerald (`#2CA02C`), crimson (`#D62728`), and slate accents across visuals.

---

## 📐 Step 5: Implement DAX Measures Library

1. Create a dedicated measure storage table:
   * On the **Home** ribbon, click **Enter Data**.
   * Name the table `_Measures` and click **Load**.
2. Add each DAX measure defined in [`power_bi/dax_measures.md`](dax_measures.md) by selecting `_Measures` > **New Measure**:
   * **Core Financials:** `[Total Sales]`, `[Gross Sales]`, `[Total COGS]`, `[Net Profit]`, `[Profit Margin %]`, `[Discount Concession $]`, `[Effective Discount Rate %]`.
   * **Volume & Basket:** `[Total Line Items]`, `[Distinct Orders]`, `[Total Quantity Sold]`, `[Average Order Value]`, `[Items Per Order]`.
   * **Time Intelligence:** `[Sales YoY Growth %]`, `[Profit YoY Growth %]`, `[Sales MoM Growth %]`.
   * **Returns & Quality:** `[Returned Orders]`, `[Order Return Rate %]`, `[Sales Exposed to Returns $]`, `[Return Sales Ratio %]`.
   * **Logistics & SLAs:** `[Total Shipping Cost]`, `[Shipping Cost Ratio %]`, `[Average Lead Time Days]`, `[Delayed Orders Count]`, `[On-Time Delivery Rate %]`.
   * **Simulation & What-If:** `[Simulated Profit]`, `[Profit Opportunity $]`, `[Recovered Margin Spread bps]`.
3. Set **Format Strings** (Currency `\$#,##0.00`, Percentage `0.0%`, Whole Number `#,##0`) and assign each measure to its respective Display Folder.
4. Delete the empty `Column1` from `_Measures` to convert it into a calculator icon.

---

## 🎛️ Step 6: Create What-If Discount Cap Parameter

To enable dynamic policy simulation on Page 4:

1. Navigate to the **Modeling** ribbon.
2. Click **New Parameter** > **Numeric range**.
3. Configure:
   * **Name:** `Discount Cap`
   * **Data type:** `Decimal Number`
   * **Minimum:** `0.00`
   * **Maximum:** `0.50`
   * **Increment:** `0.05`
   * **Default:** `0.20`
   * Check **Add slicer to this page**.
4. Power BI will create the calculated table:
   ```dax
   Discount Cap = GENERATESERIES(0, 0.5, 0.05)
   Discount Cap Value = SELECTEDVALUE('Discount Cap'[Discount Cap], 0.20)
   ```
5. Format `Discount Cap Value` as Percentage (`0%`).

---

## 📊 Step 7: Assemble the 5 Interactive Dashboard Pages

Build out each canvas according to the layouts, visual types, and field bindings in [`power_bi/dashboard_specification.md`](dashboard_specification.md):

### Page 1: Executive Overview (`1280 x 720` px)
1. **Header Banner:** Navy background `#1B365D`, title "E-Commerce Profitability Intelligence — Executive Scorecard".
2. **Global Slicers:** Year (`dim_date[year]`), Market (`dim_geography[market]`), Customer Segment (`dim_customers[segment]`).
3. **Top KPI Row (5 Cards):**
   * Card 1: `[Total Sales]` with subtext `[Sales YoY Growth %]`
   * Card 2: `[Net Profit]` (conditional font color: Green if $>0$, Red if $<0$)
   * Card 3: `[Profit Margin %]` (`0.0%`)
   * Card 4: `[Distinct Orders]` with subtext `[Average Order Value]`
   * Card 5: `[Order Return Rate %]` with subtext `[Sales Exposed to Returns $]`
4. **Visual 1 (Area & Line):** Monthly Net Sales vs Net Profit (X: `dim_date[year_month]`, Y1: `[Total Sales]`, Y2: `[Net Profit]`).
5. **Visual 2 (Clustered Bar):** Category P&L Breakdown (Y: `dim_products[category]`, X: `[Total Sales]`, `[Net Profit]`).
6. **Visual 3 (Clustered Column):** Sales & Profit by Global Market (`dim_geography[market]`).
7. **Visual 4 (Horizontal Bar):** Top Regional Operating Hubs by Net Profit Margin %.

### Page 2: Profitability Intelligence & Bleeder Audit
1. **Visual 1 (Horizontal Bar):** Sub-Category Profitability Waterfall (Y: `dim_products[sub_category]`, X: `[Net Profit]`). Apply conditional color: Red for Tables and Bookcases, Green for Copiers/Phones.
2. **Visual 2 (Scatter Plot):** Sub-Category Volume vs Margin (X: `[Total Sales]`, Y: `[Profit Margin %]`, Size: `[Total Quantity Sold]`, Tooltip: `[Discount Concession $]`).
3. **Visual 3 (Audit Table):** High-Volume Margin Bleeders (Product ID, Product Name, Sub-Category, Quantity, Sales, Profit, Margin %, Return Rate). Sort by Net Profit ascending.

### Page 3: Customer Intelligence & Segment Economics
1. **Top KPI Cards:** Total Unique Customers, Customer Lifetime Value Proxy, Top Segment Margin %, Repeat Purchase Ratio.
2. **Visual 1 (Donut Chart):** Sales & Profit Contribution by Customer Segment (`Consumer`, `Corporate`, `Home Office`).
3. **Visual 2 (Heatmap Matrix):** RFM Quintile Margin Distribution (Rows: R-Score 1-5, Columns: M-Score 1-5, Values: `[Profit Margin %]`).
4. **Visual 3 (Cohort Retention Matrix):** Multi-Year Customer Cohort Retention (Rows: Acquisition Cohort Year, Columns: Activity Year 0-3, Values: Retention % and Cumulative Margin).

### Page 4: Discount Impact & Price Elasticity
1. **What-If Control Slicer:** Connect the `Discount Cap` slider (0% to 50%).
2. **Simulation Impact Cards:** Baseline Profit ($1.47M), Simulated Profit with Cap, Profit Opportunity ($), Margin Spread Improvement (bps).
3. **Visual 1 (Clustered Column & Line):** Sales Volume vs Net Margin % by Discount Tier (0%, 0-10%, 10-20%, 20-30%, >30%).
4. **Visual 2 (Scatter Chart):** Order-Level Discount Depth vs Margin % with regression trendline.
5. **Visual 3 (Stacked Bar):** Dollar Discount Concession by Sub-Category.

### Page 5: Regional Logistics & Fulfillment Analytics
1. **Logistics KPIs:** Average Lead Time (3.97 Days), Total Shipping Freight ($1.35M), Shipping Cost Ratio (10.7%), Delayed Delivery Rate.
2. **Visual 1 (Clustered Bar):** Freight Ratio & Delivery Speed by Carrier Shipping Mode (`Same Day`, `First Class`, `Second Class`, `Standard Class`).
3. **Visual 2 (Choropleth Map / Filled Map):** Global Regional Profitability & Return Intensity.
4. **Visual 3 (Table / Decomposition Tree):** Lead Time vs Order Return Rate Correlation by Geographic Market.

---

## 🔍 Step 8: Quality Gate & Validation Checklist

Before presenting or publishing the report, execute every verification item in [`power_bi/validation_checklist.md`](validation_checklist.md):
1. Confirm zero slicer selections produce `Total Sales = $12,642,501.91` and `Net Profit = $1,467,457.29` ($0.00 variance against SQLite warehouse).
2. Confirm `Distinct Orders = 25,728` and `Order Return Rate = 4.19%`.
3. Open Power BI **Performance Analyzer** (`View` > `Performance Analyzer` > `Start Recording`) and refresh visuals; confirm DAX query execution times are `< 500ms`.
4. Verify cross-filtering behaves unidirectionally without circular dependency warnings.

---

## 💾 Step 9: Save & Publish Deliverables

1. Save the local report as `ecommerce_profitability.pbix` in the project root or `power_bi/` directory.
2. Export page screenshots to `power_bi/screenshots/` for GitHub documentation and portfolio showcases.
3. If publishing to Power BI Service:
   * Click **Publish** on the Home ribbon.
   * Select your target Workspace (e.g., `Executive Analytics Portfolio`).
   * Configure scheduled refresh if connected to an enterprise gateway or cloud PostgreSQL database.
