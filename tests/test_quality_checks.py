import pandas as pd


def test_unique_grain_passes():
    df = pd.DataFrame(
        {
            "date": ["2026-01-01", "2026-01-02"],
            "client_id": [1001, 1001],
            "asin": ["B001", "B001"],
        }
    )

    assert df.duplicated(subset=["date", "client_id", "asin"]).sum() == 0
