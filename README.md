# Amazon Retail Analytics Pipeline

Production-style analytics engineering pipeline that ingests retail and advertising data, transforms it into analytics-ready models, and applies automated data quality checks for BI reporting.

---

## Overview

This project simulates a real-world analytics engineering workflow for retail and marketing data. It consolidates sales, traffic, and ad spend into a unified dataset using a layered ELT architecture.

The pipeline mirrors cloud data warehouse design patterns (e.g., Redshift or Snowflake) using a local, file-based implementation.

---

## Business Problem

Retail and marketing teams often rely on fragmented datasets across multiple sources, including:

- Sales (revenue, units)
- Traffic (sessions, views)
- Advertising (spend, clicks)

This project demonstrates how to:

- Centralise disparate datasets
- Standardise transformation logic
- Build a unified performance model
- Enable downstream analytics and reporting

---

## Architecture

```
Source Data (CSV / API-style)
        ↓
Python Ingestion Layer   ← schema validation + column normalisation
        ↓
Raw Layer      (data/raw/)
        ↓
Staging Layer  (data/staged/)   ← now populated (stg_sales, stg_traffic, stg_ad_spend)
        ↓
Curated Layer  (data/curated/)
        ↓
Data Quality Checks
        ↓
Analytics-Ready Dataset
```

---

## Tech Stack

- **Python** — Pandas, modular pipeline design, `logging` for structured output
- **SQL** — DDL and transformation logic
- **YAML** — configuration-driven pipeline (paths, schemas, thresholds)
- **File-based data layers** — raw, staged, curated
- **Warehouse-style data modeling** — fact and dimension tables
- **pytest** — unit tests with `pytest-cov` for coverage reporting

---

## Data Model

### Fact Table — `fct_daily_asin_performance`

Grain: one row per `date + client_id + asin`

| Column | Description |
|---|---|
| date | Report date |
| client_id | Client identifier |
| client_name | Client display name |
| channel_type | Sales channel (e.g. vendor, seller) |
| asin | Amazon Standard Identification Number |
| product_name | Product display name |
| category | Product category |
| ordered_units | Units ordered |
| ordered_revenue | Revenue from orders |
| shipped_units | Units shipped |
| shipped_revenue | Revenue from shipments |
| glance_views | Product page views |
| sessions | Unique visitor sessions |
| spend | Ad spend |
| clicks | Ad clicks |
| impressions | Ad impressions |
| conversion_rate | `ordered_units / sessions` (NaN where sessions = 0) |
| roas | `ordered_revenue / spend` (NaN where spend = 0) |
| cpc | `spend / clicks` (NaN where clicks = 0) |

### Dimension Tables

**`dim_clients`** — client_id, client_name, channel_type  
**`dim_products`** — asin, product_name, category  
**`dim_dates`** — date, year, month, day, week, weekday_name

---

## Key Features

- Modular pipeline design (ingestion, transformation, validation)
- Layered architecture (raw → staged → curated) — all three layers populated
- Schema validation at ingestion — catches missing columns before they cause downstream failures
- Column name normalisation at the source boundary (strip + lowercase)
- Safe division for derived metrics — returns NaN instead of raising on zero denominators
- Vectorised `fillna` across numeric columns
- Structured logging via Python's `logging` module — no bare `print()` calls
- Configurable freshness threshold — fails if most-recent data exceeds `freshness_max_age_days`
- `run_quality_checks()` accepts an in-memory DataFrame so it can be called without a disk read
- Individual check functions (`check_required_fields`, `check_unique_grain`, etc.) are importable and independently testable
- `sys.exit(1)` on pipeline failure so schedulers and CI systems detect errors correctly

---

## Data Quality Checks

| Check | Details |
|---|---|
| Required fields | No nulls in `date`, `client_id`, `asin`, `ordered_units`, `ordered_revenue` |
| Unique grain | No duplicate `date + client_id + asin` combinations |
| Non-negative values | `ordered_units`, `ordered_revenue`, `shipped_units`, `shipped_revenue`, `glance_views`, `spend`, `clicks`, `impressions` |
| Data freshness | Most-recent record must be within `freshness_max_age_days` (default: 90, configurable in `config/pipeline_config.yaml`) |

---

## Project Structure

```
src/
  main.py            ← pipeline orchestrator (error handling, timing, sys.exit on failure)
  utils.py           ← config loading, path constants, KEYS, logging factory, CSV helpers
  ingest.py          ← schema-validated ingestion into raw layer
  transform.py       ← staging + curated transforms, fact + dimension builders
  quality_checks.py  ← individual check functions + run_quality_checks() orchestrator

config/
  pipeline_config.yaml   ← paths, required files, business keys, schemas, freshness threshold

data/
  source/            ← sample input CSVs (sales.csv, traffic.csv, ad_spend.csv)
  raw/               ← ingested copies (created at runtime)
  staged/            ← cleaned per-source files (created at runtime)
  curated/           ← final analytics-ready outputs (created at runtime)

sql/                 ← DDL and transformation queries
docs/                ← data model documentation
tests/
  conftest.py        ← shared pytest fixtures
  test_quality_checks.py
  test_transforms.py

requirements.txt
```

---

## Configuration

Key settings in `config/pipeline_config.yaml`:

```yaml
freshness_max_age_days: 90   # raise if most-recent record is older than this

schemas:                     # column contracts validated at ingestion
  sales.csv:
    required_columns: [date, client_id, ...]
  traffic.csv:
    required_columns: [date, client_id, asin, glance_views, sessions]
  ad_spend.csv:
    required_columns: [date, client_id, asin, spend, clicks, impressions]
```

---

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run the full pipeline
python src/main.py

# Run tests
pytest tests/

# Run tests with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

---

## Output

The pipeline produces the following files under `data/curated/`:

| File | Description |
|---|---|
| `fct_daily_asin_performance.csv` | Main analytics fact table |
| `dim_clients.csv` | Client dimension |
| `dim_products.csv` | Product dimension |
| `dim_dates.csv` | Date dimension |

These outputs are ready for BI tools, reporting, and downstream analytics.

---

## Author

Chris Atemkeng  
Senior Analytics and Data Engineer
