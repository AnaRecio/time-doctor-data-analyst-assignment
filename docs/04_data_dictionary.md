# Data Dictionary

This dictionary documents the raw layer datasets. Types are indicative and tool-agnostic.

## dim_account

| column_name   | type      | nullable | description                                  | example                     |
|--------------|-----------|----------|----------------------------------------------|-----------------------------|
| account_id    | string    | N        | Unique identifier for the account            | "9b2c...-uuid"              |
| account_name  | string    | N        | Human-readable account name                  | "Account_48392"             |
| plan_tier     | string    | N        | Subscription tier                            | "pro"                       |
| created_at    | timestamp | N        | Account creation timestamp                   | "2025-06-10T12:00:00"       |
| region        | string    | Y        | Geographic region (coarse)                   | "NA"                        |
| is_active     | boolean   | N        | Whether the account is currently active      | true                        |

## dim_user

| column_name    | type      | nullable | description                                   | example                     |
|---------------|-----------|----------|-----------------------------------------------|-----------------------------|
| user_id        | string    | N        | Unique identifier for the user                | "a13f...-uuid"              |
| account_id     | string    | N        | Account the user belongs to                   | "9b2c...-uuid"              |
| role           | string    | N        | User role within the account                  | "member"                    |
| created_at     | timestamp | N        | User creation timestamp                       | "2025-11-02T09:30:00"       |
| activated_at   | timestamp | Y        | When the user activated the product           | "2025-11-03T10:00:00"       |
| timezone       | string    | Y        | User timezone                                 | "America/Bogota"            |
| country        | string    | Y        | Country code                                  | "CR"                        |
| is_active      | boolean   | N        | Whether the user is currently active          | true                        |
| deactivated_at | timestamp | Y        | Deactivation timestamp (if deactivated)       | "2025-12-15T08:00:00"       |

## fct_event

| column_name      | type      | nullable | description                                                      | example                     |
|-----------------|-----------|----------|------------------------------------------------------------------|-----------------------------|
| event_id         | string    | N        | Unique identifier for the event                                  | "f12c...-uuid"              |
| event_ts         | timestamp | N        | Timestamp when the event occurred                                | "2026-01-10T14:22:11"       |
| ingested_at      | timestamp | N        | Timestamp when the event was ingested                            | "2026-01-10T14:25:40"       |
| event_name       | string    | N        | Event type name                                                  | "timer_stop"                |
| event_category   | string    | N        | High-level category: engagement, work_session, output            | "work_session"              |
| user_id          | string    | N        | User who produced the event                                      | "a13f...-uuid"              |
| account_id       | string    | N        | Account associated with the event (denormalized for BI)          | "9b2c...-uuid"              |
| task_id          | string    | Y        | Task identifier for output events                                | "c88d...-uuid"              |
| duration_seconds | integer   | Y        | Duration associated with the event (e.g., session length)        | 3600                        |
| is_productive    | boolean   | Y        | Productivity flag (proxy; only relevant for some event types)    | true                        |
| source           | string    | Y        | Event source/channel                                             | "desktop"                   |
