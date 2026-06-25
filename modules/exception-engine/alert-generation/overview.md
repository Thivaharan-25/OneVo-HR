# Alert Generation

**Module:** Exception Engine  
**Feature:** Alert Generation

---

## Purpose

Generates alerts when rule thresholds are breached. One alert per rule per employee per evaluation window (dedup). Data snapshot captured as evidence. Phase 2 Automation Center can handle alert delivery/escalation, case conversation creation, and resolver-based assignment. Phase 1 alert delivery must use lightweight monitoring/attendance notification rules.

## Database Tables

### `exception_alerts`
Key columns: `employee_id`, `rule_id`, `triggered_at`, `severity`, `summary`, `data_snapshot_json` (evidence), `status` (`new`, `acknowledged`, `dismissed`, `escalated`).

Alerts that require human review should link to a workflow case conversation rather than a normal direct message. The case can include the assigned resolver, employee, original requester, or invited participants according to the automation rule.

### `alert_acknowledgements`
Audit trail: `alert_id`, `acknowledged_by_id`, `action` (`acknowledged`, `dismissed`, `escalated`, `noted`), `comment`.

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `ExceptionAlertCreated` | Rule threshold breached | [[modules/notifications/overview\|Notifications]]. Phase 2 Workflow/Automation Engine may also consume this event for advanced routing/escalation. |
| `AlertAcknowledged` | Manager acknowledges/dismisses | Audit trail |

## SignalR Integration

New alerts are pushed to frontend via `exception-alerts` channel in Phase 2. Phase 1 monitoring alerts use Notifications.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/exceptions/alerts` | `exceptions:view` | Phase 2: list active alerts |
| GET | `/api/v1/exceptions/alerts/{id}` | `exceptions:view` | Phase 2: alert detail with evidence |
| PUT | `/api/v1/exceptions/alerts/{id}/acknowledge` | `exceptions:acknowledge` | Phase 2: acknowledge |
| PUT | `/api/v1/exceptions/alerts/{id}/dismiss` | `exceptions:acknowledge` | Phase 2: dismiss |

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
