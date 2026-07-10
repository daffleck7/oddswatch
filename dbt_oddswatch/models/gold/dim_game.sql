with games as (
    select * from {{ ref('stg_mlb_games') }}
    union all
    select * from {{ ref('stg_world_cup_games') }}
),

teams as (
    select team_key, team_name from {{ ref('dim_team') }}
)

select
    row_number() over (order by g.date, g.game_id) as game_key,
    g.game_id,
    g.sport,
    g.season,
    g.date,
    g.stage,
    ht.team_key as home_team_key,
    at.team_key as away_team_key,
    g.venue
from games g
left join teams ht on g.home_team = ht.team_name
left join teams at on g.away_team = at.team_name
