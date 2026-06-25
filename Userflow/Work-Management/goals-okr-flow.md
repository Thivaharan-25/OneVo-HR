# Goals and OKRs (Phase 2)

**Area:** Work -> Goals (`/work/goals`, Phase 2 only)
**Trigger:** Deferred Phase 2 only. Phase 1 must not expose Goals, OKR, objective, key result, or goal check-in navigation.
**Required Permission:** `okr:read` (view); `okr:write` (create/edit)

## Purpose

Goals and OKRs are a deferred Phase 2 design reference. Phase 1 Work supports Projects, Work Items, Documents, Project Members, Project Settings, and Worklogs only.

## Key Entities

| Entity | Role |
|---|---|
| `OBJECTIVE` | Strategic goal: title, owner, progress percentage |
| `KEY_RESULT` | Measurable outcome linked to an objective |
| `OKR_UPDATE` | A progress update on an objective or key result |
| `OKR_ALIGNMENT` | Parent-child alignment between objectives |
| `INITIATIVE` | A specific action or project contributing to a key result |
| `GOAL_CHECKIN` | Periodic progress check-in with commentary |

## Flow Steps

### View Goals (`/work/goals`, Phase 2)

1. User opens Work -> Goals.
2. Each objective shows title, owner, progress bar, key result count, and status.
3. User clicks an objective to open its detail.

### Create Objective

1. User clicks "+ Create" -> "New Objective".
2. User enters title, description, owner, and time period.
3. System creates `OBJECTIVE` with progress at 0%.

### Add Key Results to Objective

1. From objective detail (`/work/goals/[id]`), user clicks "Add Key Result".
2. User enters title, target value, unit, and start value.
3. System creates `KEY_RESULT` linked to the objective.

### Track Progress

1. User opens objective detail and clicks "Check In".
2. User updates the current value for one or more key results.
3. System creates `OKR_UPDATE` records and recalculates objective progress.
4. User may add a `GOAL_CHECKIN` note with commentary and `progress_delta`.

### OKR Alignment

1. User opens an objective and clicks "Align to Parent".
2. System creates `OKR_ALIGNMENT` with `contribution_weight`.
3. Parent objective progress is partially influenced by child objective progress.

### Link Initiative

1. From a key result, user clicks "Add Initiative".
2. User links an existing project or creates a new initiative title.
3. System creates `INITIATIVE` linked to the key result.

## Connection Points

| Connects to | How |
|---|---|
| Work -> Projects | An initiative under a key result can link to a WMS project. |
| Work analytics (Phase 2) | Objective progress contributes to productivity analytics when Phase 2 analytics is enabled. |
| Inbox | Check-in reminders and alignment requests land in Inbox. |
| People -> Employees | Objectives are owned by employees; profile links open employee detail. |

## Related Flows

- [[Userflow/Work-Management/wm-overview|WMS Overview]]
- [[Userflow/Work-Management/project-flow|Project Management]]
- [[Userflow/Work-Management/resource-flow|Resource Management (Phase 2)]]
