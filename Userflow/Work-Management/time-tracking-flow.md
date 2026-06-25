# Worklogs

**Area:** Work -> Worklogs (`/work/worklogs`)
**Trigger:** User opens Worklogs from the Work panel, or logs time from within a work item.

## Purpose

Worklogs capture how long employees spend on work items. Phase 1 keeps this simple: logs are attached to work items and can roll up by project and employee. Advanced timesheets, capacity analytics, and report dashboards are Phase 2 unless explicitly enabled later.

## Key Entities

| Entity | Role |
|---|---|
| `TIME_LOG` | A single worklog entry: work item, user, duration, date |
| `TIMER_SESSION` | Optional active timer that creates a `TIME_LOG` when stopped |
| `TIMESHEET` | Phase 2 weekly summary of all time logs for a user |
| `TIMESHEET_ENTRY` | Phase 2 grouping of time logs under a timesheet period |
| `OVERTIME_ENTRY` | Hours exceeding scheduled shift; handled by Time & Attendance |
| `TIME_REPORT` | Phase 2 aggregated time report |

## Flow Steps

### Log Time Against a Work Item

1. From a work item detail, user clicks "Log Time" or starts a timer.
2. User stops the timer; system calculates duration and creates `TIME_LOG`.
3. Alternatively, user manually enters duration and date.
4. Time log appears in the work item time history and project worklog list.

### View Worklogs (`/work/worklogs`)

1. User opens Work -> Worklogs.
2. System loads worklogs visible to the user by project membership and permission.
3. Worklogs show date, work item, project, employee, and duration.
4. Totals can be grouped by day, project, employee, or work item.

### Overtime Connection

1. Time & Attendance owns overtime rules and overtime approval.
2. Worklogs may provide supporting evidence for overtime, but they do not replace attendance records.
3. Approved overtime entries feed payroll only when payroll integration is enabled.

### Attendance Correction Connection

1. If Time & Attendance finds a discrepancy, worklogs may be shown as supporting context.
2. Attendance correction remains a Time & Attendance workflow.

### Time Reports (Phase 2)

1. User with reporting permission opens Work -> Analytics or Work -> Reports when Phase 2 analytics is enabled.
2. Filters may include date range, employee, project, work item, and billable/non-billable.
3. System generates `TIME_REPORT`, exportable as CSV or PDF.

## Connection Points

| Connects to | How |
|---|---|
| Work -> Work Items | Time is logged directly from work item detail. |
| Work -> Projects | Project worklogs show effort by project. |
| Time & Attendance -> Attendance | Worklogs may support attendance correction review. |
| Time & Attendance -> Overtime | Worklogs may support overtime evidence, but overtime approval stays in Time & Attendance. |
| Work analytics (Phase 2) | Time data feeds productivity and capacity analytics only when enabled. |
| Inbox | Timesheet or overtime approval requests land in Inbox when those workflows are enabled. |

## Related Flows

- [[Userflow/Work-Management/wm-overview|WMS Overview]]
- [[Userflow/Work-Management/task-flow|Task Management]]
- [[Userflow/Work-Management/resource-flow|Resource Management (Phase 2)]]
- [[Userflow/Time-Attendance/shift-schedule-setup|Shift Schedule Setup]]
