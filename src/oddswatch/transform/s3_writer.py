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
