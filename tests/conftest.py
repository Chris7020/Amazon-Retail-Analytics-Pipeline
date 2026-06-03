"""Shared pytest fixtures for the test suite."""

from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture()
def valid_fact_df() -> pd.DataFrame:
    """A minimal, fully-valid fact DataFrame for use across test modules."""
    return pd.DataFrame(
        {
            "date":             pd.to_datetime(["2026-05-01", "2026-05-02"]),
            "client_id":        [1001, 1001],
            "asin":             ["B001", "B001"],
            "ordered_units":    [10, 20],
            "ordered_revenue":  [100.0, 200.0],
            "shipped_units":    [10, 20],
            "shipped_revenue":  [100.0, 200.0],
            "glance_views":     [500, 600],
            "spend":            [50.0, 60.0],
            "clicks":           [20, 30],
            "impressions":      [1000, 1200],
            "sessions":         [200, 250],
        }
    )
