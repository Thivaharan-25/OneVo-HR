# Work - Overview

**Area:** Work
**Phase:** 1 with Phase 2 design references retained

> **Implementation guardrail:** For Phase 1 implementation, only build: Workspaces, Projects, Project members/invitations, Work items, Kanban/List/Calendar views, Worklogs, Simple project docs/pages if enabled. Do not build Phase 2 areas unless explicitly requested: Planner/sprints/roadmaps, Goals/OKR, Advanced resource planning, Chat/AI chat, Repository automation, Workspace source pools, Multi-workspace project participation.
**Customer Navigation:** Work

---

## Phase 1 Scope

Work Phase 1 is a simple project and work-item area inside the same ONEVO customer app. It is not a separate workspace product and it is not an external system.

Active Phase 1 Work includes:

- workspaces
- projects
- work items
- basic project membership
- simple project settings
- worklogs
- simple docs/pages if retained for project context

Do not expose Planner, Goals/OKR, broad resource planning, advanced roadmap, Chat AI, workspace-heavy planning, or automation-rule builders as active Phase 1 Work screens.

Canonical Phase 1 Work rules:

- A tenant can create multiple workspaces.
- Each project belongs to exactly one workspace.
- Each project has Kanban, List, and Calendar views for work items.
- Project/workspace admins invite members directly to a project; the selected member accepts or declines.
- Simple project-link invitations between project admins are allowed and create project-link records when accepted.
- Workspace linking, linked workspace source pools, owner-to-owner participation governance, and advanced project-link/dependency platforms are Phase 2.

---

## Purpose

Work is the project and task management layer inside ONEVO. It is sold through subscription plans as a base module or optional add-on. It answers what teams are building through projects and work items.

When HR and Monitoring modules are also enabled, Work can be shown beside attendance, monitoring, productivity, and alert data. It still uses the same backend, same database, and same customer app shell.

---

## Ownership

| Layer | Owner |
|---|---|
| Work frontend surfaces | ONEVO customer app |
| Work backend API and business logic | ONEVO backend |
| HR to Work integration | Internal module services, direct FKs, domain events |

---

## Active Phase 1 Module Map

| Work Area | ONEVO Route | Backend Key |
|---|---|---|
| Workspaces | `/work/workspaces` | workspace |
| Projects | `/work/projects` | project |
| Work Items | `/work/items`, `/work/projects/{id}/items` | task; simple Kanban/List/Calendar views |
| Worklogs | `/work/worklogs`, embedded in work items | time |
| Simple Docs/Pages | `/work/documents`, `/work/projects/{id}/documents` where retained | collab |
| Project Members | embedded in project detail/settings | project_members |
| Project Settings | embedded in project detail/settings | project_settings |

## Deferred Phase 2 Module Map

| Deferred Area | Status |
|---|---|
| Planner / sprints / boards / roadmap | Phase 2 |
| Goals / OKR | Phase 2 |
| Advanced resource planning | Phase 2 |
| Workspace-heavy collaboration | Phase 2 |
| Chat / Chat AI | Phase 2 |
| Repository automation rules | Phase 2 |
| Microsoft Teams workspace/chat sync | Phase 2 unless separately reactivated |

---

## Add Employee vs Add Member

**Add Employee** belongs to People. It creates a new employee record in the company.

**Add Member** belongs to Work. It adds an existing employee to a project or work membership context. It must not create a new employee record.

---

## Integration Points With HR

| Work Concept | ONEVO HR Connection |
|---|---|
| Work user | Maps to ONEVO user and optional employee identity |
| Work item assignee | Must be an existing employee/user within the allowed company/project context |
| Worklog | Can connect to Time & Attendance and payroll/analytics where needed |
| Project member | Existing employee added to project context; not a new employee |
| Productivity context | Can surface only when Monitoring is enabled and permission allows it |

---

## Data Scope

All Work data is tenant-scoped. Projects and work items remain inside the current tenant/company context unless a future connected-company feature explicitly allows controlled participation.

Project membership controls project visibility and work. Position-derived employee visibility does not automatically grant project membership.

Projects inherit their workspace from the selected workspace context. Phase 1 does not use linked workspace source pools or owner-to-owner workspace participation requests.

Project dashboards are filtered by viewer context:

| Viewer context | Show |
|---|---|
| Project admin | Overall project health, members, settings, work items, worklogs |
| Project member | Own and assigned work, visible comments/checklists, published updates |
| Viewer/stakeholder | Published summary only |

Broader workspace/legal-entity/team contribution reporting from older WorkSync planning remains Phase 2 reference only.

---

## Packaging Rules

- Work is sold through Subscription Plans as a base module or optional add-on.
- Related add-ons can include Project Management, Third Party Integrations, and IDE Extension in later phases.
- HR Core and Monitoring modules are separate plan-selected modules.
- The frontend must hide disabled modules; route guards and backend APIs must enforce entitlements server-side.
- There are no WorkManage Pro bridge endpoints. Do not call `/api/v1/bridges/*`.

---

## Related Active Phase 1 Flows

- [[Userflow/Work-Management/project-flow|Project Management]]
- [[Userflow/Work-Management/task-flow|Work Item Management]]
- [[Userflow/Work-Management/time-tracking-flow|Worklogs]]
- [[Userflow/Work-Management/collaboration-flow|Simple Docs/Pages]]

## Deferred Phase 2 References

- [[Userflow/Work-Management/planning-flow|Planning / Planner]]
- [[Userflow/Work-Management/goals-okr-flow|Goals and OKRs]]
- [[Userflow/Work-Management/resource-flow|Resource Management]]
- [[Userflow/Work-Management/my-space-flow|My Space]]
- [[Userflow/Work-Management/chat-ai-flow|Chat AI]]
- [[Userflow/Work-Management/integration-automation-flow|Integration Automation]]
- [[Userflow/Work-Management/workspace-teams-sync|Workspace Teams Sync]]
