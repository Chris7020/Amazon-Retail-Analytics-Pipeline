select
    cast(date as date) as date,
    client_id,
    client_name,
    channel_type,
    asin,
    product_name,
    category,
    ordered_units,
    ordered_revenue,
    shipped_units,
    shipped_revenue
from raw.sales;
