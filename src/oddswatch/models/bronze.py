"""Pydantic models for bronze (raw) data."""

from pydantic import BaseModel


class BronzeMLBGame(BaseModel):
    """Raw MLB game record from FiveThirtyEight ELO dataset."""

    date: str
    season: int
    neutral: int
    playoff: str | None
    team1: str
    team2: str
    score1: float
    score2: float


class BronzeWorldCupMatch(BaseModel):
    """Raw World Cup match record from international results dataset."""

    date: str
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    tournament: str
    city: str
    country: str
    neutral: str
