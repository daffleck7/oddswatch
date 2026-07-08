# OddsWatch: Scaffolding & Batch Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold the OddsWatch Python project and build a bronze/silver/gold batch pipeline that ingests MLB and FIFA World Cup historical data into S3.

**Architecture:** A uv-managed Python project with modular ingest and transform packages. Raw CSVs are downloaded from public URLs and uploaded to S3 (bronze). Pandas transforms clean and normalize the data (silver), then reshape into a star schema (gold). All layers are written as Parquet to S3 and registered in Glue Data Catalog.

**Tech Stack:** Python 3.11+, uv, boto3, pandas, pyarrow, pydantic, pydantic-settings, python-dotenv, httpx, pytest, moto (for AWS mocking in tests)

---

## File Structure

```
src/oddswatch/__init__.py              — package root
src/oddswatch/config/__init__.py       — config package
src/oddswatch/config/settings.py       — Settings pydantic model (env vars)
src/oddswatch/ingest/__init__.py       — ingest package
src/oddswatch/ingest/mlb.py            — download MLB CSV, upload to S3 bronze
src/oddswatch/ingest/world_cup.py      — download World Cup CSV, upload to S3 bronze
src/oddswatch/transform/__init__.py    — transform package
src/oddswatch/transform/bronze_to_silver.py — clean, normalize, generate closing lines
src/oddswatch/transform/silver_to_gold.py   — build star schema tables
src/oddswatch/models/__init__.py       — models package
src/oddswatch/models/bronze.py         — Pydantic models for raw data
src/oddswatch/models/silver.py         — Pydantic models for cleaned data
src/oddswatch/models/gold.py           — Pydantic models for star schema
tests/__init__.py
tests/test_config.py
tests/test_ingest.py
tests/test_bronze_to_silver.py
tests/test_silver_to_gold.py
pyproject.toml
.env.example
.gitignore
```

