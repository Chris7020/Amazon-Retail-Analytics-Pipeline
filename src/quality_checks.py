import pandas as pd
from utils import CURATED_DIR, read_csv

KEYS = ["date", "client_id", "asin"]


def run_quality_checks() -> None:
    df = read_csv(CURATED_DIR / "fct_daily_asin_performance.csv")
    df["date"] = pd.to_datetime(df["date"])

    required_cols = ["date", "client_id", "asin", "ordered_units", "ordered_revenue"]
    for col in required_cols:
        if df[col].isnull().any():
            raise ValueError(f"Null values found in required column: {col}")

    duplicate_count = df.duplicated(subset=KEYS).sum()
    if duplicate_count > 0:
        raise ValueError(f"Duplicate grain detected: {duplicate_count} duplicate rows")

    negative_columns = [
        "ordered_units",
        "ordered_revenue",
        "shipped_units",
        "shipped_revenue",
        "spend",
        "clicks",
        "impressions",
    ]
    for col in negative_columns:
        if (df[col] < 0).any():
            raise ValueError(f"Negative values found in column: {col}")

    max_date = df["date"].max()
    if pd.isna(max_date):
        raise ValueError("Freshness check failed: max date is null")

    print("All quality checks passed.")
