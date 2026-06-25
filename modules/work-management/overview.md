# Module Family: Work

**Pillar:** 3 - Work
**Phase:** 1 with Phase 2 design references retained
**Solution namespace:** `ONEVO.Modules.WorkSync.*`
**Database:** Same `ApplicationDbContext` as all other ONEVO modules. No separate database and no bridge APIs.

---

## Phase 1 Boundary

Work Phase 1 is intentionally simple. Active customer-facing Work includes:

- workspaces
- projects
- work items
- basic project membership
- simple project settings
- worklogs
- simple docs/pages if retained for project context

Do not expose Planner, Goals/OKR, advanced roadmap, broad resource planning, Chat AI, workspace-heavy planning, repository automation rules, or workflow-style automation builders as active Phase 1 screens.

Canonical Phase 1 Work rules:

- A tenant can create multiple workspaces.
- Each project belongs to exactly one workspace.
- Each project has simple Kanban, List, and Calendar work-item views.
- Project/workspace admins invite members directly to a project; the selected member accepts or declines.
- Simple project-link invitations between project admins are allowed and create project-link records when accepted.
- Workspace linking, linked workspace source pools, owner-to-owner participation governance, and advanced project-link/dependency platforms are Phase 2.

The detailed module references below are kept so Phase 2 design is not lost. Phase 2 rows must not be treated as current implementation requirements.

> **Implementation guardrail:** For Phase 1 implementation, only build: Workspaces, Projects, Project members/invitations, Work items, Kanban/List/Calendar views, Worklogs, Simple project docs/pages if enabled. Do not build Phase 2 areas unless explicitly requested: Planner/sprints/roadmaps, Goals/OKR, Advanced resource planning, Chat/AI chat, Repository automation, Workspace source pools, Multi-workspace project participation.

---

## Overview

Work is ONEVO's internal work management pillar. It is not an external system. All Work tables live in the same EF Core `ApplicationDbContext`, the same PostgreSQL database, and the same deployment unit as HR and Monitoring.

Phase 1 Work provides workspaces, simple projects, work items, direct project membership invitations, simple project settings, Kanban/List/Calendar project views, worklogs, and simple docs/pages where retained. Larger WorkSync capabilities such as sprints, advanced boards, roadmaps, OKR, chat, AI chat assistance, repository automation, advanced resource planning, workspace source pools, and Teams chat sync are Phase 2 design references unless explicitly reactivated.

Microsoft Teams workspace/group and chat sync is handled by the separate [[modules/integrations/microsoft-teams/overview|Microsoft Teams Integration]] module. Microsoft Teams chat/message sync is Phase 2.

---

## Module Index

| Module | Namespace | Phase | Tables / Scope | Spec |
|:-------|:----------|:------|:---------------|:-----|
| Foundation | `WorkSync.Foundation` | Phase 1 | workspaces, local workspace roles, workspace membership | [[modules/work-management/foundation\|Foundation]] |
| Project Management | `WorkSync.Projects` | Phase 1 | projects, project members/invitations, simple project links, simple settings | [[modules/work-management/projects\|Projects]] |
| Work Items | `WorkSync.Tasks` | Phase 1 | tasks/work items, assignments, checklists/comments, Kanban/List/Calendar views where retained | [[modules/work-management/tasks\|Tasks]] |
| Worklogs | `WorkSync.Time` | Phase 1 | time_logs/worklogs connected to work items | [[modules/work-management/time\|Time]] |
| Simple Docs/Pages | `WorkSync.Collaboration` | Phase 1 limited | simple project documents/pages if retained | [[modules/work-management/collaboration\|Collaboration]] |
| Planning | `WorkSync.Planning` | Phase 2 | sprints, boards, roadmaps, baselines | [[modules/work-management/planning\|Planning]] |
| OKR / Goals | `WorkSync.OKR` | Phase 2 | objectives, key results, check-ins | [[modules/work-management/okr\|OKR]] |
| My Space | `WorkSync.MySpace` | Phase 2 | personal boards, todos, saved views | [[modules/work-management/my-space\|My Space]] |
| Resource Management | `WorkSync.Resources` | Phase 2 | resource plans, allocations, capacity planning | [[modules/work-management/resources\|Resources]] |
| Chat | `WorkSync.Chat` | Phase 2 | channels, members, messages, Teams chat sync | [[modules/work-management/chat\|Chat]] |
| Chat AI | `WorkSync.ChatAI` | Phase 2 | AI detections, action jobs, reminders | [[modules/work-management/chat-ai\|Chat AI]] |
| Insight & Analytics | `WorkSync.Analytics` | Phase 2 unless simple reports retained | dashboards, widgets, saved views, exports | [[modules/work-management/analytics\|Analytics]] |
| Integration & API | `WorkSync.Integrations` | Phase 2 | repositories, code events, automation rules | [[modules/work-management/integrations\|Integrations]] |

