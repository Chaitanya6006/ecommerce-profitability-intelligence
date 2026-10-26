# Power BI Dashboard Specification & Visual Wireframes
## E-Commerce Profitability Intelligence Platform

This specification details the canvas layout, visual hierarchy, exact field bindings, slicers, and conditional formatting rules for all **5 interactive dashboard pages**.

---

## 🎨 Global UI/UX Design System
* **Canvas Resolution:** 16:9 Standard widescreen ($1280 \times 720\text{ px}$ or $1920 \times 1080\text{ px}$)
* **Background:** Clean neutral `#F8F9FA` with white container cards (`#FFFFFF`) with subtle border shadows (`#E2E8F0`).
* **Header Banner:** Height $60\text{ px}$, deep corporate navy `#1B365D`, containing Report Title, Page Subtitle, and Global Reset Slicer icon.
* **KPI Accent Palette:**
  * Operating Profit / Positive Margin: Emerald `#2CA02C`
  * Operating Deficit / Margin Erosion: Crimson `#D62728`
  * Warning / At-Risk Segment: Amber `#FF7F0E`
  * Neutral Volume / Benchmark: Slate Blue `#3182BD`

---

## 📄 PAGE 1: EXECUTIVE OVERVIEW

```
+-------------------------------------------------------------------------------------------------------------+
| [LOGO] E-COMMERCE PROFITABILITY INTELLIGENCE — Executive Performance Scorecard                              |
| Top-line GMV, operating margins, fulfillment efficiency, and return rates.      [Year ▼] [Market ▼] [Reset] |
+-------------------------------------------------------------------------------------------------------------+
| KPI CARDS (Row 1):                                                                                          |
| +-----------------+ +-----------------+ +-----------------+ +-----------------+ +-----------------+         |
| | Gross Revenue   | | Net Profit      | | Net Margin %    | | Distinct Orders | | Return Rate %   |         |
| | $12.64M         | | $1.47M          | | 11.6%           | | 25,728          | | 4.19%           |         |
| | YoY: +18.2% ▲   | | YoY: +12.4% ▲   | | Spread: -60 bps | | AOV: $491.39    | | Sales: $525.9K  |         |
| +-----------------+ +-----------------+ +-----------------+ +-----------------+ +-----------------+         |
+-------------------------------------------------------------------------------------------------------------+
| VISUAL 1 (Left 60%):                                   | VISUAL 2 (Right 40%):                              |
| Monthly Net Sales ($) vs. Net Profit ($) Trend         | Category P&L and Margin Contribution               |
| Dual-Axis Area & Line Chart (48 Months: 2012–2015)     | Clustered Bar Chart                                |
|   - Primary Y-Axis (Area): Total Sales ($K)            |   - Y-Axis: Category (Technology, Office, Furniture|
|   - Secondary Y-Axis (Line): Net Profit ($K)           |   - X-Axis: Total Sales ($), Net Profit ($)        |
|   - Tooltip: AOV, Orders, Return Rate                  |   - Data Label: Margin % (Tech: 13.4%, Furn: 6.9%) |
+-------------------------------------------------------------------------------------------------------------+
| VISUAL 3 (Left 50%):                                   | VISUAL 4 (Right 50%):                              |
| Global Market Profitability Breakdown                  | Top 5 Regional Operating Hubs                      |
| Clustered Column Chart by Market                       | Horizontal Bar Chart with Conditional Color        |
|   - Categories: APAC, EU, US, LATAM, EMEA, Africa      |   - Central US, Western Europe, North Asia, etc.   |
|   - Measures: Net Sales vs. Net Profit                 |   - Metric: Net Profit Margin %                    |
+-------------------------------------------------------------------------------------------------------------+
```

### Visual Specifications
1. **Global Slicers (Top Right):**
   * Date Slicer: Between (`dim_date[full_date]`) or Dropdown (`dim_date[year]`)
   * Market Slicer: Dropdown (`dim_geography[market]`)
   * Customer Segment: Button Bar (`dim_customers[segment]`)
