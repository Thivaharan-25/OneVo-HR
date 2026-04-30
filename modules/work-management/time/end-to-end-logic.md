# Time Management — End-to-End Logic

**Module:** WorkSync
**Feature:** Time Management

---

## Manual Time Log

```
POST /api/v1/tasks/{id}/time-logs
  body: { logged_date, duration_minutes, description }
  → CreateTimeLogHandler
    → 1. Verify task exists and user has workspace access
    → 2. Validate: duration_minutes > 0, logged_date <= today
    → 3. INSERT time_logs:
             task_id, user_id, workspace_id, tenant_id
             logged_date, duration_minutes, description
             source = "manual"
    → 4. Publish TimeLoggedEvent (aggregation trigger)
    → Return Result<TimeLogDto>
  → 201 Created
```

## Timer Start / Stop

```
POST /api/v1/me/timer/start
  body: { task_id }
  → StartTimerHandler
    → 1. Check: SELECT COUNT(*) FROM time_logs
                WHERE user_id = ? AND ended_at IS NULL
         If > 0: return 409 ACTIVE_TIMER_EXISTS
    → 2. INSERT time_logs:
             task_id, user_id, source = "timer"
             started_at = now(), ended_at = null, duration_minutes = 0
    → Return Result<TimerDto>

PATCH /api/v1/me/timer/stop
  → StopTimerHandler
    → 1. Load time_log WHERE user_id = ? AND ended_at IS NULL
         If not found: return 404 NO_ACTIVE_TIMER
    → 2. duration_minutes = CEIL((now() - started_at) / 60)
    → 3. UPDATE time_logs: ended_at = now(), duration_minutes = calculated
    → 4. Publish TimeLoggedEvent
    → Return Result<TimeLogDto>
```

## IDE Tag: @time:log 2h

```
Handled by IDE Tag Engine (see modules/ide-extension/overview)
  → Creates time_log row with source = "ide_tag"
  → duration_minutes calculated from tag param (e.g. "2h" → 120)
  → Links to tag_execution_id in ide_tag_executions for undo
  → If undo: DELETE time_log row within 30s window
```

## Timesheet Submit → Approve

```
PATCH /api/v1/timesheets/{id}/submit
  → SubmitTimesheetHandler
    → 1. Verify timesheet status = "draft" and belongs to caller
    → 2. Aggregate time_logs for period into timesheet_entries
    → 3. UPDATE timesheets.status = "submitted", submitted_at = now()
    → 4. Publish TimesheetSubmittedEvent → notify approver

PATCH /api/v1/timesheets/{id}/approve
  → [RequirePermission("time:approve")]
  → ApproveTimesheetHandler
    → 1. UPDATE timesheets.status = "approved", approved_by_id = caller
    → 2. Publish TimesheetApprovedEvent
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Timer already running | 409 | You have an active timer — stop it first |
| Stop with no active timer | 404 | No active timer found |
| Log for future date | 422 | Cannot log time for a future date |
| Modify submitted timesheet | 422 | Timesheet is locked after submission |

## Related

- [[modules/work-management/time/overview|Time Overview]]
- [[modules/work-management/time/testing|Time Testing]]
