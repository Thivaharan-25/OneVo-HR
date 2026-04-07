# Escalation Chains

**Module:** Exception Engine  
**Feature:** Escalation Chains

---

## Purpose

Time-based notification routing by severity. If alert is not acknowledged within delay, auto-escalate to next step.

## Database Tables

### `escalation_chains`
Key columns: `severity`, `step_order`, `notify_role` (`reporting_manager`, `department_head`, `hr`, `ceo`, `custom`), `notify_user_id`, `delay_minutes`.

Example for `critical`: 1. reporting_manager (0 min) → 2. hr (30 min) → 3. ceo (60 min).

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `AlertEscalated` | Unacknowledged alert escalated | [[notifications]] |

## Key Business Rules

1. Escalation chains are per-severity, not per-rule.
2. Escalation is time-based via Hangfire delayed jobs.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/exceptions/escalation-chains` | `exceptions:manage` | List chains |
| POST | `/api/v1/exceptions/escalation-chains` | `exceptions:manage` | Create/update chain |

## Related

- [[exception-engine|Exception Engine Module]]
- [[exception-engine/alert-generation/overview|Alert Generation]]
- [[exception-engine/evaluation-engine/overview|Evaluation Engine]]
- [[exception-engine/exception-rules/overview|Exception Rules]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[event-catalog]]
- [[shared-kernel]]
- [[WEEK4-exception-engine]]
