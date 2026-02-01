# Data Model

## Design Principles

- Use a minimal set of core entities to keep the model realistic, understandable, and easy to extend.
- Store atomic, time-stamped events as the single source of truth for all usage analytics.
- Derive activity, sessions, and metrics in downstream transformation layers rather than introducing additional raw entities.
- Favor BI simplicity and analytical flexibility over strict normalization when it improves usability and performance.

---

## Entities Overview (Raw Layer)

### 1) dim_account

**Grain:** 1 row per account (customer organization/team)

**Primary Key:** `account_id`

**Purpose:**
- Enables customer-level segmentation and rollups.
- Supports account health views and plan-tier comparisons.
- Provides the organizational context for user activity.

**Key Attributes:**
- `plan_tier`
- `created_at`
- `region`
- `is_active`

---

### 2) dim_user

**Grain:** 1 row per user

**Primary Key:** `user_id`  
**Foreign Key:** `account_id -> dim_account.account_id`

**Purpose:**
- Captures user lifecycle (created, activated, deactivated).
- Enables behavioral segmentation by role and geography.
- Provides the bridge between organizational context and activity events.

**Key Attributes:**
- `role`
- `created_at`
- `activated_at`
- `is_active`
- `deactivated_at`

---

### 3) fct_event

**Grain:** 1 row per event (atomic activity record)

**Primary Key:** `event_id`  

**Foreign Keys:**  
- `user_id -> dim_user.user_id`  
- `account_id -> dim_account.account_id` (denormalized)

**Purpose:**
- Serves as the single source of truth for all usage analytics.
- Enables time-based trends, retention proxies, and productivity/output proxies.
- Preserves the historical context of each event at the time it occurred.

---

### Required Time Fields

- `event_ts`: when the event actually occurred (business truth)
- `ingested_at`: when the event was received by the system

**Usage of these fields:**
- Metrics and trends are computed using `event_ts`.
- `ingested_at` supports realistic handling of late-arriving data, freshness monitoring, and incremental backfills.

---

### Optional Fields

- `duration_seconds` (nullable)
- `task_id` (nullable)
- `source` (desktop / web / mobile / api)

These fields allow richer analysis without overcomplicating the raw model.

---

## Relationships

- `dim_account (1) -> (many) dim_user`
- `dim_user (1) -> (many) fct_event`
- `dim_account (1) -> (many) fct_event` (via denormalized `account_id`)


---

## Event Taxonomy

Events are grouped into high-level categories to support analysis without building an overly complex event system.

| event_name         | event_category |
|--------------------|----------------|
| app_open           | engagement     |
| dashboard_view     | engagement     |
| timer_start        | work_session   |
| timer_stop         | work_session   |
| idle_detected      | work_session   |
| manual_time_added  | work_session   |
| task_created       | output         |
| task_completed     | output         |

---

## Notes on Activity, Sessions, and Outputs

### Activity
Activity is derived from the presence of events on a given day (e.g., daily active users, active days per week).

### Work Sessions
Work session time is calculated using `timer_stop.duration_seconds` only.  
This avoids double counting and removes the need for complex session reconstruction logic while remaining realistic.

### Outputs
Outputs are proxied using task-related events (e.g., `task_completed` per user per day).  
This avoids domain-specific definitions of output while still allowing meaningful productivity signals.

