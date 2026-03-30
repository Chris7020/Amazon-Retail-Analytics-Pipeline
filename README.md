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

- Centralize disparate datasets  
- Standardize transformation logic  
- Build a unified performance model  
- Enable downstream analytics and reporting  

---

## Architecture
Source Data (CSV / API-style)
↓
Python Ingestion Layer
↓
Raw Layer (data/raw)
↓
Staging Layer (data/staged)
↓
Curated Layer (data/curated)
↓
Data Quality Checks
↓
Analytics-Ready Dataset


---

## Tech Stack

- Python (Pandas, modular pipeline design)
- SQL (DDL and transformation logic)
- YAML (configuration-driven pipeline)
- File-based data layers (raw, staged, curated)
- Warehouse-style data modeling (fact and dimensions)

---

## Data Model

### Fact Table

**fct_daily_asin_performance**

Grain: one row per `date + client_id + asin`

#### Metrics

- ordered_units  
- ordered_revenue  
- shipped_units  
- shipped_revenue  
- glance_views  
- sessions  
- spend  
- clicks  
- impressions  
- conversion_rate  
- roas  
- cpc  

---

### Dimension Tables

**dim_clients**
- client_id  
- client_name  
- channel_type  

**dim_products**
- asin  
- product_name  
- category  

**dim_dates**
- date  
- year  
- month  
- day  
- week  
- weekday_name  

---

## Key Features

- Modular pipeline design (ingestion, transformation, validation)
- Layered architecture (raw, staged, curated)
- Analytics-ready dimensional modeling
- Automated data quality checks
- Business-oriented metrics (ROAS, conversion rate, CPC)

---

## Data Quality Checks

The pipeline validates:

- Required fields (no null values)
- Unique grain (`date + client_id + asin`)
- No negative values (revenue, units, spend)
- Data freshness

---

## Project Structure
src/ → pipeline logic (ingestion, transforms, checks)
sql/ → DDL and transformation queries
data/source/ → sample input data
data/raw/ → ingested raw data
data/staged/ → cleaned/staged data
data/curated/ → final analytics-ready outputs
config/ → pipeline configuration
docs/ → data model documentation
tests/ → validation tests


---

## How to Run
pip install -r requirements.txt
python src/main.py


---

## Output

The pipeline produces:

- fct_daily_asin_performance.csv  
- dim_clients.csv  
- dim_products.csv  
- dim_dates.csv  

These outputs are ready for BI tools, reporting, and downstream analytics.

---

## Why This Project Matters

This project demonstrates:

- End-to-end pipeline design  
- Data modeling for analytics  
- Data quality and validation practices  
- Business-aligned metric development  
- Production-style project structure  


---

## Author

Chris Atemkeng  
Senior Analytics and Data Engineer  
