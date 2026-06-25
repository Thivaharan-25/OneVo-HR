# Time Off Requests

**Module:** Time Off
**Feature:** Time Off Requests

---

## Purpose

Time off request submission, approval, rejection, and cancellation for self-service time_off and managed time_off actions.

Managers remain employees and use the same self-service time_off flow for their own time_off. Managed visibility over other employees is permission-based and separate.

## Database Tables

### `time_off_requests`

Key columns: `employee_id`, `time_off_type_id`, `start_date`, `end_date`, optional `start_time`/`end_time`, `request_duration_minutes`, `deduction_minutes`, `reason`, `status` (`pending`, `approved`, `rejected`, `cancelled`), `approved_by_id`, `conflict_snapshot_json`, `document_file_id`.

## Key Business Rules

1. Self-service time_off access is personal employee access.
2. Managed time_off visibility requires scoped people-management access.
3. Request validation checks minute balance, overlapping Time Off requests, and policy rules.
4. Calendar conflict detection on submission is warning-only and does not block by itself.
5. Schedules define expected working pattern for attendance; Calendar shows Time Off, holidays, schedules, and events in time context.
6. Time Off request duration is captured directly as minutes. The UI may help the user enter duration using date/time fields, but the saved request stores `request_duration_minutes`.
7. Full-day and half-day are not canonical request modes in Phase 1. If added later, they are UI shortcuts only and must convert to explicit minutes before saving.
8. Shift schedules are used for attendance expectations, calendar display, and availability context — they do not calculate Time Off request duration in Phase 1.
9. All request durations and deductions are stored in minutes.

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `TimeOffRequested` | Employee submits | [[modules/notifications/overview|Notifications]] |
| `TimeOffApproved` | Configured approver approves | [[modules/notifications/overview|Notifications]], [[modules/time-attendance/overview|Time & Attendance]], [[modules/calendar/overview|Calendar]] |
| `TimeOffRejected` | Configured approver rejects | [[modules/notifications/overview|Notifications]] |
| `TimeOffCancelled` | Cancellation | [[modules/notifications/overview|Notifications]], entitlement adjustment |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/time-off/requests` | `time_off:create` | Submit request |
| GET | `/api/v1/time-off/requests/me` | `time_off:read-own` | Own requests |
| PUT | `/api/v1/time-off/requests/{id}/approve` | `time_off:approve` | Approve |
| PUT | `/api/v1/time-off/requests/{id}/reject` | `time_off:approve` | Reject |

## Related

- [[modules/time-off/overview|Time Off Module]]
- [[modules/time-off/time-off-entitlements/overview|Time Off Entitlements]]
- [[modules/time-off/time-off-policies/overview|Time Off Policies]]
- [[modules/time-off/time-off-types/overview|Time Off Types]]
- [[modules/calendar/overview|Calendar]]
