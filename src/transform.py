"""
Transformation layer: raw → staged → curated.

Key changes from original
-------------------------
* _safe_divide() replaces the inline .replace(0, pd.NA) pattern so the logic
  is reusable and the intent is explicit.
* The per-column fillna loop is replaced by a single vectorised call.
* Every DataFrame gets reset_index(drop=True) after sort_values so the exported
  index is always sequential (0-based).
* Staging writes are added for each source so the intermediate layer is
  populated (it existed in config but was unused).
* Dimension building is extracted from build_fact_table into build_dimensions()
  so build_fact_table has a single responsibility.
* date parsing is done explicitly with pd.to_datetime rather than relying on
  the read_csv parse_dates kwarg so the format is consistent regardless of
  how data arrives.
"""

from __future__ import annotations

import pandas as pd

from utils import CURATED_DIR, KEYS, RAW_DIR, STAGED_DIR, read_csv, setup_logging, write_csv

log = setup_logging("transform")

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

_NUMERIC_FILL_ZERO = [
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

_ORDERED_COLUMNS = [
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


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """
    Divide two Series, returning NaN wherever the denominator is 0 or null.

    Using .where() avoids dtype coercion issues that can arise with
    .replace(0, pd.NA) on integer columns.
    """
    safe_denom = denominator.where(denominator > 0)  # NaN where 0 or negative
    return numerator / safe_denom


# --------------------------------------------------------------------------- #
# Staging transforms
# --------------------------------------------------------------------------- #

def _stage(file_name: str, staged_name: str) -> pd.DataFrame:
    """Load one raw file, normalise column names and date type, write to staged."""
    df = read_csv(RAW_DIR / file_name)
    df.columns = df.columns.str.strip().str.lower()
    df["date"] = pd.to_datetime(df["date"])
    write_csv(df, STAGED_DIR / staged_name)
    log.info("Staged %s → %s  (%d rows)", file_name, staged_name, len(df))
    return df


def transform_sales() -> pd.DataFrame:
    return _stage("sales.csv", "stg_sales.csv")


def transform_traffic() -> pd.DataFrame:
    return _stage("traffic.csv", "stg_traffic.csv")


def transform_ad_spend() -> pd.DataFrame:
    return _stage("ad_spend.csv", "stg_ad_spend.csv")


# --------------------------------------------------------------------------- #
# Dimension builders  (called from build_dimensions, not build_fact_table)
# --------------------------------------------------------------------------- #

def build_dim_clients(fact_df: pd.DataFrame) -> pd.DataFrame:
    dim = (
        fact_df[["client_id", "client_name", "channel_type"]]
        .drop_duplicates()
        .sort_values("client_id")
        .reset_index(drop=True)
    )
    write_csv(dim, CURATED_DIR / "dim_clients.csv")
    log.info("Built dim_clients  (%d rows)", len(dim))
    return dim


def build_dim_products(fact_df: pd.DataFrame) -> pd.DataFrame:
    dim = (
        fact_df[["asin", "product_name", "category"]]
        .drop_duplicates()
        .sort_values("asin")
        .reset_index(drop=True)
    )
    write_csv(dim, CURATED_DIR / "dim_products.csv")
    log.info("Built dim_products  (%d rows)", len(dim))
    return dim


def build_dim_dates(fact_df: pd.DataFrame) -> pd.DataFrame:
    dim = (
        fact_df[["date"]]
        .drop_duplicates()
        .sort_values("date")
        .reset_index(drop=True)
        .copy()
    )
    dim["year"]         = dim["date"].dt.year
    dim["month"]        = dim["date"].dt.month
    dim["day"]          = dim["date"].dt.day
    dim["week"]         = dim["date"].dt.isocalendar().week.astype(int)
    dim["weekday_name"] = dim["date"].dt.day_name()
    write_csv(dim, CURATED_DIR / "dim_dates.csv")
    log.info("Built dim_dates  (%d rows)", len(dim))
    return dim


def build_dimensions(fact_df: pd.DataFrame) -> None:
    """Build and persist all dimension tables from the fact DataFrame."""
    build_dim_clients(fact_df)
    build_dim_products(fact_df)
    build_dim_dates(fact_df)


# --------------------------------------------------------------------------- #
# Fact table
# --------------------------------------------------------------------------- #

def build_fact_table() -> pd.DataFrame:
    """
    Merge staged sources, compute derived metrics, and write the curated fact
    table.  Dimension building is intentionally NOT done here; call
    build_dimensions(fact_df) separately so this function has a single
    responsibility and is easier to test.
    """
    sales    = transform_sales()
    traffic  = transform_traffic()
    ad_spend = transform_ad_spend()

    df = (
        sales
        .merge(traffic,  on=KEYS, how="left")
        .merge(ad_spend, on=KEYS, how="left")
    )

    # Vectorised fill — replaces the original per-column for-loop
    df[_NUMERIC_FILL_ZERO] = df[_NUMERIC_FILL_ZERO].fillna(0)

    # Derived metrics — safe divide returns NaN instead of raising on 0
    df["conversion_rate"] = _safe_divide(df["ordered_units"],  df["sessions"])
    df["roas"]            = _safe_divide(df["ordered_revenue"], df["spend"])
    df["cpc"]             = _safe_divide(df["spend"],           df["clicks"])

    df = (
        df[_ORDERED_COLUMNS]
        .sort_values(KEYS)
        .reset_index(drop=True)
    )

    write_csv(df, CURATED_DIR / "fct_daily_asin_performance.csv")
    log.info("Built fct_daily_asin_performance  (%d rows)", len(df))
    return df
