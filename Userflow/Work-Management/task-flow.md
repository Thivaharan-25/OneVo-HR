# Task Management

**Area:** Workforce -> My Work / Workforce -> Projects -> Board
**Trigger:** User clicks "My Work" in Workforce panel, or opens a project board
**Required Permission:** `tasks:read` (view); `tasks:write` (create/edit/assign)

## Purpose

Tasks are the atomic unit of work in the WMS. A task can be a feature, bug, issue, or any actionable item. Tasks live inside projects and support a full lifecycle: creation -> assignment -> work -> submission -> approval -> close. Bugs are a specialised task type with additional reproduction steps and resolution tracking.

Assignments are employee-backed in Phase 1. The system stores both `user_id` and `employee_id` so Work Management can respect HR status, department/team reporting, offboarding, leave, and calendar conflicts.

Task assignment authority is bound to the project/workspace context. A reporting manager's hierarchy over an employee does not allow task assignment in another manager's workspace unless the actor also has local project/workspace authority there.

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

### View My Work (`/workforce/my-work`)

1. User opens Workforce -> My Work.
2. System loads all tasks assigned to the current employee across all projects in the current company tenant scope.
3. Tasks are grouped by project and filterable by status, priority, due date.
4. User clicks a task to open its detail panel.

### Create Task (from project board)

1. User opens a project board (`/workforce/projects/[id]/board`).
2. User clicks "+ Add Task" in a status column.
3. User selects responsible workspace if the project has more than one linked workspace. The selected workspace must be active in `PROJECT_WORKSPACE`.
4. User enters title, description, priority, due date, labels.
5. System validates the actor has `tasks:write`, project access, and task authority in the selected workspace/project context.
6. System creates `TASK` record linked to the project and responsible workspace.
7. User optionally assigns the task to an allowed assignee.
8. Assignee picker returns only employees who are active project members, selected workspace participants, or approved scoped participants for this project.
9. If the actor is relying on reporting-manager authority, the assignee must be below the actor in the position hierarchy and the actor must control this workspace/project context.
10. System resolves the selected user's `employee_id`, validates active employment, checks approved leave/calendar conflicts, and creates `TASK_ASSIGNEE`.
11. If the employee is on leave or has a calendar conflict, the UI shows the warning from `availability_status`/`availability_warning`; tenant policy may block the assignment.

### Assignment Examples

| Scenario | Result |
|:---------|:-------|
| User manages a workspace created from their reporting team and assigns a task to their report inside that workspace | Allowed when `tasks:write` and local workspace/project authority are present. |
| User is a member, not lead/admin, in another manager's workspace and tries to assign a task to their own report there | Blocked unless they have local task authority in that workspace/project. |
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
| Workforce -> Presence | Assignee's current task shows on their presence card |
| Workforce -> Timesheets | Time logs are attached to tasks and flow into timesheets |
| Leave + Calendar | Assignment warns or blocks when the employee is on approved leave or has a calendar conflict |
| Inbox | Task approvals, assignment notifications, and mentions land in Inbox |
| Workforce -> Planner | Tasks are organised into sprints on the Planner board |

## Related Flows

- [[Userflow/Work-Management/wm-overview|WMS Overview]]
- [[Userflow/Work-Management/project-flow|Project Management]]
- [[Userflow/Work-Management/planning-flow|Planning - Sprints and Boards]]
- [[Userflow/Work-Management/time-tracking-flow|Time Tracking]]
