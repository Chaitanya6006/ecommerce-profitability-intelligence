// ============================================================================
// Power Query (M) ETL Ingestion Scripts
// E-Commerce Profitability Intelligence Platform
// ============================================================================

// ----------------------------------------------------------------------------
// Parameter: DataFolderPath
// Set this to your local data/processed directory path in Power BI Desktop
// (Home -> Transform Data -> Manage Parameters)
// ----------------------------------------------------------------------------
let
    DataFolderPath = "C:\Users\Admin\Desktop\Ecommerce-Profitability-Intelligence\data\processed\" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
in
    DataFolderPath;

// ----------------------------------------------------------------------------
// Query 1: dim_customers
// ----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolderPath & "dim_customers.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders, {
        {"customer_key", Int64.Type},
        {"customer_id", type text},
        {"customer_name", type text},
        {"segment", type text}
    })
in
    ChangeTypes;

// ----------------------------------------------------------------------------
// Query 2: dim_products
// ----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolderPath & "dim_products.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders, {
        {"product_key", Int64.Type},
        {"product_id", type text},
        {"product_name", type text},
        {"category", type text},
        {"sub_category", type text}
    })
in
    ChangeTypes;

// ----------------------------------------------------------------------------
// Query 3: dim_geography
// ----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolderPath & "dim_geography.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders, {
        {"geography_key", Int64.Type},
        {"city", type text},
        {"state", type text},
        {"country", type text},
        {"region", type text},
        {"market", type text},
        {"postal_code", type text}
    })
in
    ChangeTypes;

// ----------------------------------------------------------------------------
// Query 4: dim_date
// ----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolderPath & "dim_date.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders, {
        {"date_key", Int64.Type},
        {"full_date", type date},
        {"day_of_month", Int64.Type},
        {"month", Int64.Type},
        {"month_name", type text},
        {"quarter", Int64.Type},
        {"year", Int64.Type},
        {"day_of_week", type text},
        {"is_weekend", Int64.Type}
    })
in
    ChangeTypes;

// ----------------------------------------------------------------------------
// Query 5: dim_shipping_mode
// ----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolderPath & "dim_shipping_mode.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders, {
        {"shipping_mode_key", Int64.Type},
        {"ship_mode", type text}
    })
in
    ChangeTypes;

// ----------------------------------------------------------------------------
// Query 6: fact_orders
// ----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolderPath & "fact_orders.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders, {
        {"row_id", Int64.Type},
        {"order_id", type text},
        {"customer_key", Int64.Type},
        {"product_key", Int64.Type},
        {"geography_key", Int64.Type},
        {"order_date_key", Int64.Type},
        {"ship_date_key", Int64.Type},
        {"shipping_mode_key", Int64.Type},
        {"sales", type number},
        {"quantity", Int64.Type},
        {"discount", type number},
        {"profit", type number},
        {"shipping_cost", type number},
        {"gross_sales", type number},
        {"discount_amount", type number},
        {"cogs", type number},
        {"lead_time_days", Int64.Type},
        {"order_priority", type text},
        {"is_returned", Int64.Type}
    })
in
    ChangeTypes;

// ----------------------------------------------------------------------------
// Query 7: fact_returns
// ----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents(DataFolderPath & "fact_returns.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders, {
        {"return_id", Int64.Type},
        {"order_id", type text},
        {"region", type text},
        {"returned_flag", type text}
    })
in
    ChangeTypes;
