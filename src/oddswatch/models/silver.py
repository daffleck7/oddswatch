"""Pydantic models for silver (cleaned/normalized) data."""

from datetime import date

from pydantic import BaseModel


class SilverGame(BaseModel):
    """Cleaned and normalized game record with synthetic closing lines.

    Unified schema across MLB and World Cup.
    """

    game_id: str
    sport: str
    date: date
    season: int
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    stage: str | None
    venue: str | None
    closing_spread: float
    closing_total: float
    closing_moneyline_home: int
    closing_moneyline_away: int
