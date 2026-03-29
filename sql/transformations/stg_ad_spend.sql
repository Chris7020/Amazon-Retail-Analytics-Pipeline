select
    cast(date as date) as date,
    client_id,
    asin,
    spend,
    clicks,
    impressions
from raw.ad_spend;
