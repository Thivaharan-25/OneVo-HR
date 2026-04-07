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
| `LeaveRequested` | Employee submits | [[notifications]] |
| `LeaveApproved` | Manager approves | [[notifications]], [[workforce-presence]] |
| `LeaveRejected` | Manager rejects | [[notifications]] |
| `LeaveCancelled` | Cancellation | [[notifications]], entitlement adjustment |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/leave/requests` | `leave:create` | Submit request |
| PUT | `/api/v1/leave/requests/{id}/approve` | `leave:approve` | Approve |
| PUT | `/api/v1/leave/requests/{id}/reject` | `leave:approve` | Reject |
| GET | `/api/v1/leave/requests/me` | `leave:read-own` | Own requests |
| GET | `/api/v1/leave/calendar` | `leave:read` | Team leave calendar |

## Related

- [[leave|Leave Module]]
- [[balance-audit]]
- [[leave-entitlements]]
- [[leave-policies]]
- [[leave-types]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[error-handling]]
- [[event-catalog]]
- [[notifications]]
- [[WEEK3-leave]]
