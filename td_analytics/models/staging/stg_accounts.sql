{{ config(materialized='view') }}

select
  -- keys
  cast(account_id as string) as account_id,

  -- attributes
  cast(account_name as string) as account_name,
  cast(plan_tier as string) as plan_tier,
  cast(region as string) as region,
  cast(is_active as bool) as is_active,

  -- timestamps
  cast(created_at as timestamp) as created_at

from {{ source('raw', 'raw_dim_account') }}
