{{ config(materialized='table') }}

with base as (
  select
    user_id,
    account_id,
    date(event_ts) as event_date,

    event_name,
    event_category,
    duration_seconds,

    event_ts,
    ingested_at,

    -- late-arriving event indicator
    case
      when ingested_at > timestamp_add(event_ts, interval 6 hour) then 1
      else 0
    end as is_late_event
  from {{ ref('stg_events') }}
),

agg as (
  select
    account_id,
    user_id,
    event_date,

    -- activity foundation
    1 as is_active_user,

    -- session proxies
    sum(case when event_name = 'timer_start' then 1 else 0 end) as sessions_started,
    sum(case when event_name = 'timer_stop' then 1 else 0 end) as sessions_stopped,

    -- time proxy (uses duration when present; missing durations stay null -> treated as 0)
    sum(case when event_category = 'work_session' then coalesce(duration_seconds, 0) else 0 end) as work_session_seconds,

    -- output proxies
    sum(case when event_name = 'task_created' then 1 else 0 end) as tasks_created,
    sum(case when event_name = 'task_completed' then 1 else 0 end) as tasks_completed,

    -- data quality / pipeline reality
    sum(is_late_event) as late_events
  from base
  group by 1,2,3
)

select * from agg
