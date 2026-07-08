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
