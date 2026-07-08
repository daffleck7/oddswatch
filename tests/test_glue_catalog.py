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
