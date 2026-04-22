# Time Tracking

**Area:** Workforce → Timesheets (`/workforce/time`)  
**Trigger:** User clicks "Timesheets" in the Workforce panel, or logs time from within a task  
**Required Permission:** `time:read` (view own); `time:read:team` (view team); `time:write` (log time)

## Purpose

Time tracking captures how long employees spend on tasks. Time logs roll up into weekly timesheets for approval and connect directly to the HR modules: Attendance (corrections feed from timesheets) and Overtime (excess hours logged here become Overtime entries in Calendar → Overtime).

## Key Entities

| Entity | Role |
|---|---|
| `TIME_LOG` | A single time entry — task, user, duration, date |
| `TIMER_SESSION` | An active running timer (start → stop → creates TIME_LOG) |
| `TIMESHEET` | Weekly summary of all time logs for a user |
| `TIMESHEET_ENTRY` | A time log grouped under a timesheet period |
| `OVERTIME_ENTRY` | Hours exceeding the scheduled shift — requires approval |
| `BILLABLE_RATE` | User/project rate for billable time |
| `TIME_REPORT` | Aggregated time report by project, user, or period |

## Flow Steps

### Log Time Against a Task
1. From a task detail, user clicks "Log Time" or starts the timer (creates `TIMER_SESSION`)
2. User stops the timer — system calculates duration and creates `TIME_LOG`
3. Alternatively, user manually enters duration and date without a timer
4. Time log appears in the task's time history and rolls into the current week's `TIMESHEET`

### View Timesheet (`/workforce/time`)
1. User opens Workforce → Timesheets
2. System loads the current week's `TIMESHEET` for the user
3. Timesheet shows: date, task name, project, duration — grouped by day
4. Total hours per day compared against scheduled shift hours from Calendar → Schedules
5. Hours exceeding the daily schedule are flagged as potential overtime

### Submit Timesheet for Approval
1. User reviews the week's entries and clicks "Submit"
2. Timesheet status changes from "draft" to "submitted"
3. Manager receives an Inbox notification to approve or return for correction
4. On approval, timesheet status changes to "approved"

### Overtime Creation (automatic)
1. When a timesheet is approved and total daily hours exceed the scheduled shift, system automatically creates an `OVERTIME_ENTRY`
2. The `OVERTIME_ENTRY` appears in Calendar → Overtime for the manager to formally approve
3. Approved overtime entries feed into payroll (Phase 2)

### Attendance Correction Connection
1. If an employee's attendance record in Calendar → Attendance shows a discrepancy with their `TIME_LOG` entries, an attendance correction request is created
2. The correction adjusts the attendance record to match actual logged time

### Time Reports (`/workforce/time/reports`)
1. User with `time:read:team` permission opens time reports
2. Filters: date range, employee, project, task, billable / non-billable
3. System generates `TIME_REPORT` — exportable as CSV or PDF

## Connection Points

| Connects to | How |
|---|---|
| Workforce → Tasks | Time is logged directly from task detail |
| Calendar → Attendance | Timesheet entries reconcile with attendance records |
| Calendar → Overtime | Excess hours from approved timesheets create overtime entries |
| Calendar → Schedules | Scheduled shift hours are the baseline for overtime calculation |
| Workforce → Analytics | Time data feeds productivity and capacity analytics |
| Inbox | Timesheet approval requests land in Inbox |

## Related Flows

- [[Userflow/Work-Management/wm-overview|WMS Overview]]
- [[Userflow/Work-Management/task-flow|Task Management]]
- [[Userflow/Work-Management/resource-flow|Resource Management]]
- [[Userflow/Workforce-Presence/shift-schedule-setup|Shift Schedule Setup]]
