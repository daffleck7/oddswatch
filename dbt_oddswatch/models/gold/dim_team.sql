with all_teams as (
    select home_team as team_name, sport from {{ ref('stg_mlb_games') }}
    union
    select away_team as team_name, sport from {{ ref('stg_mlb_games') }}
    union
    select home_team as team_name, sport from {{ ref('stg_world_cup_games') }}
    union
    select away_team as team_name, sport from {{ ref('stg_world_cup_games') }}
),

distinct_teams as (
    select distinct team_name, sport
    from all_teams
)

select
    row_number() over (order by sport, team_name) as team_key,
    lower(replace(team_name, ' ', '_')) as team_id,
    team_name,
    sport
from distinct_teams
