"""
Ingestion layer: read source CSVs, validate schemas, write to raw layer.
"""

from __future__ import annotations

import pandas as pd

from utils import (
    CONFIG,
    SOURCE_DIR,
    RAW_DIR,
    ensure_directories,
    read_csv,
    setup_logging,
    write_csv,
)

log = setup_logging("ingest")


# --------------------------------------------------------------------------- #
# Schema validation
# --------------------------------------------------------------------------- #

def _validate_schema(df: pd.DataFrame, file_name: str) -> None:
    """
    Raise ValueError if the DataFrame is missing any column declared in the
    config schema for this file.  Column names are compared after normalising
    to lowercase + stripped whitespace.
    """
    schemas: dict = CONFIG.get("schemas", {})
    file_schema = schemas.get(file_name)
    if file_schema is None:
        return  # no schema defined — skip validation

    expected: set[str] = set(file_schema.get("required_columns", []))
    actual: set[str] = set(df.columns)
    missing = expected - actual
    if missing:
        raise ValueError(
            f"{file_name}: missing required columns: {sorted(missing)}"
        )


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def ingest_files() -> None:
    """
    Copy every required source file into the raw layer after normalising column
    names and validating the schema.

    Raises
    ------
    FileNotFoundError  if a required source file does not exist.
    ValueError         if a file fails schema validation.
    """
    ensure_directories()

    for file_name in CONFIG["required_source_files"]:
        src = SOURCE_DIR / file_name
        dst = RAW_DIR / file_name

        if not src.exists():
            raise FileNotFoundError(f"Missing source file: {src}")

        df = read_csv(src)

        # Normalise column names once at the boundary so downstream code can
        # rely on consistent names regardless of source formatting.
        df.columns = df.columns.str.strip().str.lower()

        _validate_schema(df, file_name)

        write_csv(df, dst)
        log.info("Ingested %s → %s  (%d rows)", file_name, dst, len(df))
