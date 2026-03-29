select
    cast(date as date) as date,
    client_id,
    asin,
    glance_views,
    sessions
from raw.traffic;
