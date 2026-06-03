"""
Unit tests for quality_checks.py.

The original test file had a critical bug: test_unique_grain_passes() called
pandas' duplicated() directly rather than any function from quality_checks.py,
so the test suite gave false confidence — a broken check_unique_grain() would
still produce a green test run.

Every test here imports and calls the actual check functions.
"""

from __future__ import annotations

import pandas as pd
import pytest

# Adjust the import path if running pytest from the repo root with src/ on
# PYTHONPATH (e.g. pytest --import-mode=importlib or via conftest.py sys.path).
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from quality_checks import (
    check_freshness,
    check_non_negative,
    check_required_fields,
    check_unique_grain,
)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _make_df(**overrides) -> pd.DataFrame:
    """Return a valid fact DataFrame, with any column replaced via overrides."""
    base: dict = {
        "date":            pd.to_datetime(["2026-05-01", "2026-05-02"]),
        "client_id":       [1001, 1001],
        "asin":            ["B001", "B001"],
        "ordered_units":   [10, 20],
        "ordered_revenue": [100.0, 200.0],
        "shipped_units":   [10, 20],
        "shipped_revenue": [100.0, 200.0],
        "glance_views":    [500, 600],
        "spend":           [50.0, 60.0],
        "clicks":          [20, 30],
        "impressions":     [1000, 1200],
        "sessions":        [200, 250],
    }
    base.update(overrides)
    return pd.DataFrame(base)


# --------------------------------------------------------------------------- #
# check_required_fields
# --------------------------------------------------------------------------- #

def test_required_fields_passes():
    check_required_fields(_make_df())  # must not raise


def test_required_fields_raises_on_null_value():
    df = _make_df(ordered_revenue=[None, 200.0])
    with pytest.raises(ValueError, match="Null values in required column 'ordered_revenue'"):
        check_required_fields(df)


def test_required_fields_raises_on_missing_column():
    df = _make_df().drop(columns=["asin"])
    with pytest.raises(ValueError, match="Missing required column: 'asin'"):
        check_required_fields(df)


# --------------------------------------------------------------------------- #
# check_unique_grain
# --------------------------------------------------------------------------- #

def test_unique_grain_passes():
    check_unique_grain(_make_df())  # must not raise


def test_unique_grain_raises_on_duplicate_rows():
    df = _make_df(
        date=pd.to_datetime(["2026-05-01", "2026-05-01"]),
        client_id=[1001, 1001],
        asin=["B001", "B001"],
    )
    with pytest.raises(ValueError, match="Duplicate grain detected"):
        check_unique_grain(df)


# --------------------------------------------------------------------------- #
# check_non_negative
# --------------------------------------------------------------------------- #

def test_non_negative_passes():
    check_non_negative(_make_df())  # must not raise


@pytest.mark.parametrize("col", [
    "ordered_units", "ordered_revenue", "shipped_units", "shipped_revenue",
    "glance_views", "spend", "clicks", "impressions",
])
def test_non_negative_raises_for_each_column(col):
    df = _make_df(**{col: [-1, 10]})
    with pytest.raises(ValueError, match=f"Negative values in '{col}'"):
        check_non_negative(df)


def test_non_negative_skips_missing_optional_column():
    """Columns absent from the DataFrame should be silently skipped."""
    df = _make_df().drop(columns=["shipped_units"])
    check_non_negative(df)  # must not raise


# --------------------------------------------------------------------------- #
# check_freshness
# --------------------------------------------------------------------------- #

def test_freshness_passes_for_recent_data():
    check_freshness(_make_df(), max_age_days=9999)  # must not raise


def test_freshness_raises_for_old_data():
    df = _make_df(date=pd.to_datetime(["2020-01-01", "2020-01-02"]))
    with pytest.raises(ValueError, match="Freshness check"):
        check_freshness(df, max_age_days=30)


def test_freshness_raises_when_all_dates_null():
    df = _make_df(date=[pd.NaT, pd.NaT])
    with pytest.raises(ValueError, match="no valid dates"):
        check_freshness(df)
