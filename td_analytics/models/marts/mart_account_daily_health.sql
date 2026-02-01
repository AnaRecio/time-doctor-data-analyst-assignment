{{ config(materialized='table') }}

with user_day as (
  select *
  from {{ ref('fct_daily_user_activity') }}
),

account_day as (
  select
    account_id,
    event_date,

    -- core usage
    count(distinct user_id) as dau,

    -- engagement
    sum(engagement_events) as engagement_events,
    safe_divide(sum(engagement_events), nullif(count(distinct user_id), 0)) as engagement_events_per_active_user,

    -- sessions
    sum(sessions_started) as sessions_started,
    sum(sessions_stopped) as sessions_stopped,
    safe_divide(sum(sessions_started), nullif(count(distinct user_id), 0)) as sessions_started_per_active_user,

    -- work
    sum(work_session_seconds) as total_work_session_seconds,
    safe_divide(sum(work_session_seconds), nullif(count(distinct user_id), 0)) as avg_work_session_seconds_per_active_user,

    -- output
    sum(tasks_created) as tasks_created,
    sum(tasks_completed) as tasks_completed,
    safe_divide(sum(tasks_completed), nullif(count(distinct user_id), 0)) as tasks_completed_per_active_user,
    safe_divide(sum(tasks_completed), nullif(sum(tasks_created), 0)) as task_completion_rate,

    -- data trust guardrails
    sum(late_events) as late_events,
    safe_divide(
      sum(late_events),
      nullif(sum(engagement_events + sessions_started + sessions_stopped + tasks_created + tasks_completed), 0)
    ) as late_event_rate

  from user_day
  group by 1,2
)

select * from account_day

