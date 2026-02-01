# Time Doctor — Senior Data Analyst Assignment 

A reproducible analytics pipeline built with synthetic usage data, BigQuery, and dbt. This repository demonstrates how to go from raw event CSVs to a production-ready analytics layer with tests and documentation.

---

## Table of contents

- [Quick start](#quick-start)
- [Project structure](#project-structure)
- [Data model](#data-model)
- [Run locally](#run-locally)
- [BigQuery instructions](#bigquery-instructions)
- [dbt workflow](#dbt-workflow)
- [Testing & validation](#testing--validation)
- [Docs & assumptions](#docs--assumptions)

---

## Quick start ⚡

Prerequisites:
- Python 3.9+ (recommended)
- Google Cloud SDK (`bq`)
- dbt (configured for BigQuery)

Install Python deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Generate example data:

```bash
python scripts/generate_dummy_data.py
# output: data/raw/dim_account.csv, data/raw/dim_user.csv, data/raw/fct_event.csv
```

---

## Project structure 

```
time-doctor-data-analyst-assignment/
├── data/raw/          # generated CSVs
├── scripts/           # data generation scripts
├── docs/              # model design, assumptions, dictionary
├── td_analytics/      # dbt project (models, tests, macros)
└── README.md          # this file
```

---

## Data model 

Primary entities:
- **Accounts** — account-level metadata
- **Users** — user profiles and attributes
- **Events** — raw task/activity events (source of truth for metrics)

See `/docs` for context, and metric definitions.

---

## Run locally / dbt workflow 🔧

1. Validate dbt connection:

```bash
dbt debug
```

2. Run staging models (clean & standardize raw data):

```bash
dbt run --select staging
```

3. Run marts (analytics tables):

```bash
dbt run --select marts
```

4. Run tests:

```bash
dbt test
```

Tip: You can select a single model for iterative development, e.g.:

```bash
dbt run -s fct_daily_account_health
dbt test -s fct_daily_account_health
```

---

## BigQuery instructions 

Create dataset:

```bash
bq mkdir --dataset td_assignment
```

Load generated CSVs into raw tables:

```bash
bq load --autodetect --source_format=CSV td_assignment.raw_dim_account data/raw/dim_account.csv
bq load --autodetect --source_format=CSV td_assignment.raw_dim_user data/raw/dim_user.csv
bq load --autodetect --source_format=CSV td_assignment.raw_fct_event data/raw/fct_event.csv
```

> Note: Adjust dataset and table names to match your BigQuery environment and permission model.

---

## Testing & validation 

- dbt tests are defined in `td_analytics/models/*/schema.yml` (schema and data tests)
- Run `dbt test` after `dbt run` to validate assumptions

---

## Docs & assumptions

See `docs/` for:
- Context & scope
- Data dictionary
- Assumptions
- Metric definitions 

---

## Author

Ana Recio



