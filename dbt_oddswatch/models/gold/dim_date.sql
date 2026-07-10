with all_dates as (
    select distinct date from {{ ref('stg_mlb_games') }}
    union
    select distinct date from {{ ref('stg_world_cup_games') }}
)

select
    row_number() over (order by date) as date_key,
    date,
    day_of_week(date) as day_of_week_num,
    case day_of_week(date)
        when 1 then 'Monday'
        when 2 then 'Tuesday'
        when 3 then 'Wednesday'
        when 4 then 'Thursday'
        when 5 then 'Friday'
        when 6 then 'Saturday'
        when 7 then 'Sunday'
    end as day_of_week,
    month(date) as month,
    year(date) as year,
    day_of_week(date) in (6, 7) as is_weekend
from all_dates
