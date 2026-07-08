"""End-to-end batch pipeline: bronze -> silver -> gold with S3 and Glue."""

import logging

import pandas as pd

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
