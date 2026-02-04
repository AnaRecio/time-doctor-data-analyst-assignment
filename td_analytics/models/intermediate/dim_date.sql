{{ config(materialized='table') }}

with bounds as (
  select
    min(date(event_ts)) as min_date,
    max(date(event_ts)) as max_date
  from {{ ref('stg_events') }}
)

select d as date_day
from bounds,
unnest(generate_date_array(min_date, max_date)) as d
