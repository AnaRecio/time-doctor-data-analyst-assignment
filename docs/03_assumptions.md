# Assumptions

## Assumptions
1) Event-driven usage model  
Product usage and behavior are represented as timestamped events.

2) Productivity is a proxy  
We treat productivity signals (e.g., work session time) as proxy indicators rather than absolute truth. Some events may be classified as productive, but this is not perfect.

3) Output is proxied by task events  
Outputs are approximated through task creation/completion events. This avoids domain-specific definitions of "output" and keeps the model simple.

4) Late-arriving events exist  
Events may be ingested hours or days after they occurred. We include ingested_at to support backfills, freshness discussions, and realistic monitoring considerations.

5) Users may never activate  
Some users are created but never activated (activated_at is null) and therefore generate no events.

6) Churn may appear as inactivity  
Users may stop generating events without explicit deactivation. Deactivation is also supported via deactivated_at.
