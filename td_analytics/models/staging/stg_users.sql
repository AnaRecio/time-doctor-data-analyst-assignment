{{ config(materialized='view') }}

select
  -- keys
  cast(user_id as string) as user_id,
  cast(account_id as string) as account_id,

  -- attributes
  cast(role as string) as role,
  cast(country as string) as country,
  cast(is_active as bool) as is_active,

  -- timestamps
  cast(created_at as timestamp) as created_at,
  cast(activated_at as timestamp) as activated_at,
  cast(deactivated_at as timestamp) as deactivated_at

from {{ source('raw', 'raw_dim_user') }}