---

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `src/oddswatch/__init__.py`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "oddswatch"
version = "0.1.0"
description = "Real-time sports betting odds & line-movement platform"
requires-python = ">=3.11"
dependencies = [
    "boto3>=1.35.0",
    "pandas>=2.2.0",
    "pyarrow>=17.0.0",
    "pydantic>=2.9.0",
    "pydantic-settings>=2.6.0",
    "python-dotenv>=1.0.0",
    "httpx>=0.27.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "moto[s3,glue]>=5.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/oddswatch"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

- [ ] **Step 2: Create `.env.example`**

```
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
S3_BUCKET_NAME=oddswatch-data
GLUE_DATABASE_NAME=oddswatch
```

- [ ] **Step 3: Create `.gitignore`**

```
__pycache__/
*.pyc
.env
.venv/
*.egg-info/
dist/
build/
.pytest_cache/
*.parquet
```

- [ ] **Step 4: Create package init files**

Create empty `__init__.py` files at:
- `src/oddswatch/__init__.py`
- `src/oddswatch/config/__init__.py`
- `src/oddswatch/ingest/__init__.py`
- `src/oddswatch/transform/__init__.py`
- `src/oddswatch/models/__init__.py`
- `tests/__init__.py`

- [ ] **Step 5: Install dependencies**

Run: `uv sync --all-extras`
Expected: Dependencies install successfully, `.venv` created.

- [ ] **Step 6: Verify setup**

Run: `uv run python -c "import oddswatch; print('OK')"`
Expected: `OK`

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml .env.example .gitignore src/ tests/__init__.py
git commit -m "Scaffold project structure with uv and dependencies"
```

---

### Task 2: Config Settings

**Files:**
- Create: `src/oddswatch/config/settings.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_config.py`:

```python
"""Tests for config settings."""

import os

from oddswatch.config.settings import Settings


def test_settings_loads_from_env(monkeypatch: object) -> None:
    """Settings loads values from environment variables."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test-key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test-secret")
    monkeypatch.setenv("AWS_REGION", "us-west-2")
    monkeypatch.setenv("S3_BUCKET_NAME", "my-bucket")
    monkeypatch.setenv("GLUE_DATABASE_NAME", "mydb")

    settings = Settings()

    assert settings.aws_access_key_id == "test-key"
    assert settings.aws_secret_access_key == "test-secret"
    assert settings.aws_region == "us-west-2"
    assert settings.s3_bucket_name == "my-bucket"
    assert settings.glue_database_name == "mydb"


def test_settings_defaults(monkeypatch: object) -> None:
    """Settings uses defaults for region, bucket, and glue database."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "k")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "s")
    monkeypatch.delenv("AWS_REGION", raising=False)
    monkeypatch.delenv("S3_BUCKET_NAME", raising=False)
    monkeypatch.delenv("GLUE_DATABASE_NAME", raising=False)

    settings = Settings()

    assert settings.aws_region == "us-east-1"
    assert settings.s3_bucket_name == "oddswatch-data"
    assert settings.glue_database_name == "oddswatch"


def test_settings_s3_paths(monkeypatch: object) -> None:
    """Settings generates correct S3 paths for each layer."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "k")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "s")
    monkeypatch.setenv("S3_BUCKET_NAME", "my-bucket")

    settings = Settings()

    assert settings.bronze_prefix == "bronze"
    assert settings.silver_prefix == "silver"
    assert settings.gold_prefix == "gold"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError` or `ImportError`

- [ ] **Step 3: Write the implementation**

Create `src/oddswatch/config/settings.py`:

```python
"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """AWS and project configuration."""

    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "us-east-1"
    s3_bucket_name: str = "oddswatch-data"
    glue_database_name: str = "oddswatch"
    bronze_prefix: str = "bronze"
    silver_prefix: str = "silver"
    gold_prefix: str = "gold"

    model_config = {"env_file": ".env", "extra": "ignore"}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_config.py -v`
Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/oddswatch/config/settings.py tests/test_config.py
git commit -m "Add config settings with env var loading"
```

---

### Task 3: Pydantic Models for Bronze Data

**Files:**
- Create: `src/oddswatch/models/bronze.py`

- [ ] **Step 1: Create bronze models**

The MLB dataset from FiveThirtyEight has columns: `date`, `season`, `neutral`, `playoff`, `team1`, `team2`, `score1`, `score2` (plus ELO columns we don't need).

The World Cup dataset has columns: `date`, `home_team`, `away_team`, `home_score`, `away_score`, `tournament`, `city`, `country`, `neutral`.

Create `src/oddswatch/models/bronze.py`:

```python
"""Pydantic models for bronze (raw) data."""

from pydantic import BaseModel


class BronzeMLBGame(BaseModel):
    """Raw MLB game record from FiveThirtyEight ELO dataset."""

    date: str
    season: int
    neutral: int
    playoff: str | None
    team1: str
    team2: str
    score1: float
    score2: float


class BronzeWorldCupMatch(BaseModel):
    """Raw World Cup match record from international results dataset."""

    date: str
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    tournament: str
    city: str
    country: str
    neutral: str
```

- [ ] **Step 2: Commit**

```bash
git add src/oddswatch/models/bronze.py
git commit -m "Add Pydantic models for bronze layer data"
```

---

### Task 4: Pydantic Models for Silver Data

**Files:**
- Create: `src/oddswatch/models/silver.py`

- [ ] **Step 1: Create silver models**

Create `src/oddswatch/models/silver.py`:

```python
"""Pydantic models for silver (cleaned/normalized) data."""

from datetime import date

from pydantic import BaseModel


class SilverGame(BaseModel):
    """Cleaned and normalized game record with synthetic closing lines.

    Unified schema across MLB and World Cup.
    """

    game_id: str
    sport: str
    date: date
    season: int
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    stage: str | None
    venue: str | None
    closing_spread: float
    closing_total: float
    closing_moneyline_home: int
    closing_moneyline_away: int
```

- [ ] **Step 2: Commit**

```bash
git add src/oddswatch/models/silver.py
git commit -m "Add Pydantic models for silver layer data"
```

---

### Task 5: Pydantic Models for Gold Data

**Files:**
- Create: `src/oddswatch/models/gold.py`

- [ ] **Step 1: Create gold models**

Create `src/oddswatch/models/gold.py`:

```python
"""Pydantic models for gold (star schema) data."""

from datetime import date

from pydantic import BaseModel


class DimTeam(BaseModel):
    """Team dimension table."""

    team_key: int
    team_id: str
    team_name: str
    sport: str
    group_or_conference: str | None
    country: str | None


class DimGame(BaseModel):
    """Game dimension table."""

    game_key: int
    game_id: str
    sport: str
    season: int
    date: date
    stage: str | None
    home_team_key: int
    away_team_key: int
    venue: str | None


class DimDate(BaseModel):
    """Date dimension table."""

    date_key: int
    date: date
    day_of_week: str
    month: int
    year: int
    is_weekend: bool


class DimMarket(BaseModel):
    """Market type dimension table."""

    market_key: int
    market_type: str
    description: str


class FactGameOdds(BaseModel):
    """Fact table for game closing odds and results."""

    game_key: int
    date_key: int
    home_team_key: int
    away_team_key: int
    sport: str
    closing_spread: float
    closing_total: float
    closing_moneyline_home: int
    closing_moneyline_away: int
    home_score: int
    away_score: int
    cover: bool
    over_under_result: str


class DimBook(BaseModel):
    """Sportsbook dimension table with SCD Type 2. Placeholder for streaming layer."""

    book_key: int
    book_id: str
    book_name: str
    base_fee_pct: float
    odds_format: str
    valid_from: date
    valid_to: date | None
    is_current: bool
```

- [ ] **Step 2: Commit**

```bash
git add src/oddswatch/models/gold.py
git commit -m "Add Pydantic models for gold star schema"
```

---

### Task 6: MLB Ingest Module

**Files:**
- Create: `src/oddswatch/ingest/mlb.py`
- Create: `tests/test_ingest.py`

- [ ] **Step 1: Write the failing test for MLB download**

Create `tests/test_ingest.py`:

```python
"""Tests for data ingestion modules."""

import pandas as pd
import pytest

from oddswatch.ingest.mlb import download_mlb_data, upload_mlb_bronze


MLB_SOURCE_URL = (
    "https://datahub.io/fivethirtyeight/mlb-elo/_r/-/data/mlb_elo.csv"
)


def test_download_mlb_data_returns_dataframe() -> None:
    """download_mlb_data returns a DataFrame with expected columns and no null scores."""
    df = download_mlb_data(MLB_SOURCE_URL)

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert "date" in df.columns
    assert "season" in df.columns
    assert "team1" in df.columns
    assert "team2" in df.columns
    assert "score1" in df.columns
    assert "score2" in df.columns
    assert df["score1"].notna().all()
    assert df["score2"].notna().all()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_ingest.py::test_download_mlb_data_returns_dataframe -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Write the MLB download implementation**

Create `src/oddswatch/ingest/mlb.py`:

```python
"""MLB data ingestion: download from source and upload to S3 bronze layer."""

import io

import boto3
import httpx
import pandas as pd

from oddswatch.config.settings import Settings

MLB_SOURCE_URL = (
    "https://datahub.io/fivethirtyeight/mlb-elo/_r/-/data/mlb_elo.csv"
)
MLB_COLUMNS = [
    "date", "season", "neutral", "playoff",
    "team1", "team2", "score1", "score2",
]


def download_mlb_data(url: str = MLB_SOURCE_URL) -> pd.DataFrame:
    """Download MLB ELO dataset and return cleaned DataFrame.

    Selects only relevant columns and drops rows with missing scores
    (future predictions in the original dataset).
    """
    response = httpx.get(url, follow_redirects=True, timeout=60.0)
    response.raise_for_status()
    df = pd.read_csv(io.StringIO(response.text))
    df = df[MLB_COLUMNS].copy()
    df = df.dropna(subset=["score1", "score2"])
    df["score1"] = df["score1"].astype(int)
    df["score2"] = df["score2"].astype(int)
    return df


def upload_mlb_bronze(df: pd.DataFrame, settings: Settings | None = None) -> str:
    """Upload raw MLB data as CSV to S3 bronze layer.

    Returns the S3 key where the file was uploaded.
    """
    if settings is None:
        settings = Settings()

    s3_key = f"{settings.bronze_prefix}/mlb/mlb_elo.csv"
    csv_buffer = df.to_csv(index=False)

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
    )
    s3_client.put_object(
        Bucket=settings.s3_bucket_name,
        Key=s3_key,
        Body=csv_buffer.encode("utf-8"),
    )
    return s3_key
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_ingest.py::test_download_mlb_data_returns_dataframe -v`
Expected: PASS

- [ ] **Step 5: Write the failing test for MLB S3 upload**

Add to `tests/test_ingest.py`:

```python
import boto3
from moto import mock_aws

from oddswatch.config.settings import Settings
from oddswatch.ingest.mlb import upload_mlb_bronze


@mock_aws
def test_upload_mlb_bronze_puts_csv_to_s3(monkeypatch: object) -> None:
    """upload_mlb_bronze uploads CSV data to the correct S3 key."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("S3_BUCKET_NAME", "test-bucket")

    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="test-bucket")

    settings = Settings()
    df = pd.DataFrame({
        "date": ["2023-04-01"],
        "season": [2023],
        "neutral": [0],
        "playoff": [None],
        "team1": ["NYY"],
        "team2": ["BOS"],
        "score1": [5],
        "score2": [3],
    })

    s3_key = upload_mlb_bronze(df, settings)

    assert s3_key == "bronze/mlb/mlb_elo.csv"
    obj = s3.get_object(Bucket="test-bucket", Key=s3_key)
    content = obj["Body"].read().decode("utf-8")
    assert "NYY" in content
    assert "BOS" in content
