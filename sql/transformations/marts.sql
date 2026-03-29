select
    s.date,
    s.client_id,
    s.client_name,
    s.channel_type,
    s.asin,
    s.product_name,
    s.category,
    s.ordered_units,
    s.ordered_revenue,
    s.shipped_units,
    s.shipped_revenue,
    t.glance_views,
    t.sessions,
    a.spend,
    a.clicks,
    a.impressions,
    s.ordered_units / nullif(t.sessions, 0) as conversion_rate,
    s.ordered_revenue / nullif(a.spend, 0) as roas,
    a.spend / nullif(a.clicks, 0) as cpc
from stg_sales s
left join stg_traffic t
    on s.date = t.date
   and s.client_id = t.client_id
   and s.asin = t.asin
left join stg_ad_spend a
    on s.date = a.date
   and s.client_id = a.client_id
   and s.asin = a.asin;
