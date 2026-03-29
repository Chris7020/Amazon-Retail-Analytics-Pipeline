# Amazon-Retail-Analytics-Pipeline
Production-style analytics engineering pipeline that ingests mock retail and ad data, transforms it into curated fact/dimension tables, and applies automated data quality checks for BI-ready reporting

## Overview
This project simulates a production-style analytics engineering pipeline for retail and advertising data. It ingests mock sales, traffic, and ad spend datasets, transforms them into analytics-ready tables, applies data quality checks, and produces curated outputs for BI reporting.

## Business Problem
Retail and marketing teams often rely on siloed datasets across sales, traffic, and ad platforms. This project demonstrates how to build a unified daily performance model at the client and product level for downstream reporting and analysis.

## Architecture
Mock CSV / API-style source → Python ingestion → Raw layer → Staging transforms → Curated fact and dimension tables → Data quality checks → BI-ready output

## Tech Stack
- Python
- SQL
- Pandas
- YAML config
- AWS-style layered design (raw / staged / curated)
- Tableau-ready output structure

## Data Model

### Fact Table
**fct_daily_asin_performance**
- Grain: one row per `date + client_id + asin`

### Dimension Tables
- dim_clients
- dim_products
- dim_dates

## Data Quality Checks
- Required fields not null
- Unique grain validation
- No negative revenue, units, or spend
- Freshness check on latest load date

## Key Features
- Modular ingestion and transformation scripts
- Analytics-ready dimensional modeling
- Automated validation checks
- Portfolio-safe production-style structure

## Example Metrics
- Ordered Revenue
- Ordered Units
- Shipped Revenue
- Glance Views
- Sessions
- Ad Spend
- ROAS
- Conversion Rate
- CPC

## How to Run
```bash
pip install -r requirements.txt
python src/main.py
