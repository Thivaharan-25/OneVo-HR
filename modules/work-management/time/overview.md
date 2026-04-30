# Time Management

**Module:** WorkSync
**Feature:** Time Management
**Namespace:** `WorkSync.Time`
**Owner:** DEV5
**Tables:** 3

---

## Purpose

Time tracking for work done on tasks. Developers log time manually or start/stop a timer. Time logs feed HR payroll analytics and the Discrepancy Engine (Pillar 2) via `wms_daily_time_logs`. Overtime correlation links `overtime_records` to tasks.

---

## Database Tables

### `time_logs`
Key columns: `task_id` (FK → tasks), `user_id`, `workspace_id`, `tenant_id`, `logged_date`, `duration_minutes`, `description`, `source` (`manual`, `timer`, `ide_tag`), `timesheet_entry_id` (FK → timesheet_entries, nullable).

`time_logs.user_id` → `employees.user_id` is the HR correlation point. Never store `employee_id` directly in WorkSync tables.

### `timesheets`
Weekly/bi-weekly time summary per user. Key columns: `user_id`, `workspace_id`, `tenant_id`, `period_start`, `period_end`, `status` (`draft`, `submitted`, `approved`, `rejected`), `total_minutes`, `submitted_at`, `approved_by_id`.

### `timesheet_entries`
Individual day entries within a timesheet. Key columns: `timesheet_id`, `logged_date`, `total_minutes`, `task_breakdown_json`.

---

## Key Business Rules

1. Only one active timer per user at a time: `time_logs` row with `ended_at = null`. Application layer enforces uniqueness.
2. IDE tag `@time:log 2h` creates a `time_logs` row with `source = ide_tag`.
3. `time_logs` feed `wms_daily_time_logs` in the Discrepancy Engine — Hangfire aggregates daily.
4. `overtime_records.task_id` (nullable) references `tasks.id` for overtime-to-task correlation.
5. Timesheet submission locks entries — no changes allowed after `status = submitted`.

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `TimeLoggedEvent` | Time log created | Timesheet aggregation, Discrepancy Engine feed |
| `TimesheetSubmittedEvent` | Timesheet status → submitted | Notifications (approver) |
| `TimesheetApprovedEvent` | Timesheet approved | Payroll integration signal |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/tasks/{id}/time-logs` | `time:read` | Logs for a task |
| POST | `/api/v1/tasks/{id}/time-logs` | `time:write` | Manual log |
| POST | `/api/v1/me/timer/start` | `time:write` | Start timer |
| PATCH | `/api/v1/me/timer/stop` | `time:write` | Stop timer |
| GET | `/api/v1/me/timesheets` | `time:read` | List timesheets |
| PATCH | `/api/v1/timesheets/{id}/submit` | `time:write` | Submit timesheet |
| PATCH | `/api/v1/timesheets/{id}/approve` | `time:approve` | Approve timesheet |

---

## Related

- [[modules/work-management/tasks/overview|Task Management]] — task_id FK
- [[modules/workforce-presence/overview|Workforce Presence]] — Discrepancy Engine feed
- [[database/schemas/wms-project-management|WMS Project Management Schema]] — time_logs section
- [[Userflow/Work-Management/time-tracking-flow.md|Time Tracking User Flow]]
- [[current-focus/DEV5-wms-foundation|DEV5 Task 4]]
