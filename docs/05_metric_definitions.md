# Metric Definitions

All KPIs are calculated at the grain: **account_id + event_date (daily)** and are meant to power an executive scorecard plus operational drilldowns.

**Primary Source Tables**
- `dim_user_day` (user eligibility + daily user context)
- `fct_user_day_activity` (daily user activity rollups)
- `stg_accounts` (account attributes)

**Time Semantics**
- Activity is attributed to the day of `event_ts` (occurred time).
- Late arriving data is tracked via `late_events` / `late_event_rate` and can cause small backfilled changes.

---

## KPI Metrics (Account-Day)

### Eligible Users
- **Field:** `eligible_users`
- **Definition:** Count of users marked as eligible on `event_date` within an account.
- **Formula (conceptual):** `countif(is_eligible_user = 1)`
- **Grain:** account-day
- **Why it matters:** Establishes the denominator for adoption and normalizes accounts of different sizes.
- **Assumptions / Limitations:**
  - “Eligible” should represent users expected to use the product (e.g., activated/seat assigned).
  - If eligibility logic changes, adoption comparability across time changes.

---

### Daily Active Users (DAU)
- **Field:** `dau`
- **Definition:** Count of distinct users who generated activity on `event_date`.
- **Formula (conceptual):** `count(distinct activity.user_id)`
- **Grain:** account-day
- **Why it matters:** Core adoption signal and the executive “heartbeat” metric.
- **Assumptions / Limitations:**
  - DAU can shift slightly if late events arrive and backfill.
  - Activity requires a row in `fct_user_day_activity` (i.e., at least one tracked event).

---

### Adoption Rate
- **Field:** `adoption_rate`
- **Definition:** Share of eligible users who were active on `event_date`.
- **Formula:** `dau / eligible_users`
- **Grain:** account-day
- **Why it matters:** Normalizes adoption by account size (more meaningful than raw DAU alone).
- **Assumptions / Limitations:**
  - If `eligible_users` is 0, metric is null (division guarded).
  - Adoption can be inflated if eligibility is too narrow or lagging (e.g., seats not updated).

---

### Engagement per Active User
- **Field:** `engagement_per_active_user`
- **Definition:** Average engagement events per active user on `event_date`.
- **Formula:** `sum(engagement_events) / dau`
- **Grain:** account-day
- **Why it matters:** Measures *depth* of usage (not just presence).
- **Assumptions / Limitations:**
  - Sensitive to event instrumentation changes.

---

### Sessions Started per Active User
- **Field:** `sessions_started_per_active_user`
- **Definition:** Average number of sessions started per active user on `event_date`.
- **Formula:** `sum(sessions_started) / dau`
- **Grain:** account-day
- **Why it matters:** Proxy for workflow frequency (how often users initiate a work cycle).
- **Assumptions / Limitations:**
  - Assumes `sessions_started` is reliably tracked (e.g., timer_start).
  - Not a perfect “session” definition unless bounded and deduped.

---

### Work Minutes per Active User
- **Field:** `work_min_per_active_user`
- **Definition:** Average time spent working per active user on `event_date`, in minutes.
- **Formula:** `(sum(work_seconds) / 60) / dau`
- **Grain:** account-day
- **Why it matters:** Proxy for product value capture / time investment.
- **Assumptions / Limitations:**
  - Assumes `work_seconds` is derived from reliable duration sources.
  - Outliers can distort averages; in production you’d cap or flag extreme values.

---

### Tasks Completed per Active User
- **Field:** `tasks_completed_per_active_user`
- **Definition:** Average completed tasks per active user on `event_date`.
- **Formula:** `sum(tasks_completed) / dau`
- **Grain:** account-day
- **Why it matters:** Productivity / output signal tied to business outcomes.
- **Assumptions / Limitations:**
  - Depends on consistent task event tracking.
  - Task complexity varies; this is quantity-based productivity, not quality-based.

---

### Late Event Rate (Data Trust / Pipeline Reality)
- **Field:** `late_event_rate`
- **Definition:** Share of recorded activity events that arrived late (ingested > allowed threshold after event_ts).
- **Formula:** `sum(late_events) / sum(engagement_events + sessions_started + tasks_completed)`
- **Grain:** account-day
- **Why it matters:** A guardrail for executive trust—high late rates can explain “moving” numbers.
- **Assumptions / Limitations:**
  - Denominator is a proxy for “total relevant activity” (not all event types included).

---

## Business Interpretations

- **Adoption (DAU + Adoption Rate):** Are users showing up, and is that healthy vs account size?
- **Engagement & Workflow (Engagement/User, Sessions/User):** Are users interacting meaningfully and repeatedly?
- **Productivity (Work Min/User, Tasks Completed/User):** Is the product driving measurable output?
- **Trust (Late Event Rate):** Are changes real behavior shifts or pipeline latency artifacts?

- Grain: day (rolling) or week
- Source: dim_user + fct_event
- Notes: Activation is required; users who never activated are excluded.

### Week-over-Week Retention (Activity-Based)
- Definition: % of users active in week N who are also active in week N+1.
- Grain: week cohort
- Source: fct_event

## Productivity / Output Proxies

### Productive Time (per Active User per Day)
- Definition: Sum of duration_seconds for relevant work_session events (e.g., timer_stop) per user-day.
- Grain: user-day
- Source: fct_event
- Caveats: duration_seconds may be missing or contain outliers; use guardrails.

### Outputs per Active User (per Day)
- Definition: Count of task_completed events per user-day.
- Grain: user-day
- Source: fct_event
- Caveats: task_id may be missing for some events (intentional imperfection).

