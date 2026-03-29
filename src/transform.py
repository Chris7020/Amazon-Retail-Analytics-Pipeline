import pandas as pd
        fact_df[["asin", "product_name", "category"]]
        .drop_duplicates()
        .sort_values(["asin"])
    )
    write_csv(dim_products, CURATED_DIR / "dim_products.csv")
    return dim_products


def build_dim_dates(fact_df: pd.DataFrame) -> pd.DataFrame:
    dim_dates = fact_df[["date"]].drop_duplicates().sort_values(["date"]).copy()
    dim_dates["year"] = dim_dates["date"].dt.year
    dim_dates["month"] = dim_dates["date"].dt.month
    dim_dates["day"] = dim_dates["date"].dt.day
    dim_dates["week"] = dim_dates["date"].dt.isocalendar().week.astype(int)
    dim_dates["weekday_name"] = dim_dates["date"].dt.day_name()
    write_csv(dim_dates, CURATED_DIR / "dim_dates.csv")
    return dim_dates


def build_fact_table() -> pd.DataFrame:
    sales = transform_sales()
    traffic = transform_traffic()
    ad_spend = transform_ad_spend()

    df = (
        sales
        .merge(traffic, on=KEYS, how="left")
        .merge(ad_spend, on=KEYS, how="left")
    )

    numeric_fill_zero = [
        "glance_views",
        "sessions",
        "spend",
        "clicks",
        "impressions",
        "ordered_units",
        "ordered_revenue",
        "shipped_units",
        "shipped_revenue",
    ]

    for col in numeric_fill_zero:
        df[col] = df[col].fillna(0)

    df["conversion_rate"] = df["ordered_units"] / df["sessions"].replace(0, pd.NA)
    df["roas"] = df["ordered_revenue"] / df["spend"].replace(0, pd.NA)
    df["cpc"] = df["spend"] / df["clicks"].replace(0, pd.NA)

    ordered_columns = [
        "date",
        "client_id",
        "client_name",
        "channel_type",
        "asin",
        "product_name",
        "category",
        "ordered_units",
        "ordered_revenue",
        "shipped_units",
        "shipped_revenue",
        "glance_views",
        "sessions",
        "spend",
        "clicks",
        "impressions",
        "conversion_rate",
        "roas",
        "cpc",
    ]

    df = df[ordered_columns].sort_values(["date", "client_id", "asin"])
    write_csv(df, CURATED_DIR / "fct_daily_asin_performance.csv")

    build_dim_clients(df)
    build_dim_products(df)
    build_dim_dates(df)

    return df