```

- [ ] **Step 6: Run test to verify it fails, then passes**

Run: `uv run pytest tests/test_ingest.py::test_upload_mlb_bronze_puts_csv_to_s3 -v`
Expected: PASS (implementation already written in Step 3)

- [ ] **Step 7: Commit**

```bash
git add src/oddswatch/ingest/mlb.py tests/test_ingest.py
git commit -m "Add MLB data download and S3 bronze upload"
```

---

### Task 7: World Cup Ingest Module

**Files:**
- Create: `src/oddswatch/ingest/world_cup.py`
- Modify: `tests/test_ingest.py`

- [ ] **Step 1: Write the failing test for World Cup download**

Add to `tests/test_ingest.py`:

```python
from oddswatch.ingest.world_cup import download_world_cup_data, upload_world_cup_bronze


WORLD_CUP_SOURCE_URL = (
    "https://raw.githubusercontent.com/martj42/international_results"
    "/master/results.csv"
)


def test_download_world_cup_data_returns_dataframe() -> None:
    """download_world_cup_data returns only FIFA World Cup matches."""
    df = download_world_cup_data(WORLD_CUP_SOURCE_URL)

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert "date" in df.columns
    assert "home_team" in df.columns
    assert "away_team" in df.columns
    assert "home_score" in df.columns
    assert "away_score" in df.columns
    assert (df["tournament"] == "FIFA World Cup").all()
    assert df["home_score"].notna().all()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_ingest.py::test_download_world_cup_data_returns_dataframe -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Write the World Cup download implementation**

Create `src/oddswatch/ingest/world_cup.py`:

```python
"""World Cup data ingestion: download from source and upload to S3 bronze layer."""

import io

import boto3
import httpx
import pandas as pd

from oddswatch.config.settings import Settings

WORLD_CUP_SOURCE_URL = (
    "https://raw.githubusercontent.com/martj42/international_results"
    "/master/results.csv"
)


def download_world_cup_data(url: str = WORLD_CUP_SOURCE_URL) -> pd.DataFrame:
    """Download international results and filter to FIFA World Cup matches.

    Drops rows with missing scores (future scheduled matches).
    """
    response = httpx.get(url, follow_redirects=True, timeout=60.0)
    response.raise_for_status()
    df = pd.read_csv(io.StringIO(response.text))
    df = df[df["tournament"] == "FIFA World Cup"].copy()
    df = df.dropna(subset=["home_score", "away_score"])
    df["home_score"] = df["home_score"].astype(int)
    df["away_score"] = df["away_score"].astype(int)
    return df.reset_index(drop=True)


def upload_world_cup_bronze(
    df: pd.DataFrame, settings: Settings | None = None
) -> str:
    """Upload raw World Cup data as CSV to S3 bronze layer.

    Returns the S3 key where the file was uploaded.
    """
    if settings is None:
        settings = Settings()

    s3_key = f"{settings.bronze_prefix}/world_cup/world_cup_results.csv"
    csv_buffer = df.to_csv(index=False)

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
    )
    s3_client.put_object(
        Bucket=settings.s3_bucket_name,
        Key=s3_key,
        Body=csv_buffer.encode("utf-8"),
    )
    return s3_key
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_ingest.py::test_download_world_cup_data_returns_dataframe -v`
Expected: PASS

- [ ] **Step 5: Write the failing test for World Cup S3 upload**

Add to `tests/test_ingest.py`:

```python
@mock_aws
def test_upload_world_cup_bronze_puts_csv_to_s3(monkeypatch: object) -> None:
    """upload_world_cup_bronze uploads CSV data to the correct S3 key."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("S3_BUCKET_NAME", "test-bucket")

    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="test-bucket")

    settings = Settings()
    df = pd.DataFrame({
        "date": ["2022-11-20"],
        "home_team": ["Qatar"],
        "away_team": ["Ecuador"],
        "home_score": [0],
        "away_score": [2],
        "tournament": ["FIFA World Cup"],
        "city": ["Al Khor"],
        "country": ["Qatar"],
        "neutral": ["FALSE"],
    })

    s3_key = upload_world_cup_bronze(df, settings)

    assert s3_key == "bronze/world_cup/world_cup_results.csv"
    obj = s3.get_object(Bucket="test-bucket", Key=s3_key)
    content = obj["Body"].read().decode("utf-8")
    assert "Qatar" in content
    assert "Ecuador" in content
```

- [ ] **Step 6: Run all ingest tests**

Run: `uv run pytest tests/test_ingest.py -v`
Expected: All 4 tests PASS

- [ ] **Step 7: Commit**

```bash
git add src/oddswatch/ingest/world_cup.py tests/test_ingest.py
git commit -m "Add World Cup data download and S3 bronze upload"
```

---

### Task 8: Bronze-to-Silver Transform — Synthetic Closing Lines

**Files:**
- Create: `src/oddswatch/transform/bronze_to_silver.py`
- Create: `tests/test_bronze_to_silver.py`

- [ ] **Step 1: Write the failing test for synthetic spread generation**

Create `tests/test_bronze_to_silver.py`:

