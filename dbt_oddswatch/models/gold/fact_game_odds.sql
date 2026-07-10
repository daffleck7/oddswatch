with games as (
    select * from {{ ref('stg_mlb_games') }}
    union all
    select * from {{ ref('stg_world_cup_games') }}
),

dim_game as (
    select game_key, game_id from {{ ref('dim_game') }}
),

dim_date as (
    select date_key, date from {{ ref('dim_date') }}
),

dim_team as (
    select team_key, team_name from {{ ref('dim_team') }}
)

select
    dg.game_key,
    dd.date_key,
    ht.team_key as home_team_key,
    at.team_key as away_team_key,
    g.sport,
    g.closing_spread,
    g.closing_total,
    g.closing_moneyline_home,
    g.closing_moneyline_away,
    g.home_score,
    g.away_score,
    (g.home_score - g.away_score + g.closing_spread) > 0 as cover,
    case
        when (g.home_score + g.away_score) > g.closing_total then 'over'
        when (g.home_score + g.away_score) < g.closing_total then 'under'
        else 'push'
    end as over_under_result
from games g
left join dim_game dg on g.game_id = dg.game_id
left join dim_date dd on g.date = dd.date
left join dim_team ht on g.home_team = ht.team_name
left join dim_team at on g.away_team = at.team_name
