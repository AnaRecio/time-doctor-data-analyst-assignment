{{ config(materialized='table') }}

with user_day as (
  select *
  from {{ ref('fct_daily_user_activity') }}
),

account_day as (
  select
    account_id,
    event_date,

    count(distinct user_id) as dau,
    sum(work_session_seconds) as total_work_session_seconds,
    sum(tasks_created) as tasks_created,
    sum(tasks_completed) as tasks_completed,
    sum(late_events) as late_events,

    -- helpful ratios (safe divisions)
    safe_divide(sum(tasks_completed), nullif(count(distinct user_id), 0)) as tasks_completed_per_active_user,
    safe_divide(sum(work_session_seconds), nullif(count(distinct user_id), 0)) as avg_work_session_seconds_per_active_user
  from user_day
  group by 1,2
)

select
  a.account_id,
  a.event_date,

  a.dau,
  a.total_work_session_seconds,
  a.tasks_created,
  a.tasks_completed,
  a.late_events,

  a.tasks_completed_per_active_user,
  a.avg_work_session_seconds_per_active_user

from account_day a
