# Resource Management (Phase 2)

**Area:** Work -> Analytics (`/work/analytics`, Phase 2 only)
**Trigger:** Deferred Phase 2 only. Phase 1 Work must not expose a top-level resource analytics route.
**Required Permission:** `analytics:read` (view); `analytics:write` (manage allocations)

## Purpose

Resource management answers who is available, at what capacity, and with which skills so project work can be planned without overloading employees. It connects Time & Attendance schedules with WMS project planning. This is Phase 2 unless a small capacity signal is embedded inside a simple Phase 1 project member view.

## Key Entities

| Entity | Role |
|---|---|
| `SKILL` | A named capability defined at the workspace level |
| `USER_SKILL` | An employee skill record with proficiency level |
| `RESOURCE_PLAN` | An employee allocation to a project |
| `CAPACITY_SNAPSHOT` | Weekly utilisation percentage per employee |
| `SKILL_REQUIREMENT` | Skills needed for a project |
| `RESOURCE_ALLOCATION_LOG` | History of allocation changes |

## Flow Steps

### View Capacity (`/work/analytics`, Phase 2)

1. User opens Work -> Analytics.
2. System loads capacity snapshots for employees in scope.
3. Capacity view shows employee name, current allocation percent, available hours, and scheduled hours.
4. Employees above 100% utilisation are highlighted as overallocated.

### Allocate Employee to Project

1. From a project detail or analytics page, user clicks "Allocate Resource".
2. User selects an employee and sets allocation percentage.
3. System creates `RESOURCE_PLAN`.
4. Employee capacity snapshots update on the next calculation.
5. Allocation history is logged in `RESOURCE_ALLOCATION_LOG`.

### Skill Matching

1. Project lead defines `SKILL_REQUIREMENT` records.
2. User opens "Find Resources"; system matches employees with `USER_SKILL` records.
3. User reviews the matched list and allocates selected employees to the project.

### Employee Skills

1. Employee skills are managed in the People employee detail page.
2. HR admin or manager adds `USER_SKILL` records with skill name, proficiency level, and verification date.

## Connection Points

| Connects to | How |
|---|---|
| Work -> Projects | Resource allocations are linked to projects and visible in project member context. |
| Work -> Planner (Phase 2) | Sprint planning references capacity to avoid overallocation. |
| Time & Attendance -> Schedules | Scheduled work hours determine available capacity. |
| People -> Employees | Employee skills and profile links come from employee detail. |
| Work -> Worklogs | Actual time logged feeds into utilisation reporting when Phase 2 analytics is enabled. |

## Related Flows

- [[Userflow/Work-Management/wm-overview|WMS Overview]]
- [[Userflow/Work-Management/project-flow|Project Management]]
- [[Userflow/Work-Management/time-tracking-flow|Time Tracking]]
- [[Userflow/Time-Attendance/presence-overview|Time & Attendance]]