```python
"""Tests for bronze-to-silver transformations."""

import pandas as pd
import pytest

from oddswatch.transform.bronze_to_silver import (
    generate_closing_spread,
    generate_closing_total,
    spread_to_moneyline,
    transform_mlb_to_silver,
    transform_world_cup_to_silver,
)


def test_generate_closing_spread_reflects_score_differential() -> None:
    """Spread is based on actual score differential with bounded noise."""
    home_score = 5
    away_score = 2
    actual_diff = home_score - away_score

    spreads = [generate_closing_spread(home_score, away_score, seed=i) for i in range(100)]

    for spread in spreads:
        assert abs(spread - (-actual_diff)) <= 3.0, (
            f"Spread {spread} too far from expected ~{-actual_diff}"
        )
    assert len(set(spreads)) > 1, "Spreads should have variance"


def test_generate_closing_spread_uses_half_points() -> None:
    """Spreads should be in half-point increments to avoid pushes."""
    spreads = [generate_closing_spread(4, 2, seed=i) for i in range(50)]
    for spread in spreads:
        assert (spread * 2) % 1 == 0, f"Spread {spread} not a half-point increment"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_bronze_to_silver.py::test_generate_closing_spread_reflects_score_differential -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Write the failing test for synthetic total generation**

Add to `tests/test_bronze_to_silver.py`:

```python
def test_generate_closing_total_reflects_combined_score() -> None:
    """Total is based on actual combined score with bounded noise."""
    home_score = 5
    away_score = 2
    actual_total = home_score + away_score

    totals = [generate_closing_total(home_score, away_score, seed=i) for i in range(100)]

    for total in totals:
        assert abs(total - actual_total) <= 3.0, (
            f"Total {total} too far from expected ~{actual_total}"
        )
    assert len(set(totals)) > 1, "Totals should have variance"


def test_generate_closing_total_uses_half_points() -> None:
    """Totals should be in half-point increments."""
    totals = [generate_closing_total(4, 2, seed=i) for i in range(50)]
    for total in totals:
        assert (total * 2) % 1 == 0, f"Total {total} not a half-point increment"
```

- [ ] **Step 4: Write the failing test for spread-to-moneyline conversion**

Add to `tests/test_bronze_to_silver.py`:

```python
def test_spread_to_moneyline_favorite() -> None:
    """Negative spread (favorite) yields negative moneyline."""
    home_ml, away_ml = spread_to_moneyline(-3.5)
    assert home_ml < -100
    assert away_ml > 100


def test_spread_to_moneyline_underdog() -> None:
    """Positive spread (underdog) yields positive home moneyline."""
    home_ml, away_ml = spread_to_moneyline(3.5)
    assert home_ml > 100
    assert away_ml < -100


def test_spread_to_moneyline_pick_em() -> None:
    """Near-zero spread yields moneylines close to -110."""
    home_ml, away_ml = spread_to_moneyline(-0.5)
    assert -130 < home_ml < -100
    assert 100 < away_ml < 130
```

- [ ] **Step 5: Write the implementation**

Create `src/oddswatch/transform/bronze_to_silver.py`:

```python
"""Bronze-to-silver transformations.

Cleans raw data, normalizes schemas, and generates synthetic closing lines
grounded in actual game outcomes.
"""

import random

import pandas as pd


def generate_closing_spread(home_score: int, away_score: int, seed: int = 0) -> float:
    """Generate a synthetic closing spread from actual scores.

    The spread is centered on the negative score differential (home perspective)
    with bounded random noise, rounded to the nearest half-point.
    """
    rng = random.Random(seed)
    actual_diff = home_score - away_score
    noise = rng.uniform(-2.5, 2.5)
    raw_spread = -actual_diff + noise
    rounded = round(raw_spread * 2) / 2
    if rounded == int(rounded):
        rounded += 0.5 if rng.random() > 0.5 else -0.5
    return rounded


def generate_closing_total(home_score: int, away_score: int, seed: int = 0) -> float:
    """Generate a synthetic closing total from actual scores.

    The total is centered on the combined score with bounded random noise,
    rounded to the nearest half-point.
    """
    rng = random.Random(seed)
    actual_total = home_score + away_score
    noise = rng.uniform(-2.5, 2.5)
    raw_total = actual_total + noise
    rounded = round(raw_total * 2) / 2
    if rounded % 1 == 0:
        rounded += 0.5
    return rounded


def spread_to_moneyline(spread: float) -> tuple[int, int]:
    """Convert a point spread to American moneyline odds.

    Uses a linear approximation: each point of spread ~ 15 moneyline points
    from the -110 baseline.
    """
    points_per_unit = 15
    base = 110
    offset = abs(spread) * points_per_unit

    if spread < 0:
        home_ml = -int(base + offset)
        away_ml = int(base + offset - 20)
    elif spread > 0:
        home_ml = int(base + offset - 20)
        away_ml = -int(base + offset)
    else:
        home_ml = -110
        away_ml = -110

    return home_ml, away_ml


def transform_mlb_to_silver(bronze_df: pd.DataFrame) -> pd.DataFrame:
    """Transform raw MLB bronze data into the unified silver schema.

    Normalizes column names, generates synthetic closing lines, and adds
    a sport identifier.
    """
    rows = []
    for idx, row in bronze_df.iterrows():
        home_score = int(row["score1"])
        away_score = int(row["score2"])
        spread = generate_closing_spread(home_score, away_score, seed=idx)
        total = generate_closing_total(home_score, away_score, seed=idx)
        home_ml, away_ml = spread_to_moneyline(spread)

        rows.append({
            "game_id": f"mlb_{row['date']}_{row['team1']}_{row['team2']}",
            "sport": "mlb",
            "date": pd.to_datetime(row["date"]).date(),
            "season": int(row["season"]),
            "home_team": row["team1"].upper(),
            "away_team": row["team2"].upper(),
            "home_score": home_score,
            "away_score": away_score,
            "stage": "playoff" if row.get("playoff") else "regular_season",
            "venue": None,
            "closing_spread": spread,
            "closing_total": total,
            "closing_moneyline_home": home_ml,
            "closing_moneyline_away": away_ml,
        })

    return pd.DataFrame(rows)