2. **KPI Scorecard Cards:**
   * Card 1: `[Total Sales]`, subtext YoY comparison via `[Sales YoY Growth %]`
   * Card 2: `[Net Profit]`, conditional text color (Green if $>0$, Red if $<0$)
   * Card 3: `[Profit Margin %]`, formatted as `0.0%`
   * Card 4: `[Distinct Orders]`, subtext `[Average Order Value]`
   * Card 5: `[Order Return Rate %]`, formatted as `0.00%`, subtext `[Sales Exposed to Returns $]`
3. **Monthly Trend Visual:**
   * X-Axis: `dim_date[year_month]` (continuous hierarchy)
   * Y-Axis 1: `[Total Sales]` (Deep Navy Area fill `#1B365D`, 15% opacity)
   * Y-Axis 2: `[Net Profit]` (Emerald Line `#2CA02C`, 3px stroke, dashed)

---

## 📄 PAGE 2: PROFITABILITY INTELLIGENCE & BLEEDER AUDIT

```
+-------------------------------------------------------------------------------------------------------------+
| PAGE 2: MERCHANDISING UNIT ECONOMICS & PROFIT BLEEDERS                                                      |
| Isolate margin-bleeding categories, high-volume loss leaders, and Pareto distributions.                     |
+-------------------------------------------------------------------------------------------------------------+
| VISUAL 1 (Top Left 50%):                               | VISUAL 2 (Top Right 50%):                          |
| Sub-Category Profit Waterfall & Ranking                | Sub-Category Margin Health Matrix                  |
| Horizontal Bar Chart (Ordered by Profit)               | Scatter Plot: Volume vs. Margin Elasticity         |
|   - Green: Copiers (+$258K), Phones (+$216K)           |   - X-Axis: Total Sales ($K)                       |
|   - Red: Tables (-$64.1K), Bookcases (-$3.5K)          |   - Y-Axis: Net Profit Margin (%)                  |
|   - Data Labels: Net Profit ($)                        |   - Bubble Size: Total Quantity Sold               |
+-------------------------------------------------------------------------------------------------------------+
| VISUAL 3 (Bottom Full Width):                                                                               |
| High-Volume Margin Bleeders (Audit Table with Conditional Color Formatting)                                 |
| Product ID | Product Name | Sub-Category | Units Sold | Total Sales | Total Profit | Margin % | Return %   |
| ----------------------------------------------------------------------------------------------------------- |
| FFE-TA-100 | Chromcraft Table | Tables    | 86         | $24,250     | -$8,420      | -34.7%   | 8.1%       |
| OFF-BI-202 | GBC DocuBind      | Binders   | 114        | $18,400     | -$4,210      | -22.9%   | 5.3%       |
+-------------------------------------------------------------------------------------------------------------+
```

### Visual Specifications
1. **Visual 1 (Sub-Category Profitability):**
   * Fields: `dim_products[sub_category]` on Y-axis, `[Net Profit]` on X-axis.
   * Conditional Color Rule: Format by Rules on `[Net Profit]` $\to$ If $< 0$ Crimson `#D62728`, If $\ge 0$ Emerald `#2CA02C`.
2. **Visual 2 (Volume vs. Margin Scatter):**
   * Values: `dim_products[sub_category]`
   * X-Axis: `[Total Sales]`, Y-Axis: `[Profit Margin %]`, Bubble Size: `[Total Quantity Sold]`
   * Quadrant Reference Lines: Vertical line at median sales, Horizontal reference line at $0\%$ margin.
   * Callout: Top-right quadrant = "Core Growth Engines"; Bottom-right quadrant = "High-Volume Drainers".
3. **Visual 3 (Bleeders Detail Table):**
   * Fields: `dim_products[product_id]`, `dim_products[product_name]`, `dim_products[sub_category]`, `[Total Quantity Sold]`, `[Total Sales]`, `[Net Profit]`, `[Profit Margin %]`, `[Order Return Rate %]`.
   * Filter: Top 25 products with `[Total Sales] >= 2000` ordered by `[Net Profit] ASC`.
   * Conditional Formatting: Background color on `[Net Profit]` and `[Profit Margin %]` with soft red gradient.

---

## 📄 PAGE 3: CUSTOMER INTELLIGENCE & RFM PERSONAS

