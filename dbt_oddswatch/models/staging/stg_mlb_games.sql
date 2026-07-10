with source as (
    select * from {{ source('oddswatch', 'silver_mlb') }}
)

select
    game_id,
    sport,
    date,
    season,
    home_team,
    away_team,
    home_score,
    away_score,
    stage,
    venue,
    closing_spread,
    closing_total,
    closing_moneyline_home,
    closing_moneyline_away
from source