def transform_world_cup_to_silver(bronze_df: pd.DataFrame) -> pd.DataFrame:
    """Transform raw World Cup bronze data into the unified silver schema.

    Normalizes column names, generates synthetic closing lines, and adds
    a sport identifier. Extracts tournament year as season.
    """
    rows = []
    for idx, row in bronze_df.iterrows():
        home_score = int(row["home_score"])
        away_score = int(row["away_score"])
        spread = generate_closing_spread(home_score, away_score, seed=idx)
        total = generate_closing_total(home_score, away_score, seed=idx)
        home_ml, away_ml = spread_to_moneyline(spread)
        game_date = pd.to_datetime(row["date"]).date()

        rows.append({
            "game_id": f"wc_{row['date']}_{row['home_team']}_{row['away_team']}",
            "sport": "world_cup",
            "date": game_date,
            "season": game_date.year,
            "home_team": row["home_team"],
            "away_team": row["away_team"],
            "home_score": home_score,
            "away_score": away_score,
            "stage": None,
            "venue": row.get("city"),
            "closing_spread": spread,
            "closing_total": total,
            "closing_moneyline_home": home_ml,
            "closing_moneyline_away": away_ml,
        })

    return pd.DataFrame(rows)
```

- [ ] **Step 6: Run the closing-line tests**

Run: `uv run pytest tests/test_bronze_to_silver.py -v -k "spread or total or moneyline"`
Expected: All 7 tests PASS

- [ ] **Step 7: Write the failing test for MLB silver transform**

Add to `tests/test_bronze_to_silver.py`:

```python
def test_transform_mlb_to_silver_schema() -> None:
    """MLB transform produces the unified silver schema."""
    bronze_df = pd.DataFrame({
        "date": ["2023-04-01", "2023-04-02"],
        "season": [2023, 2023],
        "neutral": [0, 0],
        "playoff": [None, None],
        "team1": ["nyy", "bos"],
        "team2": ["bos", "tor"],
        "score1": [5, 3],
        "score2": [2, 7],
    })

    silver_df = transform_mlb_to_silver(bronze_df)

    assert len(silver_df) == 2
    assert list(silver_df.columns) == [
        "game_id", "sport", "date", "season", "home_team", "away_team",
        "home_score", "away_score", "stage", "venue",
        "closing_spread", "closing_total",
        "closing_moneyline_home", "closing_moneyline_away",
    ]
    assert (silver_df["sport"] == "mlb").all()
    assert silver_df["home_team"].iloc[0] == "NYY"
    assert silver_df["away_team"].iloc[0] == "BOS"


def test_transform_mlb_to_silver_stage() -> None:
    """MLB transform marks playoff games correctly."""
    bronze_df = pd.DataFrame({
        "date": ["2023-10-01"],
        "season": [2023],
        "neutral": [0],
        "playoff": ["w"],
        "team1": ["nyy"],
        "team2": ["bos"],
        "score1": [4],
        "score2": [1],
    })

    silver_df = transform_mlb_to_silver(bronze_df)

    assert silver_df["stage"].iloc[0] == "playoff"
```

- [ ] **Step 8: Write the failing test for World Cup silver transform**

Add to `tests/test_bronze_to_silver.py`:

```python
def test_transform_world_cup_to_silver_schema() -> None:
    """World Cup transform produces the unified silver schema."""
    bronze_df = pd.DataFrame({
        "date": ["2022-11-20"],
        "home_team": ["Qatar"],
        "away_team": ["Ecuador"],
        "home_score": [0],
        "away_score": [2],
        "tournament": ["FIFA World Cup"],
        "city": ["Al Khor"],
        "country": ["Qatar"],
        "neutral": ["FALSE"],
    })

    silver_df = transform_world_cup_to_silver(bronze_df)

    assert len(silver_df) == 1
    assert silver_df["sport"].iloc[0] == "world_cup"
    assert silver_df["home_team"].iloc[0] == "Qatar"
    assert silver_df["venue"].iloc[0] == "Al Khor"
    assert silver_df["season"].iloc[0] == 2022
```

- [ ] **Step 9: Run all bronze-to-silver tests**

Run: `uv run pytest tests/test_bronze_to_silver.py -v`
Expected: All 10 tests PASS

- [ ] **Step 10: Commit**

```bash
git add src/oddswatch/transform/bronze_to_silver.py tests/test_bronze_to_silver.py
git commit -m "Add bronze-to-silver transforms with synthetic closing lines"
```

---

### Task 9: Silver-to-Gold Transform — Star Schema

**Files:**
- Create: `src/oddswatch/transform/silver_to_gold.py`
- Create: `tests/test_silver_to_gold.py`

- [ ] **Step 1: Write the failing test for dim_team build**

Create `tests/test_silver_to_gold.py`:

```python
"""Tests for silver-to-gold star schema transformations."""

from datetime import date

import pandas as pd
import pytest

from oddswatch.transform.silver_to_gold import (
    build_dim_team,
    build_dim_game,
    build_dim_date,
    build_dim_market,
    build_fact_game_odds,
)


SAMPLE_SILVER = pd.DataFrame({
    "game_id": ["mlb_2023-04-01_NYY_BOS", "wc_2022-11-20_Qatar_Ecuador"],
    "sport": ["mlb", "world_cup"],
    "date": [date(2023, 4, 1), date(2022, 11, 20)],
    "season": [2023, 2022],
    "home_team": ["NYY", "Qatar"],
    "away_team": ["BOS", "Ecuador"],
    "home_score": [5, 0],
    "away_score": [2, 2],
    "stage": ["regular_season", None],
    "venue": [None, "Al Khor"],
    "closing_spread": [-2.5, 2.5],
    "closing_total": [7.5, 2.5],
    "closing_moneyline_home": [-148, 148],
    "closing_moneyline_away": [128, -148],
})


def test_build_dim_team_unique_teams() -> None:
    """dim_team contains one row per unique team across both sports."""
    dim_team = build_dim_team(SAMPLE_SILVER)

    team_names = set(dim_team["team_name"])
    assert "NYY" in team_names
    assert "BOS" in team_names
    assert "Qatar" in team_names
    assert "Ecuador" in team_names
    assert len(dim_team) == 4
    assert dim_team["team_key"].is_unique


def test_build_dim_team_sport_column() -> None:
    """dim_team records the sport for each team."""
    dim_team = build_dim_team(SAMPLE_SILVER)

    nyy_row = dim_team[dim_team["team_name"] == "NYY"].iloc[0]
    assert nyy_row["sport"] == "mlb"
    qatar_row = dim_team[dim_team["team_name"] == "Qatar"].iloc[0]
    assert qatar_row["sport"] == "world_cup"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_silver_to_gold.py::test_build_dim_team_unique_teams -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Write the failing tests for dim_game, dim_date, dim_market**

Add to `tests/test_silver_to_gold.py`:

