# Comprehensive DAX Measures Library
## E-Commerce Profitability Intelligence Platform

This repository provides production-grade, mathematically verified DAX measures organized into clean functional groups. All measures are validated against the PostgreSQL/SQLite analytical warehouse benchmarks ($12.64M sales, $1.47M profit, 11.61% net margin, 25,728 distinct orders, 4.19% order return rate).

---

## 1. Core Financial Measures

### `[Total Sales]`
* **DAX Formulation:**
  ```dax
  Total Sales = 
  SUM(fact_orders[sales])
  ```
* **Business Meaning:** Net top-line transactional revenue collected after promotional discounts.
* **Grain:** Order line item aggregation.
* **Format String:** `\$#,##0.00`
* **Benchmark Value:** **\$12,642,501.91**

### `[Gross Sales]`
* **DAX Formulation:**
  ```dax
  Gross Sales = 
  SUM(fact_orders[gross_sales])
  ```
* **Business Meaning:** Undiscounted baseline list-price revenue ($\text{Sales} / (1 - \text{Discount})$).
* **Format String:** `\$#,##0.00`
* **Benchmark Value:** **\$14,561,422.37**

### `[Total COGS]`
* **DAX Formulation:**
  ```dax
  Total COGS = 
  SUM(fact_orders[cogs])
  ```
* **Business Meaning:** Cost of Goods Sold; isolates product acquisition/manufacturing cost from shipping.
* **Format String:** `\$#,##0.00`
* **Benchmark Value:** **\$9,817,040.85**

### `[Net Profit]`
* **DAX Formulation:**
  ```dax
  Net Profit = 
  SUM(fact_orders[profit])
  ```
* **Business Meaning:** Bottom-line earnings realized across order lines ($\text{Sales} - \text{COGS} - \text{Shipping Cost}$).
* **Format String:** `\$#,##0.00`
* **Benchmark Value:** **\$1,467,457.29**

### `[Profit Margin %]`
* **DAX Formulation:**
  ```dax
  Profit Margin % = 
  DIVIDE([Net Profit], [Total Sales], 0)
  ```
* **Business Meaning:** Operational profitability efficiency.
* **Numerator:** `[Net Profit]`
* **Denominator:** `[Total Sales]`
* **Format String:** `0.0%`
* **Benchmark Value:** **11.6%**

### `[Discount Concession $]`
* **DAX Formulation:**
  ```dax
  Discount Concession $ = 
  SUM(fact_orders[discount_amount])
  ```
* **Business Meaning:** Total dollar revenue forfeited to promotional price-cutting.
* **Format String:** `\$#,##0.00`
* **Benchmark Value:** **\$1,918,920.46**

### `[Effective Discount Rate %]`
* **DAX Formulation:**
  ```dax
  Effective Discount Rate % = 
  DIVIDE([Discount Concession $], [Gross Sales], 0)
  ```
* **Business Meaning:** Weighted average discount rate applied across catalog transactions.
* **Format String:** `0.0%`
* **Benchmark Value:** **13.2%**

---

## 2. Order Volume & Basket Size Metrics

### `[Total Line Items]`
* **DAX Formulation:**
  ```dax
  Total Line Items = 
  COUNTROWS(fact_orders)
  ```
* **Business Meaning:** Total discrete product lines fulfilled.
* **Format String:** `#,##0`
* **Benchmark Value:** **51,290**

### `[Distinct Orders]`
* **DAX Formulation:**
  ```dax
  Distinct Orders = 
  DISTINCTCOUNT(fact_orders[order_id])
  ```
* **Business Meaning:** Total completed purchasing transactions.
* **Format String:** `#,##0`
* **Benchmark Value:** **25,728**

### `[Total Quantity Sold]`
* **DAX Formulation:**
  ```dax
  Total Quantity Sold = 
  SUM(fact_orders[quantity])
  ```
* **Business Meaning:** Total physical product units delivered.
* **Format String:** `#,##0`
* **Benchmark Value:** **178,312 Units**