```
+-------------------------------------------------------------------------------------------------------------+
| PAGE 3: CUSTOMER PURCHASING DYNAMICS & RFM SEGMENTATION                                                     |
| Strategic personas, customer lifetime value, and cohort retention behavior.                                 |
+-------------------------------------------------------------------------------------------------------------+
| VISUAL 1 (Top Left 50%):                               | VISUAL 2 (Top Right 50%):                          |
| Customer Persona Share & Headcount                     | Segment Net Operating Income Contribution          |
| Treemap Visual: RFM Segments                          | Horizontal Bar Chart: Total Profit by Segment      |
|   - Champions (12.6%, 2,188 cust)                      |   - Champions: +$879K                              |
|   - Loyal Customers (18.3%, 3,191 cust)                |   - At Risk: +$659K                                |
|   - Margin Drainers (25.4%, 4,427 cust)                |   - Loyal Customers: +$585K                        |
|   - At Risk (15.5%, 2,690 cust)                        |   - Margin Drainers: -$773K (CRITICAL CALLOUT)     |
+-------------------------------------------------------------------------------------------------------------+
| VISUAL 3 (Bottom Left 50%):                            | VISUAL 4 (Bottom Right 50%):                       |
| Customer Purchasing Patterns by Market Segment         | Annual Customer Cohort Retention Heatmap           |
| Clustered Bar: Consumer vs. Corporate vs. Home Office  | Matrix Visual: Cohort Year vs. Year Index          |
|   - Measures: AOV ($), Basket Units, Order Frequency   |   - Rows: 2012, 2013, 2014, 2015                   |
|   - Slices customer unit economics                     |   - Values: Retention Rate % (Conditional Blue)    |
+-------------------------------------------------------------------------------------------------------------+
```

### Visual Specifications
1. **Visual 1 (RFM Personas Treemap):**
   * Category: `customer_rfm_segments[rfm_segment]`
   * Values: `[Customer Count]`
   * Tooltip: `[Total Segment Sales]`, `[Total Segment Profit]`, `[Segment Margin %]`
2. **Visual 2 (Segment Profit Contribution):**
   * Y-Axis: `customer_rfm_segments[rfm_segment]`
   * X-Axis: `[Total Segment Profit]`
   * Highlight Card: **"Margin Drainers Alert: 4,427 customers accumulate -\$773K in losses due to discount exploitation on high-freight items."**
3. **Visual 4 (Cohort Matrix):**
   * Rows: `cohort_retention_annual[cohort_year]`
   * Columns: `cohort_retention_annual[year_index]`
   * Values: `[Retention Rate %]` formatted as `0.0%`
   * Conditional Formatting: Background color gradient from Light Gray to Deep Blue `#1B365D`.

---

## 📄 PAGE 4: DISCOUNT IMPACT & WHAT-IF SIMULATOR

```
+-------------------------------------------------------------------------------------------------------------+
| PAGE 4: DISCOUNT ELASTICITY & MARGIN CLIFF INTELLIGENCE                                                     |
| Empirical margin degradation across discount tiers and What-If governance capping.                          |
+-------------------------------------------------------------------------------------------------------------+
| VISUAL 1 (Top Left 50%):                               | VISUAL 2 (Top Right 50%):                          |
| The Promotional Margin Cliff                           | Loss Propensity by Promotional Tier                |
| Clustered Bar: Discount Tier vs. Margin %              | Line Chart: % Unprofitable Transactions            |
|   - 0%: +25.3% margin                                  |   - 0% Tier: 0.0% Unprofitable                     |
|   - 0-10%: +17.2% margin                               |   - 0-10%: 19.3% Unprofitable                      |
|   - 10-20%: +9.9% margin                               |   - 10-20%: 23.3% Unprofitable                     |
|   - 20-40%: -17.3% margin (CLIFF)                      |   - 20-40%: 76.2% Unprofitable                     |
|   - >40%: -74.1% margin (CATASTROPHIC)                 |   - >40%: 98.4% Unprofitable                       |
+-------------------------------------------------------------------------------------------------------------+
| WHAT-IF PROMOTIONAL GOVERNANCE SIMULATOR (Bottom Container):                                                |
| +---------------------------------------------------------------------------------------------------------+ |
| | POLICY PARAMETER SLICER: Max Allowed Discount Cap = [ 20% ]                                             | |
| | Current Net Profit: $1,467,457  |  Simulated Profit: $1,715,957  |  Projected Profit Lift: +$248,500    | |
| | STATISTICAL CALLOUT: Kruskal-Wallis H = 25,991, p < 0.001 (Eta-squared = 0.683). Dispel Myth: Order     | |
| | Return Rates do NOT correlate with discounts (Chi-Square p = 0.116, Cramér's V = 0.013).                 | |
| +---------------------------------------------------------------------------------------------------------+ |
+-------------------------------------------------------------------------------------------------------------+
```