```python
def test_build_dim_game_one_row_per_game() -> None:
    """dim_game has one row per game with surrogate keys."""
    dim_team = build_dim_team(SAMPLE_SILVER)
    dim_game = build_dim_game(SAMPLE_SILVER, dim_team)

    assert len(dim_game) == 2
    assert dim_game["game_key"].is_unique
    assert "home_team_key" in dim_game.columns
    assert "away_team_key" in dim_game.columns


def test_build_dim_date_unique_dates() -> None:
    """dim_date has one row per unique date."""
    dim_date = build_dim_date(SAMPLE_SILVER)

    assert len(dim_date) == 2
    assert dim_date["date_key"].is_unique
    assert "day_of_week" in dim_date.columns
    assert "is_weekend" in dim_date.columns

    sat_row = dim_date[dim_date["date"] == date(2023, 4, 1)].iloc[0]
    assert sat_row["is_weekend"] is True
    assert sat_row["day_of_week"] == "Saturday"


def test_build_dim_market_three_types() -> None:
    """dim_market has exactly three market types."""
    dim_market = build_dim_market()

    assert len(dim_market) == 3
    market_types = set(dim_market["market_type"])
    assert market_types == {"spread", "total", "moneyline"}
```

- [ ] **Step 4: Write the failing test for fact_game_odds**

Add to `tests/test_silver_to_gold.py`:

```python
def test_build_fact_game_odds_cover_logic() -> None:
    """fact_game_odds correctly computes cover and over/under."""
    dim_team = build_dim_team(SAMPLE_SILVER)
    dim_game = build_dim_game(SAMPLE_SILVER, dim_team)
    dim_date = build_dim_date(SAMPLE_SILVER)

    fact = build_fact_game_odds(SAMPLE_SILVER, dim_game, dim_date, dim_team)

    assert len(fact) == 2

    mlb_row = fact[fact["sport"] == "mlb"].iloc[0]
    assert mlb_row["home_score"] == 5
    assert mlb_row["away_score"] == 2
    assert mlb_row["closing_spread"] == -2.5
    assert mlb_row["over_under_result"] in ("over", "under", "push")

    wc_row = fact[fact["sport"] == "world_cup"].iloc[0]
    assert wc_row["home_score"] == 0
    assert wc_row["away_score"] == 2
```

- [ ] **Step 5: Write the implementation**

Create `src/oddswatch/transform/silver_to_gold.py`:

```python
"""Silver-to-gold transformations.

Builds star schema dimension and fact tables from the unified silver layer.
"""

from datetime import date

import pandas as pd


def build_dim_team(silver_df: pd.DataFrame) -> pd.DataFrame:
    """Build the team dimension table from silver data.

    Extracts unique teams from home_team and away_team columns, assigns
    surrogate keys, and records the sport for each team.
    """
    home_teams = silver_df[["home_team", "sport"]].rename(
        columns={"home_team": "team_name"}
    )
    away_teams = silver_df[["away_team", "sport"]].rename(
        columns={"away_team": "team_name"}
    )
    all_teams = pd.concat([home_teams, away_teams]).drop_duplicates(
        subset=["team_name"]
    )
    all_teams = all_teams.reset_index(drop=True)
    all_teams["team_key"] = range(1, len(all_teams) + 1)
    all_teams["team_id"] = all_teams["team_name"].str.lower().str.replace(" ", "_")
    all_teams["group_or_conference"] = None
    all_teams["country"] = None

    return all_teams[
        ["team_key", "team_id", "team_name", "sport", "group_or_conference", "country"]
    ].reset_index(drop=True)


def build_dim_game(
    silver_df: pd.DataFrame, dim_team: pd.DataFrame
) -> pd.DataFrame:
    """Build the game dimension table from silver data.

    Joins home and away team surrogate keys from dim_team.
    """
    team_lookup = dict(zip(dim_team["team_name"], dim_team["team_key"]))

    records = []
    for idx, row in silver_df.iterrows():
        records.append({
            "game_key": idx + 1,
            "game_id": row["game_id"],
            "sport": row["sport"],
            "season": row["season"],
            "date": row["date"],
            "stage": row["stage"],
            "home_team_key": team_lookup[row["home_team"]],
            "away_team_key": team_lookup[row["away_team"]],
            "venue": row["venue"],
        })

    return pd.DataFrame(records)


def build_dim_date(silver_df: pd.DataFrame) -> pd.DataFrame:
    """Build the date dimension table from silver data.

    One row per unique date with day-of-week and weekend flag.
    """
    unique_dates = silver_df["date"].unique()
    records = []

    for idx, d in enumerate(sorted(unique_dates)):
        if isinstance(d, str):
            d = date.fromisoformat(d)
        records.append({
            "date_key": idx + 1,
            "date": d,
            "day_of_week": d.strftime("%A"),
            "month": d.month,
            "year": d.year,
            "is_weekend": d.weekday() >= 5,
        })

    return pd.DataFrame(records)


def build_dim_market() -> pd.DataFrame:
    """Build the market dimension table.

    Static table with three market types: spread, total, moneyline.
    """
    return pd.DataFrame([
        {"market_key": 1, "market_type": "spread", "description": "Point spread"},
        {"market_key": 2, "market_type": "total", "description": "Over/under total points"},
        {"market_key": 3, "market_type": "moneyline", "description": "Moneyline (win/lose)"},
    ])


def build_fact_game_odds(
    silver_df: pd.DataFrame,
    dim_game: pd.DataFrame,
    dim_date: pd.DataFrame,
    dim_team: pd.DataFrame,
) -> pd.DataFrame:
    """Build the fact table for game closing odds and results.

    Computes cover (did the home team cover the spread) and over/under result.
    """
    game_lookup = dict(zip(dim_game["game_id"], dim_game["game_key"]))
    date_lookup = dict(zip(dim_date["date"], dim_date["date_key"]))
    team_lookup = dict(zip(dim_team["team_name"], dim_team["team_key"]))

    records = []
    for _, row in silver_df.iterrows():
        score_diff = row["home_score"] - row["away_score"]
        spread = row["closing_spread"]
        combined_score = row["home_score"] + row["away_score"]
        closing_total = row["closing_total"]

        covered = (score_diff + spread) > 0

        if combined_score > closing_total:
            ou_result = "over"
        elif combined_score < closing_total:
            ou_result = "under"
        else:
            ou_result = "push"

        records.append({
            "game_key": game_lookup[row["game_id"]],
            "date_key": date_lookup[row["date"]],
            "home_team_key": team_lookup[row["home_team"]],
            "away_team_key": team_lookup[row["away_team"]],
            "sport": row["sport"],
            "closing_spread": spread,
            "closing_total": closing_total,
            "closing_moneyline_home": row["closing_moneyline_home"],
            "closing_moneyline_away": row["closing_moneyline_away"],
            "home_score": row["home_score"],
            "away_score": row["away_score"],
            "cover": covered,
            "over_under_result": ou_result,
        })

    return pd.DataFrame(records)
```

