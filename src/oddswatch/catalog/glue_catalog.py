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
