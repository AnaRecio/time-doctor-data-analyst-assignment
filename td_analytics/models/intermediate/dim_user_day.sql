{{ config(materialized='table') }}

select
  dd.date_day,
  u.user_id,
  u.account_id,
  u.role,
  u.country,

  case
    when u.activated_at is not null
     and date(u.activated_at) <= dd.date_day
     and (u.deactivated_at is null or date(u.deactivated_at) > dd.date_day)
    then 1 else 0
  end as is_eligible_user

from {{ ref('dim_date') }} dd
join {{ ref('stg_users') }} u
  on dd.date_day >= date(u.created_at)