---

## Add Employee vs Add Member

**Add Employee** creates a new company employee record and belongs to People.

**Add Member** adds an existing employee to a project/work membership context and belongs to Work. It must not create a new employee record.

---

## Cross-Module Data Flow

```text
tenants / legal_entities
  -> projects
  -> project_members
  -> work_items
  -> task_assignments
  -> worklogs
  -> simple project docs/pages
```

Phase 2 planning/chat/integration references:

```text
projects -> advanced planning / boards / roadmaps     (Phase 2)
projects -> OKR / goals                               (Phase 2)
projects -> advanced resource planning                (Phase 2)
channels / messages -> Chat and Teams sync            (Phase 2)
repositories -> code_activity_events / automation     (Phase 2)
```

Project/workspace relationship note: Phase 1 projects store one `workspace_id`. Workspace-heavy source pools and multi-workspace project participation are Phase 2 unless a later product decision explicitly reactivates them.

---

## Permission Model

Work uses a layered permission model. There is no separate generic "work role" engine beyond tenant RBAC and project membership in Phase 1.

1. **Tenant-level RBAC:** standard `roles`, `role_permissions`, and `user_permission_overrides`. Work permissions such as `projects:*`, `tasks:*`, and `worklogs:*` are seeded here.
2. **Project membership:** the source of truth for who can see or work inside a project. Project membership is created after a direct invitation is accepted.
3. **Local project access:** Admin, Member, Viewer, or equivalent local access level applies only inside that project.

Phase 2 may add broader workspace source-pool membership, team role, chat, planning, or integration access layers.

Authorization flow:

```text
Request arrives
  -> JWT validated
  -> module entitlement checked
  -> tenant RBAC checked
  -> project membership checked
  -> local project access checked
  -> allow or 403
```

---

## Context And Visibility Rules

Do not require administrators to configure a scope policy for every permission on every role. Permissions such as `tasks:write` and `projects:create` define action capability. Context comes from active company/legal-entity context, project membership, and local project access.

Position-derived employee visibility does not automatically grant project membership. Reporting-manager relationship does not grant Work access; project membership or local project authority is required.

Project health and progress are not shown the same way to every user:

| Viewer context | Show |
|:---------------|:-----|
| Full project administration context | Overall health, progress, members, and pending project actions |
| Project member context | Own tasks, watched tasks, assigned items, comments, and published project updates |
| Viewer/stakeholder context | Published summary, approved milestones if retained, and visible risks only |

The broader legal-entity/workspace/team visibility model from older WorkSync planning remains Phase 2 reference only.

---

## Key Invariants

1. **All Work entities are tenant-scoped.**
2. **Each Phase 1 project belongs to exactly one workspace.**
3. **Project membership controls project visibility.**
4. **Add Member does not create employees.**
5. **Worklogs may store both `user_id` and `employee_id` where HR joins are needed.**
6. **Documents are shared infrastructure.** The HR documents module and Work docs/pages share the document storage model with different scope values.
7. **Notifications are centralized.** Work domain events publish to Notifications like HR events.
8. **Planner, Goals/OKR, advanced roadmaps, broad resource planning, Chat AI, and automation rules are Phase 2.**

---

## Database Schema Files

- [[database/schemas/wms-project-management|WMS Project Management Schema]]
- [[database/schemas/wms-task-management|WMS Task Management Schema]]
- [[database/schemas/wms-collaboration|WMS Collaboration Schema]]
- [[database/schemas/wms-planning|WMS Planning Schema - Phase 2]]
- [[database/schemas/wms-chat|WMS Chat Schema - Phase 2]]
- [[database/schemas/wms-analytics|WMS Analytics Schema - Phase 2]]
- [[database/schemas/wms-integrations|WMS Integrations Schema - Phase 2]]

---

## Related

- [[Userflow/Work-Management/wm-overview|Work Userflow Overview]]
- [[Userflow/Work-Management/project-flow|Project Management]]
- [[Userflow/Work-Management/task-flow|Work Item Management]]
- [[Userflow/Work-Management/time-tracking-flow|Worklogs]]
- [[Userflow/Work-Management/collaboration-flow|Simple Docs/Pages]]
- [[Userflow/Work-Management/planning-flow|Planning - Phase 2]]
- [[Userflow/Work-Management/goals-okr-flow|Goals and OKRs - Phase 2]]
- [[Userflow/Work-Management/resource-flow|Resource Management - Phase 2]]
- [[Userflow/Work-Management/chat-ai-flow|Chat AI - Phase 2]]
- [[Userflow/Work-Management/integration-automation-flow|Integration Automation - Phase 2]]