### `[Average Order Value (AOV)]`
* **DAX Formulation:**
  ```dax
  Average Order Value = 
  DIVIDE([Total Sales], [Distinct Orders], 0)
  ```
* **Numerator:** `[Total Sales]`
* **Denominator:** `[Distinct Orders]`
* **Format String:** `\$#,##0.00`
* **Benchmark Value:** **\$491.39**

### `[Average Basket Size (Units)]`
* **DAX Formulation:**
  ```dax
  Average Basket Size = 
  DIVIDE([Total Quantity Sold], [Distinct Orders], 0)
  ```
* **Format String:** `0.0`
* **Benchmark Value:** **6.9 Units / Order**

---

## 3. Returns Intelligence

### `[Returned Orders]`
* **DAX Formulation:**
  ```dax
  Returned Orders = 
  CALCULATE(
      DISTINCTCOUNT(fact_orders[order_id]),
      fact_orders[is_returned] = 1
  )
  ```
* **Business Meaning:** Distinct customer orders subject to return requests.
* **Format String:** `#,##0`
* **Benchmark Value:** **1,079 Orders**

### `[Order Return Rate %]`
* **DAX Formulation:**
  ```dax
  Order Return Rate % = 
  DIVIDE([Returned Orders], [Distinct Orders], 0)
  ```
* **Numerator:** `[Returned Orders]` (1,079)
* **Denominator:** `[Distinct Orders]` (25,728)
* **Format String:** `0.00%`
* **Benchmark Value:** **4.19%**

### `[Returned Line Items]`
* **DAX Formulation:**
  ```dax
  Returned Line Items = 
  CALCULATE(
      COUNTROWS(fact_orders),
      fact_orders[is_returned] = 1
  )
  ```
* **Format String:** `#,##0`
* **Benchmark Value:** **2,220 Line Items**

### `[Line Item Return Rate %]`
* **DAX Formulation:**
  ```dax
  Line Item Return Rate % = 
  DIVIDE([Returned Line Items], [Total Line Items], 0)
  ```
* **Format String:** `0.00%`
* **Benchmark Value:** **4.33%**

### `[Sales Exposed to Returns $]`
* **DAX Formulation:**
  ```dax
  Sales Exposed to Returns $ = 
  CALCULATE(
      [Total Sales],
      fact_orders[is_returned] = 1
  )
  ```
* **Business Meaning:** Top-line merchandise volume exposed to cancellation and return refunds.
* **Format String:** `\$#,##0.00`
* **Benchmark Value:** **\$525,932.23 (4.16% of total revenue)**

---

## 4. Time Intelligence & Growth Measures

### `[Sales SPLY (Same Period Last Year)]`
* **DAX Formulation:**
  ```dax
  Sales SPLY = 
  CALCULATE(
      [Total Sales],
      SAMEPERIODLASTYEAR(dim_date[full_date])
  )
  ```
* **Format String:** `\$#,##0.00`

### `[Sales YoY Growth %]`
* **DAX Formulation:**
  ```dax
  Sales YoY Growth % = 
  DIVIDE([Total Sales] - [Sales SPLY], [Sales SPLY], BLANK())
  ```
* **Format String:** `+0.0%;-0.0%;0.0%`

### `[Profit SPLY]`
* **DAX Formulation:**
  ```dax
  Profit SPLY = 
  CALCULATE(
      [Net Profit],
      SAMEPERIODLASTYEAR(dim_date[full_date])
  )
  ```
* **Format String:** `\$#,##0.00`

### `[Profit YoY Growth %]`
* **DAX Formulation:**
  ```dax
  Profit YoY Growth % = 
  DIVIDE([Net Profit] - [Profit SPLY], ABS([Profit SPLY]), BLANK())
  ```
* **Format String:** `+0.0%;-0.0%;0.0%`

### `[Cumulative Sales YTD]`
* **DAX Formulation:**
  ```dax
  Cumulative Sales YTD = 
  TOTALYTD([Total Sales], dim_date[full_date])
  ```
