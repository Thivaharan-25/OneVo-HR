# Work Management (WMS) — Overview

**Area:** WorkSync / Work Management Pillar
**Trigger:** User navigates to any Workforce panel item (Projects, My Work, Planner, Goals, Docs, Timesheets, Analytics)  
**Required Permission:** `workforce:view` minimum; specific features gated by additional permission keys (see sidebar-nav.md)

## Purpose

ONEVO's Work Management System, branded as **WorkSync**, is the project and task management layer inside ONEVO. It is sold through Subscription Plans as a base module or optional add-on. It answers what teams are building through projects, chat, third-party integrations, and the IDE extension. When HR/Workforce Intelligence modules are also enabled, Work Management can be shown beside attendance, monitoring, productivity, and exception data.

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
| Task assignee | Must be an employee within the current company tenant scope unless a cross-company project grant explicitly allows a connected-company participant |
| Timesheet entry | Connects to Calendar → Attendance correction records |
| Overtime entry | Connects to Calendar → Overtime approval records |
| Resource capacity | Uses shift schedule data from Calendar → Schedules |
| Project team member | Must be an employee within the same company tenant scope unless an active company connection and scoped grant allow a connected-company participant |
| Productivity score | Surfaces on Workforce Presence card only when Workforce Intelligence is enabled |

## Data Scope

All WorkSync data is tenant-scoped. Workspaces, projects, tasks, goals, and docs remain legal-entity-local by default when a legal entity is selected. Cross-tenant collaboration requires an active company connection and explicit member/data-sharing scope; it must not be modeled as legal-entity switching inside one tenant.

Workspaces and projects use context-specific access:

- Position hierarchy resolves reporting authority and virtual reporting teams.
- Workspace membership controls workspace collaboration.
- Project membership controls project visibility and work.
- Project-workspace links show participation context and responsible workspace, but do not automatically expose the project to every workspace member.
- Cross-legal-entity participation requires request/approval; it does not grant reporting authority over another legal entity's employees.

Project dashboards are filtered by viewer context. Full project administration sees overall health. Legal-entity context sees only that entity contribution. Workspace context sees only that workspace contribution. Reporting managers see only their reports' contribution inside projects/workspaces they can access. Members see own work and published updates.

## Packaging Rules

- Work Management is sold through Subscription Plans as a base module or optional add-on.
- Related add-ons can include Project Management, Agentic Chat, Third Party Integrations, and IDE Extension.
- HR Core and Workforce Intelligence modules are separate plan-selected modules.
- The React frontend must hide disabled modules on every device size; route guards and backend APIs must enforce the same module entitlements server-side.
- There are no WorkManage Pro bridge endpoints. Do not call `/api/v1/bridges/*`.

## Related Flows

- [[Userflow/Work-Management/workspace-creation-flow|Workspace Creation]]
- [[Userflow/Work-Management/project-flow|Project Management]]
- [[Userflow/Work-Management/task-flow|Task Management]]
- [[Userflow/Work-Management/planning-flow|Planning — Sprints and Boards]]
- [[Userflow/Work-Management/goals-okr-flow|Goals and OKRs]]
- [[Userflow/Work-Management/time-tracking-flow|Time Tracking]]
- [[Userflow/Work-Management/resource-flow|Resource Management]]
- [[Userflow/Workforce-Presence/presence-overview|Workforce Presence]]
- [[Userflow/Chat/chat-overview|Chat]]

