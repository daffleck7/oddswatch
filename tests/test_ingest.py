"""Tests for data ingestion modules."""

import pandas as pd
import pytest

from oddswatch.ingest.mlb import download_mlb_data, upload_mlb_bronze
from oddswatch.ingest.world_cup import download_world_cup_data, upload_world_cup_bronze


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