* **Format String:** `\$#,##0.00`

---

## 5. Logistics & Fulfillment SLA Metrics

### `[Total Shipping Cost]`
* **DAX Formulation:**
  ```dax
  Total Shipping Cost = 
  SUM(fact_orders[shipping_cost])
  ```
* **Format String:** `\$#,##0.00`
* **Benchmark Value:** **\$1,358,003.77**

### `[Freight Burden %]`
* **DAX Formulation:**
  ```dax
  Freight Burden % = 
  DIVIDE([Total Shipping Cost], [Total Sales], 0)
  ```
* **Business Meaning:** Shipping expenses incurred as a proportion of net revenue.
* **Numerator:** `[Total Shipping Cost]`
* **Denominator:** `[Total Sales]`
* **Format String:** `0.0%`
* **Benchmark Value:** **10.7%**

### `[Average Lead Time (Days)]`
* **DAX Formulation:**
  ```dax
  Average Lead Time (Days) = 
  AVERAGE(fact_orders[lead_time_days])
  ```
* **Format String:** `0.0 "Days"`
* **Benchmark Value:** **3.97 Days**

### `[Fulfillment on Ship Date (Inactive Relationship)]`
* **DAX Formulation:**
  ```dax
  Sales by Dispatch Date = 
  CALCULATE(
      [Total Sales],
      USERELATIONSHIP(fact_orders[ship_date_key], dim_date[date_key])
  )
  ```
* **Business Meaning:** Invokes secondary inactive relationship R5 to evaluate revenue dispatched rather than ordered.

---

## 6. Promotional Health & What-If Parameter Modeling

### `[Discounted Sales]`
* **DAX Formulation:**
  ```dax
  Discounted Sales = 
  CALCULATE(
      [Total Sales],
      fact_orders[discount] > 0
  )
  ```
* **Format String:** `\$#,##0.00`
* **Benchmark Value:** **\$5,650,091.24 (44.7% of total revenue)**

### `[Unprofitable Line Items Count]`
* **DAX Formulation:**
  ```dax
  Unprofitable Line Items Count = 
  CALCULATE(
      COUNTROWS(fact_orders),
      fact_orders[profit] < 0
  )
  ```
* **Format String:** `#,##0`
* **Benchmark Value:** **12,544 Line Items (24.5% of catalog sales)**

### `[Unprofitable Lines %]`
* **DAX Formulation:**
  ```dax
  Unprofitable Lines % = 
  DIVIDE([Unprofitable Line Items Count], [Total Line Items], 0)
  ```
* **Format String:** `0.0%`
* **Benchmark Value:** **24.5%**

### `[Loss-Making Products Count]`
* **DAX Formulation:**
  ```dax
  Loss-Making Products Count = 
  CALCULATE(
      DISTINCTCOUNT(fact_orders[product_key]),
      fact_orders[profit] < 0
  )
  ```
* **Business Meaning:** Count of unique catalog SKUs sold at an operational loss.
* **Format String:** `#,##0`

### `[Simulated Profit with 20% Discount Cap]`
* **DAX Formulation:**
  ```dax
  Simulated Profit (20% Cap) = 
  SUMX(
      fact_orders,
      VAR OriginalDiscount = fact_orders[discount]
      VAR CappedDiscount = MIN(OriginalDiscount, 0.20)
      VAR PriceLiftRatio = IF(OriginalDiscount > 0.20, (1 - CappedDiscount) / (1 - OriginalDiscount), 1)
      VAR SimulatedSales = fact_orders[sales] * PriceLiftRatio
      RETURN SimulatedSales - fact_orders[cogs] - fact_orders[shipping_cost]
  )
  ```
* **Business Meaning:** What-if simulation evaluating operating income recovery if discounts are restricted to a maximum 20% ceiling.
* **Format String:** `\$#,##0.00`
* **Projected Recovery:** **+\$248,500 in operating income**