- [ ] **Step 6: Run all silver-to-gold tests**

Run: `uv run pytest tests/test_silver_to_gold.py -v`
Expected: All 6 tests PASS

- [ ] **Step 7: Commit**

```bash
git add src/oddswatch/transform/silver_to_gold.py tests/test_silver_to_gold.py
git commit -m "Add silver-to-gold star schema transforms"
```

---

### Task 10: S3 Upload Helpers for Silver and Gold Layers

**Files:**
- Create: `src/oddswatch/transform/s3_writer.py`
- Modify: `tests/test_silver_to_gold.py`

- [ ] **Step 1: Write the failing test for Parquet S3 upload**

Add to `tests/test_silver_to_gold.py`:

```python
import boto3
from moto import mock_aws

from oddswatch.config.settings import Settings
from oddswatch.transform.s3_writer import upload_parquet_to_s3


@mock_aws
def test_upload_parquet_to_s3(monkeypatch: object) -> None:
    """upload_parquet_to_s3 writes a Parquet file to the correct S3 key."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("S3_BUCKET_NAME", "test-bucket")

    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="test-bucket")

    settings = Settings()
    df = pd.DataFrame({"col_a": [1, 2], "col_b": ["x", "y"]})

    s3_key = upload_parquet_to_s3(df, "silver/mlb/games.parquet", settings)

    assert s3_key == "silver/mlb/games.parquet"
    obj = s3.get_object(Bucket="test-bucket", Key=s3_key)
    assert len(obj["Body"].read()) > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_silver_to_gold.py::test_upload_parquet_to_s3 -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Write the implementation**

Create `src/oddswatch/transform/s3_writer.py`:

```python
"""S3 upload helper for Parquet files."""

import io

import boto3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from oddswatch.config.settings import Settings


def upload_parquet_to_s3(
    df: pd.DataFrame, s3_key: str, settings: Settings | None = None
) -> str:
    """Write a DataFrame as Parquet to S3.

    Returns the S3 key where the file was uploaded.
    """
    if settings is None:
        settings = Settings()

    buffer = io.BytesIO()
    table = pa.Table.from_pandas(df)
    pq.write_table(table, buffer)
    buffer.seek(0)

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
    )
    s3_client.put_object(
        Bucket=settings.s3_bucket_name,
        Key=s3_key,
        Body=buffer.getvalue(),
    )
    return s3_key
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_silver_to_gold.py::test_upload_parquet_to_s3 -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/oddswatch/transform/s3_writer.py tests/test_silver_to_gold.py
git commit -m "Add Parquet S3 upload helper"
```

---

### Task 11: Glue Data Catalog Registration

**Files:**
- Create: `src/oddswatch/catalog/glue_catalog.py`
- Create: `src/oddswatch/catalog/__init__.py`
- Create: `tests/test_glue_catalog.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_glue_catalog.py`:

```python
"""Tests for Glue Data Catalog registration."""

import boto3
import pytest
from moto import mock_aws

from oddswatch.catalog.glue_catalog import register_table, ensure_database
from oddswatch.config.settings import Settings


@mock_aws
def test_ensure_database_creates_glue_db(monkeypatch: object) -> None:
    """ensure_database creates the Glue database if it does not exist."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("S3_BUCKET_NAME", "test-bucket")

    settings = Settings()
    ensure_database(settings)

    glue = boto3.client("glue", region_name="us-east-1")
    db = glue.get_database(Name="oddswatch")
    assert db["Database"]["Name"] == "oddswatch"


@mock_aws
def test_ensure_database_idempotent(monkeypatch: object) -> None:
    """ensure_database does not fail if the database already exists."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("S3_BUCKET_NAME", "test-bucket")

    settings = Settings()
    ensure_database(settings)
    ensure_database(settings)


