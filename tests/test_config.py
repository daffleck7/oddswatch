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
