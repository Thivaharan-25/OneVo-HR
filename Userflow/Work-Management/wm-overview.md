# Work Management (WMS) — Overview

**Area:** WorkSync / Work Management Pillar
**Trigger:** User navigates to any Workforce panel item (Projects, My Work, Planner, Goals, Docs, Timesheets, Analytics)  
**Required Permission:** `workforce:view` minimum; specific features gated by additional permission keys (see sidebar-nav.md)

## Purpose

ONEVO's Work Management System, branded as **WorkSync**, is the project and task management layer inside ONEVO. It can be sold independently from HR Management, or combined with HR and Workforce Intelligence in one tenant. It answers what teams are building through Projects, Tasks, Goals, Time, Chat, Docs, and Analytics. When Workforce Intelligence is also enabled, WorkSync can be shown beside presence/productivity data; when it is sold alone, it runs without monitoring.

## Ownership

| Layer | Owner |
|---|---|
| WorkSync Frontend (UI, routing, state) | ONEVO team |
| WorkSync Backend (API, business logic, data) | ONEVO backend |
| HR to WorkSync Integration | Internal module services, direct FKs, domain events |

## Module Map

| WorkSync Module | ONEVO Route | Backend Key |
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

| WorkSync Concept | ONEVO HR Connection |
|---|---|
| WorkSync User | Maps to ONEVO User and optional Employee identity. WorkSync-only tenants still create a minimal CoreHR identity anchor, but HR pages remain hidden unless entitled. |
| Task assignee | Must be an employee within the current legal entity scope |
| Timesheet entry | Connects to Calendar → Attendance correction records |
| Overtime entry | Connects to Calendar → Overtime approval records |
| Resource capacity | Uses shift schedule data from Calendar → Schedules |
| Project team member | Must be an employee within the same entity scope |
| Productivity score | Surfaces on Workforce Presence card only when Workforce Intelligence is enabled |

## Data Scope

All WorkSync data is tenant-scoped and, when legal entities are enabled, scoped to the selected legal entity/workspace. Switching legal entity or workspace changes which projects, tasks, goals, and docs are visible.

## Packaging Rules

- WorkSync can be sold without HR Management.
- HR Management can be sold without WorkSync.
- Individual WorkSync modules can be enabled separately, such as Projects + Tasks only, Chat only, or Time + Reports only.
- The React frontend must hide disabled modules on every device size; route guards and backend APIs must enforce the same module entitlements server-side.
- There are no WorkManage Pro bridge endpoints. Do not call `/api/v1/bridges/*`.

## Related Flows

- [[Userflow/Work-Management/project-flow|Project Management]]
- [[Userflow/Work-Management/task-flow|Task Management]]
- [[Userflow/Work-Management/planning-flow|Planning — Sprints and Boards]]
- [[Userflow/Work-Management/goals-okr-flow|Goals and OKRs]]
- [[Userflow/Work-Management/time-tracking-flow|Time Tracking]]
- [[Userflow/Work-Management/resource-flow|Resource Management]]
- [[Userflow/Workforce-Presence/presence-overview|Workforce Presence]]
- [[Userflow/Chat/chat-overview|Chat]]
