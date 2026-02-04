{{ config(materialized='view') }}

select
  cast(event_id as string) as event_id,

  cast(user_id as string) as user_id,
  cast(account_id as string) as account_id,

  cast(event_name as string) as event_name,
  cast(event_category as string) as event_category,
  cast(source as string) as source,

  cast(event_ts as timestamp) as event_ts,
  cast(ingested_at as timestamp) as ingested_at,

  cast(duration_seconds as int64) as duration_seconds,
  cast(task_id as string) as task_id

from {{ source('raw', 'raw_fct_event') }}
