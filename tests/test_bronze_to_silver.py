"""Tests for bronze-to-silver transformations."""

import pandas as pd
import pytest

from oddswatch.transform.bronze_to_silver import (
    generate_closing_spread,
    generate_closing_total,
    spread_to_moneyline,
    transform_mlb_to_silver,
    transform_world_cup_to_silver,
)


def test_generate_closing_spread_reflects_score_differential() -> None:
    """Spread is based on actual score differential with bounded noise."""
    home_score = 5
    away_score = 2
    actual_diff = home_score - away_score

    spreads = [generate_closing_spread(home_score, away_score, seed=i) for i in range(100)]

    for spread in spreads:
        assert abs(spread - (-actual_diff)) <= 3.0, (
            f"Spread {spread} too far from expected ~{-actual_diff}"
        )
    assert len(set(spreads)) > 1, "Spreads should have variance"


def test_generate_closing_spread_uses_half_points() -> None:
    """Spreads should be in half-point increments to avoid pushes."""
    spreads = [generate_closing_spread(4, 2, seed=i) for i in range(50)]
    for spread in spreads:
        assert (spread * 2) % 1 == 0, f"Spread {spread} not a half-point increment"


def test_generate_closing_total_reflects_combined_score() -> None:
    """Total is based on actual combined score with bounded noise."""
    home_score = 5
    away_score = 2
    actual_total = home_score + away_score

    totals = [generate_closing_total(home_score, away_score, seed=i) for i in range(100)]

    for total in totals:
        assert abs(total - actual_total) <= 3.0, (
            f"Total {total} too far from expected ~{actual_total}"
        )
    assert len(set(totals)) > 1, "Totals should have variance"


def test_generate_closing_total_uses_half_points() -> None:
    """Totals should be in half-point increments."""
    totals = [generate_closing_total(4, 2, seed=i) for i in range(50)]
    for total in totals:
        assert (total * 2) % 1 == 0, f"Total {total} not a half-point increment"


def test_spread_to_moneyline_favorite() -> None:
    """Negative spread (favorite) yields negative moneyline."""
    home_ml, away_ml = spread_to_moneyline(-3.5)
    assert home_ml < -100
    assert away_ml > 100


def test_spread_to_moneyline_underdog() -> None:
    """Positive spread (underdog) yields positive home moneyline."""
    home_ml, away_ml = spread_to_moneyline(3.5)
    assert home_ml > 100
    assert away_ml < -100


def test_spread_to_moneyline_pick_em() -> None:
    """Near-zero spread yields moneylines close to -110."""
    home_ml, away_ml = spread_to_moneyline(-0.5)
    assert -130 < home_ml < -100
    assert 100 < away_ml < 130


def test_transform_mlb_to_silver_schema() -> None:
    """MLB transform produces the unified silver schema."""
    bronze_df = pd.DataFrame({
        "date": ["2023-04-01", "2023-04-02"],
        "season": [2023, 2023],
        "neutral": [0, 0],
        "playoff": [None, None],
        "team1": ["nyy", "bos"],
        "team2": ["bos", "tor"],
        "score1": [5, 3],
        "score2": [2, 7],
    })

    silver_df = transform_mlb_to_silver(bronze_df)

    assert len(silver_df) == 2
    assert list(silver_df.columns) == [
        "game_id", "sport", "date", "season", "home_team", "away_team",
        "home_score", "away_score", "stage", "venue",
        "closing_spread", "closing_total",
        "closing_moneyline_home", "closing_moneyline_away",
    ]
    assert (silver_df["sport"] == "mlb").all()
    assert silver_df["home_team"].iloc[0] == "NYY"
    assert silver_df["away_team"].iloc[0] == "BOS"


def test_transform_mlb_to_silver_stage() -> None:
    """MLB transform marks playoff games correctly."""
    bronze_df = pd.DataFrame({
        "date": ["2023-10-01"],
        "season": [2023],
        "neutral": [0],
        "playoff": ["w"],
        "team1": ["nyy"],
        "team2": ["bos"],
        "score1": [4],
        "score2": [1],
    })

    silver_df = transform_mlb_to_silver(bronze_df)

    assert silver_df["stage"].iloc[0] == "playoff"


def test_transform_world_cup_to_silver_schema() -> None:
    """World Cup transform produces the unified silver schema."""
    bronze_df = pd.DataFrame({
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

    silver_df = transform_world_cup_to_silver(bronze_df)

    assert len(silver_df) == 1
    assert silver_df["sport"].iloc[0] == "world_cup"
    assert silver_df["home_team"].iloc[0] == "Qatar"
    assert silver_df["venue"].iloc[0] == "Al Khor"
    assert silver_df["season"].iloc[0] == 2022
