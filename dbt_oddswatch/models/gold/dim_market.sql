select 1 as market_key, 'spread' as market_type, 'Point spread' as description
union all
select 2 as market_key, 'total' as market_type, 'Over/under total points' as description
union all
select 3 as market_key, 'moneyline' as market_type, 'Moneyline (win/lose)' as description
