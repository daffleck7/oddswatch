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
