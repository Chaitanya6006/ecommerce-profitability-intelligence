# Power BI Data Model Architecture & Governance Specification
## E-Commerce Profitability Intelligence Platform

---

## 1. Dimensional Architecture Overview

The Power BI data model follows a **Kimball-style Star Schema**, optimized for fast in-memory DAX evaluation (VertiPaq engine), unambiguous filter propagation, and zero double-counting.

```
                  +-----------------------+
                  |     dim_customers     |
                  +-----------------------+
                  | PK  customer_key      |
                  |     customer_id       |
                  |     customer_name     |
                  |     segment           |
                  +-----------+-----------+
                              | 1
                              |
                              | N (Single)
+-----------------------+     +-----------------------+     +-----------------------+
|     dim_products      |     |      fact_orders      |     |     dim_geography     |
+-----------------------+     +-----------------------+     +-----------------------+
| PK  product_key       |<----+ PK  row_id            +---->| PK  geography_key     |
|     product_id        | 1  N| FK  customer_key      |N   1|     city              |
|     product_name      |     | FK  product_key       |     |     state             |
|     category          |     | FK  geography_key     |     |     country           |
|     sub_category      |     | FK  order_date_key    |     |     region            |
+-----------------------+     | FK  ship_date_key     |     |     market            |
                              | FK  shipping_mode_key |     |     postal_code       |
+-----------------------+     |     sales             |     +-----------------------+
|       dim_date        |     |     quantity          |
+-----------------------+     |     discount          |     +-----------------------+
| PK  date_key          |<----+     profit            |---->|   dim_shipping_mode   |
|     full_date         | 1  N|     shipping_cost     |N   1+-----------------------+
|     day_of_month      |     |     gross_sales       |     | PK  shipping_mode_key |
|     month             |     |     discount_amount   |     |     ship_mode         |
|     quarter           |     |     cogs              |     +-----------------------+
|     year              |     |     lead_time_days    |
|     is_weekend        |     |     is_returned       |
+-----------------------+     +-----------+-----------+
                                          |
                                          | (Isolated Fact Table)
                              +-----------+-----------+
                              |      fact_returns     |
                              +-----------------------+
                              | PK  return_id         |
                              |     order_id          |
                              |     region            |
                              |     returned_flag     |
                              +-----------------------+
```

---

## 2. Table Catalog & Granularity Definitions

| Table Name | Table Type | Primary Key | Record Count | Granularity (1 Row Represents) | Business Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`fact_orders`** | Fact (Transactional) | `row_id` | **51,290** | One order line item for a specific product SKU within an order. | Core transactional measures (Sales, Quantity, Discount, Profit, Shipping Cost, COGS, Lead Time). |
| **`fact_returns`** | Fact (Event Log) | `return_id` | **1,079** | One returned order event. | Audit log of returned order identifiers across regional operating hubs. |
| **`dim_customers`** | Dimension | `customer_key` | **17,415** | One unique customer account. | Customer profiling, cohort tracking, and market segment analysis (`Consumer`, `Corporate`, `Home Office`). |
| **`dim_products`** | Dimension | `product_key` | **3,788** | One unique product SKU catalog item. | Merchandise categorization (`Category`, `Sub-Category`, `Product Name`). |
| **`dim_geography`** | Dimension | `geography_key` | **3,856** | One distinct geographic market/locality. | Spatial hierarchy (`Market`, `Region`, `Country`, `State`, `City`, `Postal Code`). |
| **`dim_date`** | Dimension (Calendar) | `date_key` | **1,468** | One calendar day (2012-01-01 to 2016-01-07). | Time intelligence, fiscal quarters, MoM/YoY growth, seasonality. |
| **`dim_shipping_mode`**| Dimension | `shipping_mode_key` | **4** | One fulfillment service carrier tier. | Carrier SLA logistics performance (`Same Day`, `First Class`, `Second Class`, `Standard Class`). |

---

## 3. Relationship Matrix & Filtering Governance

| Relationship ID | From Table (Foreign Key) | To Table (Primary Key) | Cardinality | Cross-Filter | Active State | Purpose & Governance |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **R1** | `fact_orders[customer_key]` | `dim_customers[customer_key]` | Many to One ($N:1$) | Single | **Active** | Filters sales and profit by customer segments and cohorts. |
| **R2** | `fact_orders[product_key]` | `dim_products[product_key]` | Many to One ($N:1$) | Single | **Active** | Slices financial metrics by category and sub-category. |
| **R3** | `fact_orders[geography_key]` | `dim_geography[geography_key]` | Many to One ($N:1$) | Single | **Active** | Slices transactions across global markets, regions, and countries. |
| **R4** | `fact_orders[order_date_key]` | `dim_date[date_key]` | Many to One ($N:1$) | Single | **Active** | Primary date filter for order transaction date. |
| **R5** | `fact_orders[ship_date_key]` | `dim_date[date_key]` | Many to One ($N:1$) | Single | *Inactive* | Secondary fulfillment date. Invoked in DAX using `USERELATIONSHIP()`. |
| **R6** | `fact_orders[shipping_mode_key]`| `dim_shipping_mode[shipping_mode_key]`| Many to One ($N:1$) | Single | **Active** | Evaluates logistics performance and freight burden by carrier tier. |

---

## 4. Double-Counting Prevention & Modeling Rules

### 4.1 Returns Isolation Strategy (Avoiding Circular & Many-to-Many Pitfalls)
* In transactional retail databases, an order may contain multiple line items in `fact_orders`, but return records in `fact_returns` exist at the **Order ID level** ($1,079$ returned orders).
* **The Antipattern:** Creating a bidirectional relationship between `fact_orders[order_id]` and `fact_returns[order_id]` causes ambiguous filter paths, non-deterministic totals, and severe performance penalties in VertiPaq.
* **Our Solution:** The ETL pipeline pre-flags each line item with an integer `is_returned` attribute ($1$ if order was returned, $0$ if retained).
* **Benefits:** 
  1. $100\%$ determinism in single-direction filter propagation.
  2. Order return rates use explicit distinct count denominators:
     $$\text{Order Return Rate} = \frac{\text{DISTINCTCOUNT}( \text{Returned Orders} )}{\text{DISTINCTCOUNT}( \text{Total Orders} )}$$
  3. Zero row-multiplication or double-counting of sales volume.

### 4.2 Calendar Hierarchy & Month Sorting
* The column `dim_date[month_name]` (e.g., "January", "February") must be sorted in Power BI by `dim_date[month]` ($1, 2, \dots, 12$) to avoid alphabetical sorting ("April", "August", "December").
* Slicers use `dim_date[full_date]` or `dim_date[year]` for continuous timeline filtering.
