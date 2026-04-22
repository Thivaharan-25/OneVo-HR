# Resource Management

**Area:** Workforce → Analytics (`/workforce/analytics`)  
**Trigger:** User clicks "Analytics" in the Workforce panel; resource data also surfaces within project detail  
**Required Permission:** `analytics:read` (view); `analytics:write` (manage allocations)

## Purpose

Resource management answers: who is available, at what capacity, and with which skills — so that project work can be planned and allocated without overloading employees. It connects workforce scheduling (Calendar → Schedules) with WMS project planning (Projects, Sprints).

## Key Entities

| Entity | Role |
|---|---|
| `SKILL` | A named capability defined at the workspace level |
| `USER_SKILL` | An employee's skill record with proficiency level |
| `RESOURCE_PLAN` | An employee's allocation to a project (percentage) |
| `CAPACITY_SNAPSHOT` | Weekly utilisation percentage per employee |
| `SKILL_REQUIREMENT` | Skills needed for a project (headcount + level) |
| `RESOURCE_ALLOCATION_LOG` | History of allocation changes |

## Flow Steps

### View Capacity (`/workforce/analytics`)
1. User opens Workforce → Analytics
2. System loads capacity snapshots for all employees in the entity scope
3. Capacity view shows: employee name, current allocation %, available hours, scheduled hours
4. Employees above 100% utilisation are highlighted as overallocated
5. Data is sourced from `CAPACITY_SNAPSHOT` records (weekly snapshots)

### Allocate Employee to Project
1. From a project detail or the Analytics page, user clicks "Allocate Resource"
2. User selects an employee and sets allocation percentage (e.g., 50%)
3. System creates `RESOURCE_PLAN` record
4. Employee's capacity snapshot is updated on the next weekly calculation
5. Allocation history logged in `RESOURCE_ALLOCATION_LOG`

### Skill Matching
1. Project lead defines `SKILL_REQUIREMENT` records: skill, required proficiency, headcount needed
2. User opens the "Find Resources" view — system matches employees with `USER_SKILL` records meeting the requirement
3. User reviews the matched list and allocates selected employees to the project

### Employee Skills
1. Employee skills are managed in their People profile (Employee detail → Skills section)
2. HR admin or manager adds `USER_SKILL` records: skill name, proficiency level, verification date
3. Skills defined at the workspace level via Admin or the Org → Job Families structure

## Connection Points

| Connects to | How |
|---|---|
| Workforce → Projects | Resource allocations are linked to projects — visible in project member list |
| Workforce → Planner | Sprint planning references capacity to avoid overallocation |
| Calendar → Schedules | Scheduled shift hours determine available capacity |
| People → Employees | Employee skills and profile link from the resource view |
| Workforce → Timesheets | Actual time logged feeds into real utilisation vs planned |
| Org → Job Families | Job family defines expected skills for role groups |

## Related Flows

- [[Userflow/Work-Management/wm-overview|WMS Overview]]
- [[Userflow/Work-Management/project-flow|Project Management]]
- [[Userflow/Work-Management/time-tracking-flow|Time Tracking]]
- [[Userflow/Workforce-Presence/presence-overview|Workforce Presence]]
