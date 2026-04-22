# Task Management

**Area:** Workforce → My Work / Workforce → Projects → Board  
**Trigger:** User clicks "My Work" in Workforce panel, or opens a project board  
**Required Permission:** `tasks:read` (view); `tasks:write` (create/edit/assign)

## Purpose

Tasks are the atomic unit of work in the WMS. A task can be a feature, bug, issue, or any actionable item. Tasks live inside projects and support a full lifecycle: creation → assignment → work → submission → approval → close. Bugs are a specialised task type with additional reproduction steps and resolution tracking.

## Key Entities

| Entity | Role |
|---|---|
| `TASK` | Core work item — title, status, priority |
| `TASK_ASSIGNEE` | User-to-task assignment link |
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
1. User opens Workforce → My Work
2. System loads all tasks assigned to the current user across all projects in the entity scope
3. Tasks are grouped by project and filterable by status, priority, due date
4. User clicks a task to open its detail panel

### Create Task (from project board)
1. User opens a project board (`/workforce/projects/[id]/board`)
2. User clicks "+ Add Task" in a status column
3. User enters title, description, priority, due date, labels
4. System creates `TASK` record linked to the project
5. User optionally assigns the task to a project member — creates `TASK_ASSIGNEE` record

### Task Lifecycle
```
Open → In Progress → In Review → Approved → Closed
                              ↓
                           Rejected → In Progress (reopened)
```

1. **Open** — task created, not yet started
2. **In Progress** — assignee begins work, logs time against the task
3. **In Review** — assignee submits work: creates `TASK_SUBMISSION` + uploads `TASK_SUBMISSION_FILE`
4. **Approved** — reviewer creates `TASK_APPROVAL` with status "approved"; task moves to Closed
5. **Rejected** — reviewer rejects with comment; system creates `TASK_REOPEN_LOG`; task returns to In Progress

### Bug Tracking
1. User creates a task and marks it as type "Bug"
2. System creates `BUG_REPORT` linked to the task
3. User adds reproduction steps: `BUG_REPRODUCTION_STEP` records (numbered, action + expected result)
4. When fixed, user adds a `BUG_RESOLUTION` record: resolution type, resolver, timestamp
5. Bug severity (critical / high / medium / low) determines priority in the Inbox exception alerts

### Dependencies
1. From task detail, user clicks "Add Dependency"
2. User searches for another task and sets type: blocks / blocked-by / relates-to
3. System creates `TASK_DEPENDENCY` record
4. Blocked tasks are visually marked on the board with a dependency badge

## Connection Points

| Connects to | How |
|---|---|
| Workforce → Presence | Assignee's current task shows on their presence card |
| Workforce → Timesheets | Time logs are attached to tasks — flow into timesheets |
| Inbox | Task approvals, assignment notifications, and mentions land in Inbox |
| Workforce → Planner | Tasks are organised into sprints on the Planner board |

## Related Flows

- [[Userflow/Work-Management/wm-overview|WMS Overview]]
- [[Userflow/Work-Management/project-flow|Project Management]]
- [[Userflow/Work-Management/planning-flow|Planning — Sprints and Boards]]
- [[Userflow/Work-Management/time-tracking-flow|Time Tracking]]
