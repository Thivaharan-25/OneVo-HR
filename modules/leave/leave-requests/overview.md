# Leave Requests

**Module:** Leave  
**Feature:** Leave Requests

---

## Purpose

Leave request submission and approval workflow with calendar conflict detection.

## Database Tables

### `leave_requests`
Key columns: `employee_id`, `leave_type_id`, `start_date`, `end_date`, `total_days`, `reason`, `status` (`pending`, `approved`, `rejected`, `cancelled`), `approved_by_id`, `conflict_snapshot_json`, `document_file_id`.

## Key Business Rules

1. Validates sufficient balance, no overlapping requests, max consecutive days.
2. Calendar conflict detection on submission — warnings only, does not block.
3. Conflict snapshot stored for approver review.

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `LeaveRequested` | Employee submits | [[modules/notifications/overview|Notifications]] |
| `LeaveApproved` | Manager approves | [[modules/notifications/overview|Notifications]], [[modules/workforce-presence/overview|Workforce Presence]] |
| `LeaveRejected` | Manager rejects | [[modules/notifications/overview|Notifications]] |
| `LeaveCancelled` | Cancellation | [[modules/notifications/overview|Notifications]], entitlement adjustment |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/leave/requests` | `leave:create` | Submit request |
| PUT | `/api/v1/leave/requests/{id}/approve` | `leave:approve` | Approve |
| PUT | `/api/v1/leave/requests/{id}/reject` | `leave:approve` | Reject |
| GET | `/api/v1/leave/requests/me` | `leave:read-own` | Own requests |
| GET | `/api/v1/leave/calendar` | `leave:read` | Team leave calendar |

## Related

- [[modules/leave/overview|Leave Module]]
- [[modules/leave/balance-audit/overview|Balance Audit]]
- [[modules/leave/leave-entitlements/overview|Leave Entitlements]]
- [[modules/leave/leave-policies/overview|Leave Policies]]
- [[modules/leave/leave-types/overview|Leave Types]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/messaging/error-handling|Error Handling]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[modules/notifications/overview|Notifications]]
- [[current-focus/DEV1-leave|DEV1: Leave]]
