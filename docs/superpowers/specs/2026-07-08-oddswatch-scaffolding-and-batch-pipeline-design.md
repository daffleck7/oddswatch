# OddsWatch: Project Scaffolding & Batch Data Pipeline

## Overview

OddsWatch is a real-time sports betting odds and line-movement platform built for
MGMT 59000 (Cloud Computing: Data Engineering). This spec covers two deliverables:
project scaffolding and the batch historical data pipeline for MLB and FIFA World Cup
game data.

The batch pipeline ingests public game-result datasets, generates synthetic closing
lines grounded in real outcomes, and transforms the data through a bronze/silver/gold
medallion architecture on AWS (S3 + Glue Data Catalog).

## Tech Stack

- **Language**: Python 3.11+
- **Dependency management**: uv
- **Cloud**: AWS — S3 (storage), Glue Data Catalog (metadata), Redshift (future warehouse)
- **Data formats**: CSV (bronze), Parquet (silver/gold)
- **Libraries**: boto3, pandas, pyarrow, pydantic, python-dotenv, pytest

## Project Structure

```
oddswatch/
├── src/oddswatch/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py          # AWS settings, env vars, bucket names
│   ├── ingest/
│   │   ├── __init__.py
│   │   ├── mlb.py               # Download & upload MLB data to bronze
│   │   └── world_cup.py         # Download & upload World Cup data to bronze
│   ├── transform/
│   │   ├── __init__.py
│   │   ├── bronze_to_silver.py  # Cleaning, normalization, synthetic closing lines
│   │   └── silver_to_gold.py    # Star schema transformation
│   └── models/
│       ├── __init__.py
│       ├── bronze.py            # Raw data models
│       ├── silver.py            # Cleaned data models
│       └── gold.py              # Star schema models (facts + dimensions)
├── tests/
│   ├── __init__.py
│   ├── test_ingest.py
│   ├── test_bronze_to_silver.py
│   └── test_silver_to_gold.py
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

## Data Sources

### MLB Historical Game Results
- **Source**: Public dataset (Kaggle or Retrosheet) covering multiple MLB seasons
- **Fields expected**: date, home_team, away_team, home_score, away_score, season,
  venue (if available)
- **Format**: CSV

### FIFA World Cup Match Results
- **Source**: Public dataset (Kaggle) covering historical World Cup tournaments
- **Fields expected**: date, home_team, away_team, home_score, away_score,
  tournament, stage/round, city/venue
- **Format**: CSV

Both datasets provide real game outcomes only. Closing lines are synthetically
generated in the silver layer.

## Pipeline Design

### Bronze Layer

**Purpose**: Raw source of truth. No transformations.

**Process**:
1. Download CSV files from public sources
2. Upload as-is to `s3://<bucket>/bronze/mlb/` and `s3://<bucket>/bronze/world_cup/`
3. Register tables in Glue Data Catalog under database `oddswatch`

**Output**: Raw CSV files in S3, Glue tables pointing at bronze paths.

### Silver Layer

**Purpose**: Cleaned, normalized, typed data with synthetic closing lines.

**Transformations**:
- Standardize column names to snake_case, consistent across both sports
- Parse dates into proper date types
- Normalize team names to canonical forms
- Add `sport` column (`mlb` or `world_cup`)
- Generate synthetic closing lines derived from actual scores:
  - **Spread**: Derived from score differential with noise (e.g., a 5-2 game yields
    a closing spread around -2.5 to -3.5 for the winner)
  - **Total**: Derived from combined score with noise (e.g., 5+2=7, closing total
    around 6.5-8.5)
  - **Moneyline**: Derived from spread using standard implied-probability conversion
- Drop duplicates and handle nulls

**Output**: Parquet files in `s3://<bucket>/silver/`, partitioned by `sport` and
`season`/`year`. Cataloged in Glue.

### Gold Layer

**Purpose**: Star-schema-ready tables for analytics and warehouse loading.

#### Fact Table

**`fact_game_odds`** — one row per game:
- `game_key` (surrogate)
- `game_id`, `date_key`, `home_team_key`, `away_team_key`, `market_key`
- `closing_spread`, `closing_total`, `closing_moneyline_home`, `closing_moneyline_away`
- `home_score`, `away_score`
- `cover` (boolean — did the favorite cover the spread)
- `over_under_result` (over/under/push)
- `sport`

#### Dimension Tables

**`dim_team`**:
- `team_key` (surrogate), `team_id`, `team_name`, `sport`
- `conference` (MLB) / `group` (World Cup), `country` (World Cup)

**`dim_game`**:
- `game_key` (surrogate), `game_id`, `sport`, `season`/`tournament`
- `date`, `stage`/`round`, `home_team_id`, `away_team_id`, `venue`

**`dim_date`**:
- `date_key`, `date`, `day_of_week`, `month`, `year`, `is_weekend`

**`dim_market`**:
- `market_key` (surrogate), `market_type` (spread/total/moneyline), `description`

#### Placeholder Tables (for streaming layer)

**`dim_book`** — with SCD Type 2 columns (`valid_from`, `valid_to`, `is_current`).
Schema defined but empty until streaming layer populates it.

**`fact_odds_tick`** and **`fact_bet`** — schemas defined, empty. Will be populated
by the streaming pipeline.

**Output**: Parquet files in `s3://<bucket>/gold/`, cataloged in Glue.

## Configuration

All AWS and project settings via environment variables:
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
- `S3_BUCKET_NAME`
- `GLUE_DATABASE_NAME` (default: `oddswatch`)

A `.env.example` documents all required variables without values.

## Testing

- Framework: pytest
- Tests mirror source structure in `tests/`
- Each pipeline stage has unit tests validating transformations
- Synthetic closing-line generation tested against known score inputs
- Minimum 80% coverage target
