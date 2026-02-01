# Metric Definitions

These metrics are designed to be derived from the atomic event table and support time-based analysis and trends. All metrics should be computed using event_ts (occurred time) and may be reconciled when late-arriving data is ingested (ingested_at).

## User Activity Metrics

### Daily Active Users (DAU)
- Definition: Count of distinct users with at least one event on a given day.
- Grain: day
- Source: fct_event
- Notes: DAU may change slightly with late-arriving events.

### Weekly Active Users (WAU)
- Definition: Count of distinct users with at least one event in the last 7 days.
- Grain: day (rolling) or week (calendar)
- Source: fct_event

### Active Days per User (Weekly)
- Definition: For each user, number of distinct active days in a calendar week.
- Grain: user-week
- Source: fct_event

## Retention / Inactivity Proxies

### 7-Day Inactivity Rate
- Definition: % of users who have no events in the last 7 days (among activated users).
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

## Data Quality Notes (Metric Reliability)
- Late-arriving events can shift day-level totals; production systems typically use incremental backfills.
- Outlier durations should be capped or flagged for reporting to avoid misleading aggregates.
- Missing duration_seconds should be treated as null and excluded from sums unless imputed.
