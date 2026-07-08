"""Pydantic models for gold (star schema) data."""

from datetime import date

from pydantic import BaseModel


class DimTeam(BaseModel):
    """Team dimension table."""

    team_key: int
    team_id: str
    team_name: str
    sport: str
    group_or_conference: str | None
    country: str | None


class DimGame(BaseModel):
    """Game dimension table."""

    game_key: int
    game_id: str
    sport: str
    season: int
    date: date
    stage: str | None
    home_team_key: int
    away_team_key: int
    venue: str | None


class DimDate(BaseModel):
    """Date dimension table."""

    date_key: int
    date: date
    day_of_week: str
    month: int
    year: int
    is_weekend: bool


class DimMarket(BaseModel):
    """Market type dimension table."""

    market_key: int
    market_type: str
    description: str


class FactGameOdds(BaseModel):
    """Fact table for game closing odds and results."""

    game_key: int
    date_key: int
    home_team_key: int
    away_team_key: int
    sport: str
    closing_spread: float
    closing_total: float
    closing_moneyline_home: int
    closing_moneyline_away: int
    home_score: int
    away_score: int
    cover: bool
    over_under_result: str


class DimBook(BaseModel):
    """Sportsbook dimension table with SCD Type 2. Placeholder for streaming layer."""

    book_key: int
    book_id: str
    book_name: str
    base_fee_pct: float
    odds_format: str
    valid_from: date
    valid_to: date | None
    is_current: bool
