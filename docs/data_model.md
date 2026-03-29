# Data Model

## Fact Table
### fct_daily_asin_performance
**Grain:** one row per `date + client_id + asin`

### Measures
- ordered_units
- ordered_revenue
- shipped_units
- shipped_revenue
- glance_views
- sessions
- spend
- clicks
- impressions
- conversion_rate
- roas
- cpc

## Dimensions

### dim_clients
- client_id
- client_name
- channel_type

### dim_products
- asin
- product_name
- category

### dim_dates
- date
- year
- month
- day
- week
- weekday_name
