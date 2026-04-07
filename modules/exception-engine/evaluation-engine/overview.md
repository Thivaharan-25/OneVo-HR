# Evaluation Engine

**Module:** Exception Engine  
**Feature:** Evaluation Engine

---

## Purpose

Core evaluation loop that runs during configured work hours. Checks all active rules against latest data.

## Database Tables

### `exception_schedules`
Key columns: `check_interval_minutes` (default 5), `active_from_time`, `active_to_time`, `active_days_json`, `timezone`.

## Evaluation Flow

```
ExceptionEngineEvaluationJob (every 5 min during work hours)
  ├─ Check exception_schedules — within active hours?
  ├─ Load all active exception_rules for tenant
  ├─ For each rule → for each target employee:
  │   ├─ Check monitoring toggles + overrides
  │   ├─ Fetch data from Activity Monitoring / Workforce Presence
  │   ├─ Evaluate threshold_json
  │   └─ If breached: dedup check → create alert → publish event
  └─ Done
```

## Hangfire Jobs

| Job | Schedule | Queue | Purpose |
|:----|:---------|:------|:--------|
| `ExceptionEngineEvaluationJob` | Every 5 min | High | Evaluate all active rules |
| `EscalationJob` | Every 5 min | High | Escalate unacknowledged alerts |

## Key Business Rules

1. Engine only runs during configured work hours.
2. Off-hours activity does NOT trigger alerts.
3. Always check monitoring toggles before evaluating.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/exceptions/schedule` | `exceptions:manage` | Get evaluation schedule |
| PUT | `/api/v1/exceptions/schedule` | `exceptions:manage` | Update schedule |

## Related

- [[exception-engine|Exception Engine Module]]
- [[exception-engine/alert-generation/overview|Alert Generation]]
- [[exception-engine/exception-rules/overview|Exception Rules]]
- [[exception-engine/escalation-chains/overview|Escalation Chains]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[error-handling]]
- [[shared-kernel]]
- [[WEEK4-exception-engine]]
