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
