# Task Management

**Area:** Work -> Work Items / Work -> Projects -> Items
**Trigger:** User clicks "Work Items" in the Work panel, or opens a project Kanban/List/Calendar view
**Required Permission:** `tasks:read` (view); `tasks:write` (create/edit/assign)

## Purpose

Tasks are the atomic unit of work in the WMS. A task can be a feature, bug, issue, or any actionable item. Tasks live inside projects and support a full lifecycle: creation -> assignment -> work -> submission -> approval -> close. Bugs are a specialised task type with additional reproduction steps and resolution tracking.


Task assignment authority is bound to the project context. The task's workspace context is inherited from the owning project. Reporting-manager relationship does not grant task assignment rights; assignment requires local project authority and an active accepted project member assignee.

## Key Entities

| Entity | Role |
|---|---|
| `TASK` | Core work item: title, status, priority |
| `TASK_ASSIGNEE` | Employee-backed user-to-task assignment link with availability status |
| `CHECKLIST_ITEM` | Sub-steps within a task |
| `TASK_DEPENDENCY` | Blocks / blocked-by relationships |
| `LABEL` + `TASK_LABEL` | Tag system for filtering |
| `TASK_SUBMISSION` + `TASK_SUBMISSION_FILE` | Work submitted for review |
| `TASK_APPROVAL` | Approval request linked to a submission |
| `TASK_REOPEN_LOG` | Audit trail when a closed task is reopened |
| `BUG_REPORT` | Bug-specific task with severity and reproduction steps |
| `BUG_REPRODUCTION_STEP` | Numbered steps to reproduce the bug |
| `BUG_RESOLUTION` | Resolution type and who resolved it |

## Flow Steps

### View My Work (`/work/items`)

1. User opens Work -> Work Items.
2. System loads all tasks assigned to the current employee across all projects in the current company tenant scope.
3. Tasks are grouped by project and filterable by status, priority, due date.
4. User clicks a task to open its detail panel.

### Create Task (from project view)

1. User opens a project Kanban, List, or Calendar view (`/work/projects/[id]/items`).
2. User clicks "+ Add Task" in a status column.
3. User enters title, description, priority, due date, labels.
4. System validates the actor has `tasks:write`, project access, and task authority in the project context.
5. System creates `TASK` record linked to the project and inherited project workspace.
6. User optionally assigns the task to an allowed assignee.
7. Assignee picker returns only active accepted project members.
8. System resolves the selected user's `employee_id`, validates active employment, checks approved time off/calendar conflicts, and creates `TASK_ASSIGNEE`.
9. If the employee is on time off or has a calendar conflict, the UI shows the warning from `availability_status`/`availability_warning`; tenant policy may block the assignment.

### Assignment Examples

| Scenario | Result |
|:---------|:-------|
| User is a member, not lead/admin, in another manager's project and tries to assign a task to their own report there | Blocked unless they have local task authority in that project. |
| User has local project administration authority and assigns a task to an approved project member from another department | Allowed by project context, subject to project policy and availability checks. |
| User has `tasks:write` but is not a project member and has no approved project grant | Blocked. |

### Task Lifecycle

```text
Open -> In Progress -> In Review -> Approved -> Closed
                              |
                           Rejected -> In Progress (reopened)
```

1. **Open**: task created, not yet started.
2. **In Progress**: assignee begins work, logs time against the task.
3. **In Review**: assignee submits work and uploads evidence.
4. **Approved**: reviewer creates `TASK_APPROVAL` with status `approved`; task moves to Closed.
5. **Rejected**: reviewer rejects with comment; system creates `TASK_REOPEN_LOG`; task returns to In Progress.

### Bug Tracking

1. User creates a task and marks it as type "Bug".
2. System creates `BUG_REPORT` linked to the task.
3. User adds reproduction steps: `BUG_REPRODUCTION_STEP` records.
4. When fixed, user adds a `BUG_RESOLUTION` record.
5. Bug severity determines priority in the Inbox exception alerts.

### Dependencies

1. From task detail, user clicks "Add Dependency".
2. User searches for another task and sets type: blocks / blocked-by / relates-to.
3. System creates `TASK_DEPENDENCY` record.
4. Blocked tasks are visually marked on the board with a dependency badge.

## Connection Points

| Connects to | How |
|---|---|
| Monitoring -> Live Status | Assignee's current task may show on their presence card when enabled |
| Work -> Worklogs | Time logs are attached to tasks and flow into worklogs |
| Time Off + Calendar | Assignment warns or blocks when the employee is on approved time off or has a calendar conflict |
| Inbox | Task approvals, assignment notifications, and mentions land in Inbox |
| Work -> Planner (Phase 2) | Tasks may be organised into sprints when Phase 2 planning is enabled |

## Related Flows

- [[Userflow/Work-Management/wm-overview|WMS Overview]]
- [[Userflow/Work-Management/project-flow|Project Management]]
- [[Userflow/Work-Management/planning-flow|Planning - Sprints and Boards]]
- [[Userflow/Work-Management/time-tracking-flow|Time Tracking]]
