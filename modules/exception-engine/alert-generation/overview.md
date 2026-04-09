# Alert Generation

**Module:** Exception Engine  
**Feature:** Alert Generation

---

## Purpose

Generates alerts when rule thresholds are breached. One alert per rule per employee per evaluation window (dedup). Data snapshot captured as evidence.

## Database Tables

### `exception_alerts`
Key columns: `employee_id`, `rule_id`, `triggered_at`, `severity`, `summary`, `data_snapshot_json` (evidence), `status` (`new`, `acknowledged`, `dismissed`, `escalated`).

### `alert_acknowledgements`
Audit trail: `alert_id`, `acknowledged_by_id`, `action` (`acknowledged`, `dismissed`, `escalated`, `noted`), `comment`.

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `ExceptionAlertCreated` | Rule threshold breached | [[modules/notifications/overview|Notifications]] |
| `AlertAcknowledged` | Manager acknowledges/dismisses | Audit trail |

## SignalR Integration

New alerts pushed to frontend via `exception-alerts` channel.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/exceptions/alerts` | `exceptions:view` | List active alerts |
| GET | `/api/v1/exceptions/alerts/{id}` | `exceptions:view` | Alert detail with evidence |
| PUT | `/api/v1/exceptions/alerts/{id}/acknowledge` | `exceptions:acknowledge` | Acknowledge |
| PUT | `/api/v1/exceptions/alerts/{id}/dismiss` | `exceptions:acknowledge` | Dismiss |

## Related

- [[modules/exception-engine/overview|Exception Engine Module]]
- [[frontend/architecture/overview|Evaluation Engine]]
- [[frontend/architecture/overview|Exception Rules]]
- [[frontend/architecture/overview|Escalation Chains]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/messaging/error-handling|Error Handling]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV2-exception-engine|DEV2: Exception Engine]]
