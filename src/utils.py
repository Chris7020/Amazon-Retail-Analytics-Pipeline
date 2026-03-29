from pathlib import Path
import pandas as pd
import yaml

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


CONFIG = load_config()
SOURCE_DIR = BASE_DIR / CONFIG["source_path"]
RAW_DIR = BASE_DIR / CONFIG["raw_path"]
STAGED_DIR = BASE_DIR / CONFIG["staged_path"]
CURATED_DIR = BASE_DIR / CONFIG["curated_path"]


def ensure_directories() -> None:
    for path in [SOURCE_DIR, RAW_DIR, STAGED_DIR, CURATED_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip().lower() for c in df.columns]
    return df