### Visual Specifications
1. **Visual 1 & 2 (Discount Tier Performance):**
   * X-Axis: `discount_tier_analysis[discount_tier]`
   * Bars: `[Profit Margin %]` (Green for tiers 1-3, Red for tiers 4-5)
   * Line overlay: `[Unprofitable Lines %]`
2. **What-If Simulation Cards:**
   * Dynamic DAX Card: `[Simulated Profit (20% Cap)]`
   * Delta Card: `[Simulated Profit (20% Cap)] - [Net Profit]` displaying **+\$248.5K Lift** in Emerald text.
3. **Statistical Governance Callout Box:**
   * A callout card documenting findings from `reports/statistical_analysis_report.md` explaining that return rates are statistically independent of discount depth ($\chi^2 = 4.31, p = 0.116$).

---

## 📄 PAGE 5: REGIONAL & SUPPLY CHAIN LOGISTICS

```
+-------------------------------------------------------------------------------------------------------------+
| PAGE 5: LOGISTICS PERFORMANCE, FREIGHT DRAG & FULFILLMENT SLAS                                              |
| Supply chain cycle time, carrier mode efficiency, and geographic friction.                                  |
+-------------------------------------------------------------------------------------------------------------+
| VISUAL 1 (Top Left 50%):                               | VISUAL 2 (Top Right 50%):                          |
| Carrier Shipping Mode SLA & Freight Burden             | Fulfillment Lead Time SLA Distribution             |
| Clustered Column: Lead Time (Days) vs. Freight %       | Donut Chart: Orders by Lead Time Bracket           |
|   - Same Day: 0.04 Days | 16.2% Freight Burden         |   - 0 Days (Same Day): 5.1%                        |
|   - First Class: 2.18 Days | 14.8% Freight Burden      |   - 1-2 Days (Expedited): 18.4%                    |
|   - Second Class: 3.24 Days | 11.2% Freight Burden     |   - 3-5 Days (Standard): 61.3%                     |
|   - Standard Class: 5.01 Days | 8.8% Freight Burden    |   - >5 Days (Delayed): 15.2%                       |
+-------------------------------------------------------------------------------------------------------------+
| VISUAL 3 (Bottom Full Width):                                                                               |
| Regional Supply Chain Scorecard Table                                                                       |
| Market | Region | Country Count | Orders | GMV ($) | Freight Cost ($) | Freight Burden % | Net Profit | Marg%|
| ----------------------------------------------------------------------------------------------------------- |
| APAC   | Oceania| 3             | 3,412  | $1.10M  | $120.4K          | 10.9%            | $120.1K    | 10.9%|
| LATAM  | South  | 11            | 2,145  | $680.2K | $78.1K           | 11.5%            | $62.4K     | 9.2% |
+-------------------------------------------------------------------------------------------------------------+
```

### Visual Specifications
1. **Visual 1 (Carrier Efficiency):**
   * X-Axis: `dim_shipping_mode[ship_mode]`
   * Y-Axis 1 (Bar): `[Average Lead Time (Days)]`
   * Y-Axis 2 (Line): `[Freight Burden %]`
2. **Visual 2 (Lead Time SLA Distribution):**
   * Legend: `sla_bracket` (`0 Days`, `1-2 Days`, `3-5 Days`, `>5 Days`)
   * Values: `[Distinct Orders]`
3. **Visual 3 (Regional Scorecard):**
   * Hierarchy: `dim_geography[market]` $\to$ `dim_geography[region]`
   * Measures: `[Distinct Orders]`, `[Total Sales]`, `[Total Shipping Cost]`, `[Freight Burden %]`, `[Net Profit]`, `[Profit Margin %]`, `[Order Return Rate %]`.
   * Data Bars: Enabled on `[Total Sales]` and `[Net Profit]`.
