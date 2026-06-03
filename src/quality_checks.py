"""
Data quality checks for the curated fact table.

Key changes from original
-------------------------
* KEYS is imported from utils (was re-defined locally — duplicate source of truth).
* run_quality_checks() accepts an optional DataFrame so tests can call it
  in-memory without needing a file on disk.
* The freshness check now compares max_date against today rather than only
  checking for null; threshold comes from config.
* Each sub-check is its own function so individual checks can be unit-tested
  and the failure point is immediately clear.
* glance_views added to the non-negative check (was missing in original).
* Column-existence check added before null check so KeyError is never raised
  silently.
"""

from __future__ import annotations

import pandas as pd

from utils import CONFIG, CURATED_DIR, KEYS, read_csv, setup_logging

log = setup_logging("quality_checks")

_REQUIRED_COLS = ["date", "client_id", "asin", "ordered_units", "ordered_revenue"]

_NON_NEGATIVE_COLS = [
    "ordered_units",
    "ordered_revenue",
    "shipped_units",
    "shipped_revenue",
    "glance_views",   # was missing from original
    "spend",
    "clicks",
    "impressions",
]

_FRESHNESS_MAX_AGE_DAYS: int = CONFIG.get("freshness_max_age_days", 90)


# --------------------------------------------------------------------------- #
# Individual checks (public so they can be imported by tests)
# --------------------------------------------------------------------------- #

def check_required_fields(df: pd.DataFrame) -> None:
    """Raise ValueError if any required column is missing or contains nulls."""
    for col in _REQUIRED_COLS:
        if col not in df.columns:
            raise ValueError(f"Missing required column: '{col}'")
        null_count = int(df[col].isnull().sum())
        if null_count > 0:
            raise ValueError(
                f"Null values in required column '{col}': {null_count} row(s)"
            )


def check_unique_grain(df: pd.DataFrame) -> None:
    """Raise ValueError if any date + client_id + asin combination is duplicated."""
    dupe_count = int(df.duplicated(subset=KEYS).sum())
    if dupe_count > 0:
        raise ValueError(
            f"Duplicate grain detected: {dupe_count} row(s) violate {KEYS}"
        )


def check_non_negative(df: pd.DataFrame) -> None:
    """Raise ValueError if any metric column contains a negative value."""
    for col in _NON_NEGATIVE_COLS:
        if col not in df.columns:
            continue
        neg_count = int((df[col] < 0).sum())
        if neg_count > 0:
            raise ValueError(
                f"Negative values in '{col}': {neg_count} row(s)"
            )


def check_freshness(
    df: pd.DataFrame,
    max_age_days: int = _FRESHNESS_MAX_AGE_DAYS,
) -> None:
    """
    Raise ValueError if the most-recent record is older than max_age_days.

    The original only checked that max_date was not null, which meant a dataset
    from years ago would pass.
    """
    max_date = df["date"].max()
    if pd.isna(max_date):
        raise ValueError("Freshness check: 'date' column contains no valid dates")
    age_days = (pd.Timestamp.today().normalize() - pd.Timestamp(max_date)).days
    if age_days > max_age_days:
        raise ValueError(
            f"Freshness check: most recent data is {age_days} day(s) old "
            f"(threshold: {max_age_days})"
        )


# --------------------------------------------------------------------------- #
# Orchestrator
# --------------------------------------------------------------------------- #

def run_quality_checks(df: pd.DataFrame | None = None) -> None:
    """
    Run all quality checks.

    Parameters
    ----------
    df : pd.DataFrame, optional
        Pass the in-memory fact DataFrame to avoid an extra disk read.  If
        omitted the function reads from the curated output path (useful for
        standalone / post-hoc runs).
    """
    if df is None:
        df = read_csv(CURATED_DIR / "fct_daily_asin_performance.csv")
        df["date"] = pd.to_datetime(df["date"])

    log.info("Quality checks starting  (%d rows)", len(df))

    check_required_fields(df)
    log.info("  ✓ required fields")

    check_unique_grain(df)
    log.info("  ✓ unique grain (%s)", KEYS)

    check_non_negative(df)
    log.info("  ✓ non-negative values")

    check_freshness(df)
    log.info("  ✓ data freshness (threshold: %d days)", _FRESHNESS_MAX_AGE_DAYS)

    log.info("All quality checks passed")
