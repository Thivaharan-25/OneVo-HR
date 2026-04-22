# Goals and OKRs

**Area:** Workforce → Goals (`/workforce/goals`)  
**Trigger:** User clicks "Goals" in the Workforce panel  
**Required Permission:** `goals:read` (view); `goals:write` (create/edit)

## Purpose

Goals are the strategic layer above projects and tasks. An Objective defines a qualitative target. Key Results are measurable outcomes that determine if the Objective was achieved. Goals are scoped to the legal entity and can be aligned across teams.

## Key Entities

| Entity | Role |
|---|---|
| `OBJECTIVE` | Strategic goal — title, owner, progress percentage |
| `KEY_RESULT` | Measurable outcome linked to an objective |
| `OKR_UPDATE` | A progress update on an objective or key result |
| `OKR_ALIGNMENT` | Parent-child alignment between objectives |
| `INITIATIVE` | A specific action or project contributing to a key result |
| `GOAL_CHECKIN` | Periodic progress check-in with commentary |

## Flow Steps

### View Goals (`/workforce/goals`)
1. User opens Workforce → Goals
2. System loads all objectives in the entity scope, grouped by owner or team
3. Each objective shows: title, owner, progress bar, count of key results, status
4. User clicks an objective to open its detail

### Create Objective
1. User clicks "+ Create" → "New Objective"
2. User enters: title, description, owner (employee), time period (quarterly / annual)
3. System creates `OBJECTIVE` record with progress at 0%

### Add Key Results to Objective
1. From objective detail (`/workforce/goals/[id]`), user clicks "Add Key Result"
2. User enters: title, target value (numeric), unit, start value
3. System creates `KEY_RESULT` linked to the objective

### Track Progress (Check-in)
1. User opens objective detail and clicks "Check In"
2. User updates the current value for one or more key results
3. System creates `OKR_UPDATE` records and recalculates objective progress
4. User optionally adds a `GOAL_CHECKIN` note with commentary and `progress_delta`

### OKR Alignment
1. User opens an objective and clicks "Align to Parent"
2. User selects a parent objective (team or company level)
3. System creates `OKR_ALIGNMENT` record with `contribution_weight`
4. Parent objective progress is partially influenced by child objective progress

### Link Initiative
1. From a key result, user clicks "Add Initiative"
2. User links an existing project or creates a new initiative title
3. System creates `INITIATIVE` record linked to the key result

## Connection Points

| Connects to | How |
|---|---|
| Workforce → Projects | An initiative under a key result can link to a WMS project |
| Workforce → Analytics | Objective progress contributes to workforce productivity analytics |
| Inbox | Check-in reminders and alignment requests land in Inbox |
| People → Employees | Objectives are owned by employees — profile link on objective detail |

## Related Flows

- [[Userflow/Work-Management/wm-overview|WMS Overview]]
- [[Userflow/Work-Management/project-flow|Project Management]]
- [[Userflow/Work-Management/resource-flow|Resource Management]]
