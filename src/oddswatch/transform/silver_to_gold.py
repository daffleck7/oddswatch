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
            "is_weekend": bool(d.weekday() >= 5),
        })

    dim_date = pd.DataFrame(records)
    dim_date["is_weekend"] = dim_date["is_weekend"].astype(object)
    return dim_date


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
