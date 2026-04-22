# Work Management (WMS) — Overview

**Area:** Workforce Pillar  
**Trigger:** User navigates to any Workforce panel item (Projects, My Work, Planner, Goals, Docs, Timesheets, Analytics)  
**Required Permission:** `workforce:read` minimum; specific features gated by additional permission keys (see sidebar-nav.md)

## Purpose

ONEVO's Work Management System (WMS) is the project and task management layer built on top of workforce data. It answers two questions together: who is working (Presence), and what are they working on (Projects, Tasks, Goals, Time). All WMS screens live under the Workforce pillar.

## Ownership

| Layer | Owner |
|---|---|
| WMS Frontend (UI, routing, state) | ONEVO team |
| WMS Backend (API, business logic, data) | WMS backend team |
| HR ↔ WMS Integration | ONEVO team |

## Module Map

| WMS Module | ONEVO Route | Backend Key |
|---|---|---|
| Project | `/workforce/projects` | project |
| Task (issues, bugs) | `/workforce/my-work`, `/workforce/projects/[id]/board` | task |
| Planning (sprints, boards, roadmap) | `/workforce/planner` | planning |
| Goals / OKR | `/workforce/goals` | okr |
| Collaboration — Docs + Wiki | `/workforce/docs` | collab |
| Collaboration — Comments, reactions | Embedded inside tasks + docs | collab |
| Time (logs, timesheets) | `/workforce/time` | time |
| Resource (capacity, skills) | `/workforce/analytics` | resource |
| Chat | `/chat` | chat |

## Integration Points with ONEVO HR

| WMS Concept | ONEVO HR Connection |
|---|---|
| WMS User | Maps to ONEVO Employee — profile at `/people/employees/[id]` |
| Task assignee | Must be an employee within the current legal entity scope |
| Timesheet entry | Connects to Calendar → Attendance correction records |
| Overtime entry | Connects to Calendar → Overtime approval records |
| Resource capacity | Uses shift schedule data from Calendar → Schedules |
| Project team member | Must be an employee within the same entity scope |
| Productivity score | Surfaces on Workforce Presence card for each employee |

## Data Scope

All WMS data is scoped to the legal entity selected in the topbar. Switching legal entity changes which projects, tasks, goals, and docs are visible.

## Related Flows

- [[Userflow/Work-Management/project-flow|Project Management]]
- [[Userflow/Work-Management/task-flow|Task Management]]
- [[Userflow/Work-Management/planning-flow|Planning — Sprints and Boards]]
- [[Userflow/Work-Management/goals-okr-flow|Goals and OKRs]]
- [[Userflow/Work-Management/time-tracking-flow|Time Tracking]]
- [[Userflow/Work-Management/resource-flow|Resource Management]]
- [[Userflow/Workforce-Presence/presence-overview|Workforce Presence]]
- [[Userflow/Chat/chat-overview|Chat]]