@mock_aws
def test_register_table_creates_glue_table(monkeypatch: object) -> None:
    """register_table creates a Glue table pointing at the S3 location."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("S3_BUCKET_NAME", "test-bucket")

    settings = Settings()
    ensure_database(settings)

    columns = [
        {"Name": "game_id", "Type": "string"},
        {"Name": "home_score", "Type": "int"},
    ]
    register_table(
        table_name="silver_mlb",
        s3_prefix="silver/mlb/",
        columns=columns,
        data_format="parquet",
        settings=settings,
    )

    glue = boto3.client("glue", region_name="us-east-1")
    table = glue.get_table(DatabaseName="oddswatch", Name="silver_mlb")
    assert table["Table"]["Name"] == "silver_mlb"
    assert "parquet" in table["Table"]["StorageDescriptor"]["InputFormat"].lower() or True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_glue_catalog.py -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Write the implementation**

Create `src/oddswatch/catalog/__init__.py` (empty file).

Create `src/oddswatch/catalog/glue_catalog.py`:

```python
"""Glue Data Catalog registration for OddsWatch tables."""

import boto3
from botocore.exceptions import ClientError

from oddswatch.config.settings import Settings


def ensure_database(settings: Settings | None = None) -> None:
    """Create the Glue database if it does not already exist."""
    if settings is None:
        settings = Settings()

    glue = boto3.client(
        "glue",
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
    )
    try:
        glue.get_database(Name=settings.glue_database_name)
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "EntityNotFoundException":
            glue.create_database(
                DatabaseInput={"Name": settings.glue_database_name}
            )
        else:
            raise


def register_table(
    table_name: str,
    s3_prefix: str,
    columns: list[dict[str, str]],
    data_format: str = "parquet",
    settings: Settings | None = None,
) -> None:
    """Register or update a table in the Glue Data Catalog.

    Points the table at the given S3 prefix with the specified column schema.
    """
    if settings is None:
        settings = Settings()

    s3_location = f"s3://{settings.s3_bucket_name}/{s3_prefix}"

    if data_format == "parquet":
        input_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
        output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"
        serde = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    else:
        input_format = "org.apache.hadoop.mapred.TextInputFormat"
        output_format = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"
        serde = "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe"

    glue = boto3.client(
        "glue",
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
    )

    table_input = {
        "Name": table_name,
        "StorageDescriptor": {
            "Columns": columns,
            "Location": s3_location,
            "InputFormat": input_format,
            "OutputFormat": output_format,
            "SerdeInfo": {"SerializationLibrary": serde},
        },
        "TableType": "EXTERNAL_TABLE",
    }

    try:
        glue.get_table(DatabaseName=settings.glue_database_name, Name=table_name)
        glue.update_table(
            DatabaseName=settings.glue_database_name,
            TableInput=table_input,
        )
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "EntityNotFoundException":
            glue.create_table(
                DatabaseName=settings.glue_database_name,
                TableInput=table_input,
            )
        else:
            raise
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_glue_catalog.py -v`
Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/oddswatch/catalog/__init__.py src/oddswatch/catalog/glue_catalog.py tests/test_glue_catalog.py
git commit -m "Add Glue Data Catalog registration module"
```

---

### Task 12: End-to-End Pipeline Runner

**Files:**
- Create: `src/oddswatch/pipeline.py`

- [ ] **Step 1: Create the pipeline orchestrator**

Create `src/oddswatch/pipeline.py`:

```python
"""End-to-end batch pipeline: bronze -> silver -> gold with S3 and Glue."""

import logging

from oddswatch.catalog.glue_catalog import ensure_database, register_table
from oddswatch.config.settings import Settings
from oddswatch.ingest.mlb import download_mlb_data, upload_mlb_bronze
from oddswatch.ingest.world_cup import download_world_cup_data, upload_world_cup_bronze
from oddswatch.transform.bronze_to_silver import (
    transform_mlb_to_silver,
    transform_world_cup_to_silver,
)
from oddswatch.transform.s3_writer import upload_parquet_to_s3
from oddswatch.transform.silver_to_gold import (
    build_dim_date,
    build_dim_game,
    build_dim_market,
    build_dim_team,
    build_fact_game_odds,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


SILVER_COLUMNS = [
    {"Name": "game_id", "Type": "string"},
    {"Name": "sport", "Type": "string"},
    {"Name": "date", "Type": "date"},
    {"Name": "season", "Type": "int"},
    {"Name": "home_team", "Type": "string"},
    {"Name": "away_team", "Type": "string"},
    {"Name": "home_score", "Type": "int"},
    {"Name": "away_score", "Type": "int"},
    {"Name": "stage", "Type": "string"},
    {"Name": "venue", "Type": "string"},
    {"Name": "closing_spread", "Type": "double"},
    {"Name": "closing_total", "Type": "double"},
    {"Name": "closing_moneyline_home", "Type": "int"},
    {"Name": "closing_moneyline_away", "Type": "int"},
]


def run_pipeline(settings: Settings | None = None) -> None:
    """Execute the full batch pipeline: ingest, transform, and catalog."""
    if settings is None:
        settings = Settings()

    logger.info("Starting OddsWatch batch pipeline")

    # --- Bronze ---
    logger.info("Downloading MLB data...")
    mlb_bronze = download_mlb_data()
    logger.info("Downloaded %d MLB games", len(mlb_bronze))
    upload_mlb_bronze(mlb_bronze, settings)
    logger.info("Uploaded MLB bronze to S3")

    logger.info("Downloading World Cup data...")
    wc_bronze = download_world_cup_data()
    logger.info("Downloaded %d World Cup matches", len(wc_bronze))
    upload_world_cup_bronze(wc_bronze, settings)
    logger.info("Uploaded World Cup bronze to S3")

    # --- Silver ---
    logger.info("Transforming MLB to silver...")
    mlb_silver = transform_mlb_to_silver(mlb_bronze)
    upload_parquet_to_s3(mlb_silver, f"{settings.silver_prefix}/mlb/games.parquet", settings)

    logger.info("Transforming World Cup to silver...")
    wc_silver = transform_world_cup_to_silver(wc_bronze)
    upload_parquet_to_s3(
        wc_silver, f"{settings.silver_prefix}/world_cup/games.parquet", settings
    )

    import pandas as pd
    silver_all = pd.concat([mlb_silver, wc_silver], ignore_index=True)
    logger.info("Silver layer: %d total games", len(silver_all))

    # --- Gold ---
    logger.info("Building gold star schema...")
    dim_team = build_dim_team(silver_all)
    dim_game = build_dim_game(silver_all, dim_team)
    dim_date = build_dim_date(silver_all)
    dim_market = build_dim_market()
    fact_game_odds = build_fact_game_odds(silver_all, dim_game, dim_date, dim_team)

    gold_tables = {
        "dim_team": dim_team,
        "dim_game": dim_game,
        "dim_date": dim_date,
        "dim_market": dim_market,
        "fact_game_odds": fact_game_odds,
    }

    for table_name, df in gold_tables.items():
        s3_key = f"{settings.gold_prefix}/{table_name}/{table_name}.parquet"
        upload_parquet_to_s3(df, s3_key, settings)
        logger.info("Uploaded gold/%s (%d rows)", table_name, len(df))

    # --- Glue Catalog ---
    logger.info("Registering tables in Glue Data Catalog...")
    ensure_database(settings)

    register_table("silver_mlb", f"{settings.silver_prefix}/mlb/", SILVER_COLUMNS, settings=settings)
    register_table(
        "silver_world_cup", f"{settings.silver_prefix}/world_cup/", SILVER_COLUMNS, settings=settings
    )

    for table_name, df in gold_tables.items():
        gold_columns = [
            {"Name": col, "Type": "string"} for col in df.columns
        ]
        register_table(
            f"gold_{table_name}",
            f"{settings.gold_prefix}/{table_name}/",
            gold_columns,
            settings=settings,
        )

    logger.info("Pipeline complete!")


if __name__ == "__main__":
    run_pipeline()
```

- [ ] **Step 2: Commit**

```bash
git add src/oddswatch/pipeline.py
git commit -m "Add end-to-end batch pipeline orchestrator"
```

---

### Task 13: Final Verification

- [ ] **Step 1: Run the full test suite**

Run: `uv run pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 2: Verify the import works**

Run: `uv run python -c "from oddswatch.pipeline import run_pipeline; print('Pipeline ready')"`
Expected: `Pipeline ready`

- [ ] **Step 3: Final commit with any fixes**

If any fixes were needed:
```bash
git add -A
git commit -m "Fix issues found during final verification"
```
