{{ config(materialized='table') }}

with users as (
  select * from {{ ref('dim_user_day') }}
),

activity as (
  select * from {{ ref('fct_user_day_activity') }}
),

accounts as (
  select * from {{ ref('stg_accounts') }}
)

select
  u.date_day as event_date,
  u.account_id,
  a.account_name,
  a.plan_tier,
  a.region,
  a.is_active,

 
  countif(u.is_eligible_user = 1) as eligible_users,

 
  count(distinct activity.user_id) as dau,


  safe_divide(
    count(distinct activity.user_id),
    nullif(countif(u.is_eligible_user = 1), 0)
  ) as adoption_rate,


  safe_divide(
    sum(activity.engagement_events),
    nullif(count(distinct activity.user_id), 0)
  ) as engagement_per_active_user,


  safe_divide(
    sum(activity.sessions_started),
    nullif(count(distinct activity.user_id), 0)
  ) as sessions_started_per_active_user,


  safe_divide(
    sum(activity.work_seconds) / 60,
    nullif(count(distinct activity.user_id), 0)
  ) as work_min_per_active_user,


  safe_divide(
    sum(activity.tasks_completed),
    nullif(count(distinct activity.user_id), 0)
  ) as tasks_completed_per_active_user,


  safe_divide(
    sum(activity.late_events),
    nullif(sum(activity.engagement_events + activity.sessions_started + activity.tasks_completed), 0)
  ) as late_event_rate

from users u
left join activity
  on u.user_id = activity.user_id
 and u.date_day = activity.event_date
left join accounts a
  on u.account_id = a.account_id

group by 1,2,3,4,5,6


