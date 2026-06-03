"""
Shared utilities: config loading, path constants, logging factory, CSV helpers.
All other modules import from here so paths and keys are never duplicated.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd
import yaml

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #

ROOT = Path(__file__).resolve().parent.parent
_CONFIG_PATH = ROOT / "config" / "pipeline_config.yaml"


def _load_config() -> dict:
    with open(_CONFIG_PATH) as fh:
        return yaml.safe_load(fh)


CONFIG: dict = _load_config()

SOURCE_DIR  = ROOT / CONFIG["source_path"]
RAW_DIR     = ROOT / CONFIG["raw_path"]
STAGED_DIR  = ROOT / CONFIG["staged_path"]
CURATED_DIR = ROOT / CONFIG["curated_path"]

# Single source of truth for business keys — driven by config, not hardcoded
KEYS: list[str] = CONFIG["business_keys"]


# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #

_FMT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FMT = "%Y-%m-%d %H:%M:%S"


def setup_logging(name: str = "pipeline") -> logging.Logger:
    """Return a logger with a stdout handler; idempotent across calls."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(_FMT, datefmt=_DATE_FMT))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


# --------------------------------------------------------------------------- #
# Directory management
# --------------------------------------------------------------------------- #

def ensure_directories() -> None:
    """Create all pipeline data directories if they don't already exist."""
    for directory in (RAW_DIR, STAGED_DIR, CURATED_DIR):
        directory.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------- #
# CSV helpers
# --------------------------------------------------------------------------- #

def read_csv(path: Path, parse_dates: list[str] | None = None) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=parse_dates)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
