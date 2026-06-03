"""
Unit tests for transform.py.
"""

from __future__ import annotations

import math
import sys
import pathlib

import pandas as pd
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from transform import (
    _safe_divide,
    build_dim_clients,
    build_dim_dates,
    build_dim_products,
)


# --------------------------------------------------------------------------- #
# _safe_divide
# --------------------------------------------------------------------------- #

def test_safe_divide_normal():
    num = pd.Series([10.0, 20.0])
    den = pd.Series([2.0, 4.0])
    result = _safe_divide(num, den)
    assert list(result) == [5.0, 5.0]


def test_safe_divide_zero_denominator_returns_nan():
    num = pd.Series([10.0, 20.0])
    den = pd.Series([0.0, 4.0])
    result = _safe_divide(num, den)
    assert math.isnan(result.iloc[0])
    assert result.iloc[1] == 5.0


def test_safe_divide_null_denominator_returns_nan():
    num = pd.Series([10.0])
    den = pd.Series([float("nan")])
    result = _safe_divide(num, den)
    assert math.isnan(result.iloc[0])


def test_safe_divide_zero_numerator():
    num = pd.Series([0.0])
    den = pd.Series([5.0])
    result = _safe_divide(num, den)
    assert result.iloc[0] == 0.0


# --------------------------------------------------------------------------- #
# Dimension builders
# --------------------------------------------------------------------------- #

@pytest.fixture()
def sample_fact() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date":          pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-01"]),
            "client_id":     [1001, 1001, 1002],
            "client_name":   ["Acme", "Acme", "BrandX"],
            "channel_type":  ["vendor", "vendor", "seller"],
            "asin":          ["B001", "B001", "B002"],
            "product_name":  ["Widget A", "Widget A", "Gadget B"],
            "category":      ["Electronics", "Electronics", "Home"],
            "ordered_units": [10, 20, 5],
        }
    )


def test_build_dim_clients_deduplicates(sample_fact, tmp_path, monkeypatch):
    import transform as tr
    monkeypatch.setattr(tr, "CURATED_DIR", tmp_path)
    dim = build_dim_clients(sample_fact)
    assert len(dim) == 2
    assert list(dim.columns) == ["client_id", "client_name", "channel_type"]
    assert dim.index.tolist() == [0, 1]  # sequential after reset_index


def test_build_dim_products_deduplicates(sample_fact, tmp_path, monkeypatch):
    import transform as tr
    monkeypatch.setattr(tr, "CURATED_DIR", tmp_path)
    dim = build_dim_products(sample_fact)
    assert len(dim) == 2
    assert list(dim.columns) == ["asin", "product_name", "category"]
    assert dim.index.tolist() == [0, 1]


def test_build_dim_dates_columns(sample_fact, tmp_path, monkeypatch):
    import transform as tr
    monkeypatch.setattr(tr, "CURATED_DIR", tmp_path)
    dim = build_dim_dates(sample_fact)
    assert len(dim) == 2  # two distinct dates
    for col in ("year", "month", "day", "week", "weekday_name"):
        assert col in dim.columns
    assert dim.index.tolist() == [0, 1]
