"""Bronze-to-silver transformations.

Cleans raw data, normalizes schemas, and generates synthetic closing lines
grounded in actual game outcomes.
"""

import random

import pandas as pd


def generate_closing_spread(home_score: int, away_score: int, seed: int = 0) -> float:
    """Generate a synthetic closing spread from actual scores.

    The spread is centered on the negative score differential (home perspective)
    with bounded random noise, rounded to the nearest half-point.
    """
    rng = random.Random(seed)
    actual_diff = home_score - away_score
    noise = rng.uniform(-2.5, 2.5)
    raw_spread = -actual_diff + noise
    rounded = round(raw_spread * 2) / 2
    if rounded == int(rounded):
        rounded += 0.5 if rng.random() > 0.5 else -0.5
    return rounded


def generate_closing_total(home_score: int, away_score: int, seed: int = 0) -> float:
    """Generate a synthetic closing total from actual scores.

    The total is centered on the combined score with bounded random noise,
    rounded to the nearest half-point.
    """
    rng = random.Random(seed)
    actual_total = home_score + away_score
    noise = rng.uniform(-2.5, 2.5)
    raw_total = actual_total + noise
    rounded = round(raw_total * 2) / 2
    if rounded % 1 == 0:
        rounded += 0.5
    return rounded


def spread_to_moneyline(spread: float) -> tuple[int, int]:
    """Convert a point spread to American moneyline odds.

    Uses a linear approximation: each point of spread ~ 15 moneyline points
    from the -110 baseline.
    """
    points_per_unit = 15
    base = 110
    offset = abs(spread) * points_per_unit

    if spread < 0:
        home_ml = -int(base + offset)
        away_ml = int(base + offset - 10)
    elif spread > 0:
        home_ml = int(base + offset - 10)
        away_ml = -int(base + offset)
    else:
        home_ml = -110
        away_ml = -110

    return home_ml, away_ml


def transform_mlb_to_silver(bronze_df: pd.DataFrame) -> pd.DataFrame:
    """Transform raw MLB bronze data into the unified silver schema.

    Normalizes column names, generates synthetic closing lines, and adds
    a sport identifier.
    """
    rows = []
    for idx, row in bronze_df.iterrows():
        home_score = int(row["score1"])
        away_score = int(row["score2"])
        spread = generate_closing_spread(home_score, away_score, seed=idx)
        total = generate_closing_total(home_score, away_score, seed=idx)
        home_ml, away_ml = spread_to_moneyline(spread)

        rows.append({
            "game_id": f"mlb_{row['date']}_{row['team1']}_{row['team2']}",
            "sport": "mlb",
            "date": pd.to_datetime(row["date"]).date(),
            "season": int(row["season"]),
            "home_team": row["team1"].upper(),
            "away_team": row["team2"].upper(),
            "home_score": home_score,
            "away_score": away_score,
            "stage": "playoff" if row.get("playoff") else "regular_season",
            "venue": None,
            "closing_spread": spread,
            "closing_total": total,
            "closing_moneyline_home": home_ml,
            "closing_moneyline_away": away_ml,
        })

    return pd.DataFrame(rows)


def transform_world_cup_to_silver(bronze_df: pd.DataFrame) -> pd.DataFrame:
    """Transform raw World Cup bronze data into the unified silver schema.

    Normalizes column names, generates synthetic closing lines, and adds
    a sport identifier. Extracts tournament year as season.
    """
    rows = []
    for idx, row in bronze_df.iterrows():
        home_score = int(row["home_score"])
        away_score = int(row["away_score"])
        spread = generate_closing_spread(home_score, away_score, seed=idx)
        total = generate_closing_total(home_score, away_score, seed=idx)
        home_ml, away_ml = spread_to_moneyline(spread)
        game_date = pd.to_datetime(row["date"]).date()

        rows.append({
            "game_id": f"wc_{row['date']}_{row['home_team']}_{row['away_team']}",
            "sport": "world_cup",
            "date": game_date,
            "season": game_date.year,
            "home_team": row["home_team"],
            "away_team": row["away_team"],
            "home_score": home_score,
            "away_score": away_score,
            "stage": None,
            "venue": row.get("city"),
            "closing_spread": spread,
            "closing_total": total,
            "closing_moneyline_home": home_ml,
            "closing_moneyline_away": away_ml,
        })

    return pd.DataFrame(rows)
