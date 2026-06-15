# Module Family: WorkSync (Work Management)

**Pillar:** 3 — WorkSync
**Phase:** 1
**Solution namespace:** `ONEVO.Modules.WorkSync.*`
**Database:** Same `ApplicationDbContext` as all other ONEVO modules — no separate database, no bridge APIs.

---

## Overview

WorkSync is ONEVO's internal work management pillar. It is not an external system. All WorkSync tables live in the same EF Core `ApplicationDbContext`, the same PostgreSQL database, and the same deployment unit as HR and Workforce Intelligence.

WorkSync provides projects, tasks, sprints, boards, OKR, chat, AI chat assistance, documents, roadmaps, GitHub integration, and analytics — all accessible via the same JWT that authenticates users in the HR pillar.

Microsoft Teams workspace/group and chat sync is handled by the separate [[modules/integrations/microsoft-teams/overview|Microsoft Teams Integration]] module. WorkSync owns workspace and chat behavior; the integration module owns Graph account linking, tokens, webhooks, and delta sync.

---

## Module Index

| Module | Namespace | Owner | Tables | Spec |
|:-------|:----------|:------|:-------|:-----|
| Foundation | `WorkSync.Foundation` | DEV5 | workspaces, workspace_members, workspace_roles, workspace_teams_links, teams_member_sync_status | [[modules/work-management/foundation\|Foundation]] |
| Project Management | `WorkSync.Projects` | DEV5 | projects, project_workspaces, project_members, epics, milestones, versions, release_calendar, labels | [[modules/work-management/projects\|Projects]] |
| Task Management | `WorkSync.Tasks` | DEV6 | tasks, task_assignments, task_checklists, task_checklist_items, task_tags, task_approvals, task_watchers, task_links, custom_fields, custom_field_values | [[modules/work-management/tasks\|Tasks]] |
| Planning | `WorkSync.Planning` | DEV6 | sprints, sprint_backlog_items, sprint_daily_snapshots, sprint_reports, boards, board_columns, board_task_positions, roadmaps, roadmap_items, baselines | [[modules/work-management/planning\|Planning]] |
| OKR | `WorkSync.OKR` | DEV5 | objectives, key_results, okr_check_ins | [[modules/work-management/okr\|OKR]] |
| My Space | `WorkSync.MySpace` | DEV7 | personal_boards, personal_board_columns, todos, saved_views | [[modules/work-management/my-space\|My Space]] |
| Time Management | `WorkSync.Time` | DEV5 | time_logs, timesheets, timesheet_entries | [[modules/work-management/time\|Time]] |
| Resource Management | `WorkSync.Resources` | DEV5 | resource_plans, resource_allocations, resource_availability_overrides | [[modules/work-management/resources\|Resources]] |
| Chat | `WorkSync.Chat` | DEV7 | channels, channel_members, messages, message_reactions, message_attachments, message_pins, channel_teams_links, teams_message_sync_state | [[modules/work-management/chat\|Chat]] |
| Chat AI | `WorkSync.ChatAI` | DEV7 | premium_ai_detections, ai_action_jobs, chat_reminder_items | [[modules/work-management/chat-ai\|Chat AI]] |
| Collaboration | `WorkSync.Collaboration` | DEV8 | documents (extended), document_versions, document_approvals, wiki_pages, task_documents | [[modules/work-management/collaboration\|Collaboration]] |
| Insight & Analytics | `WorkSync.Analytics` | DEV6 | dashboards, chart_widgets, saved_views, report_snapshots, report_exports, dashboard_shares, saved_view_shares | [[modules/work-management/analytics\|Analytics]] |
| Integration & API | `WorkSync.Integrations` | DEV8 | repositories, task_repository_links, code_activity_events, commit_records, pull_request_records, ci_pipeline_runs, task_automation_rules | [[modules/work-management/integrations\|Integrations]] |

---

## Cross-Module Data Flow

```
tenants (HR) ──────────────────────────────────────────────────────────>┐
legal_entities (HR Org Structure) ─────────────────────────────────────────────────────>│
                                                                         ▼
                                                              workspaces (Foundation)
                                                                         │
                              ┌──────────────────────────────────────────┤
                              ▼                                          ▼
                         projects ──────────────────────────────── workspace_members
                              │
               ┌──────────────┴──────────────┐
               ▼                             ▼
            tasks ──────────────────── sprints (Planning)
               │                             │
      ┌────────┴─────┐              sprint_backlog_items
      ▼              ▼                       │
 task_assignments  boards                sprint_daily_snapshots (burndown)
 (users)     board_columns
             board_task_positions

messages (Chat) ──────> premium_ai_detections ──────> ai_action_jobs
                                                              │
                                                        (creates task)

Microsoft Teams (Graph) ──────> workspace_teams_links ──────> workspaces
Microsoft Teams (Graph) ──────> channel_teams_links ──────> channels
Microsoft Teams messages ──────> teams_message_sync_state ──────> messages

tasks ──────> task_documents ──────> documents
tasks ──────> task_repository_links ──────> repositories
tasks ──────> code_activity_events (via webhook)
```

Project/workspace relationship note: the diagram is a logical dependency view, not an ownership rule. Projects are tenant-scoped and can link to multiple team workspaces through `project_workspaces`. Workspace membership does not automatically grant project visibility; project visibility comes from `project_members`.

Workspaces and projects have different jobs:

- **Workspace**: a regular collaboration area for a reporting team, explicit team, or work area. It owns workspace membership, chat, workspace resources, and workspace-level settings.
- **Project**: a delivery container with tasks, milestones, risks, blockers, progress, and health. A project can involve one or more workspaces through `project_workspaces`.

Creating a project from a workspace auto-links that workspace, but the project is not owned by exactly one workspace. A project can later request participation from other workspaces or legal entities.

---

## Permission Model

WorkSync uses a **layered** permission model. There is no separate generic "work role" engine beyond team roles, workspace membership, and project membership.

1. **Tenant-level RBAC** (from HR Auth module): standard `roles` + `role_permissions` + `user_permission_overrides`. WorkSync-specific permissions like `tasks:write`, `projects:write`, `sprints:manage` are seeded here.

2. **Project membership** (from WorkSync Projects): `project_members` is the source of truth for who can see or work on a project. Local access levels such as Admin, Member, and Viewer apply only inside that project.

3. **Workspace membership** (from WorkSync Foundation): `workspace_members` controls access to a team workspace, chat, workspace-level resources, and workspace administration. A workspace member does not automatically see every project linked to that workspace.

4. **Project-workspace context** (from WorkSync Projects): `project_workspaces` links a project to one or more team workspaces. This shows which workspaces/teams are involved, but it does not grant project visibility to every member of those workspaces.

5. **Team roles** (configured from Roles & Permissions, assigned from Org Structure Teams): `team_roles` + `team_role_permissions` provide scoped work authority inside a team/workspace context. Team roles are limited to Admin / Lead, Member, and Viewer / Reviewer. Team role permissions must stay inside team/work-context actions and must not grant tenant-wide HR, payroll, security, project visibility, billing, or system administration authority.

Authorization flow:
```
Request arrives →
  1. JWT validated (Auth module) — tenant_id, user_id confirmed
  2. Project membership check for project data — is user an active `project_members` row?
  3. Tenant RBAC check — does user have the required permission inside enabled module/feature boundaries?
  4. Local Admin/Member/Viewer check — does the project access level allow the action?
  5. Workspace/team-context check when needed — if the action is inside a linked workspace area, does workspace membership plus team role allow that scoped action?
  → Allow or 403
```

---

## Context And Visibility Rules

Do not require administrators to configure a scope policy for every permission on every role. Permissions such as `tasks:write`, `projects:create`, and `workspaces:manage` define action capability. Context comes from position hierarchy, active legal entity, workspace role, project membership, project-workspace link, and invite/approval state.

Hierarchy authority is not global. A reporting manager can use hierarchy to create a workspace from "My Reporting Team" or view subordinate contributions in contexts they can access. That authority does not automatically grant control over the same subordinate inside another manager's workspace or project.

A user may have `tasks:write`, but they still need the relevant project/workspace authority to create or assign tasks in that project/workspace.

Project health and progress are not shown the same way to every user:

| Viewer context | Show |
|:---------------|:-----|
| Full project administration context | Overall health, overall progress, all linked workspaces, all participating legal entities, all milestones, all risks/blockers, all pending project approvals, and all members. |
| Legal-entity-scoped approval or management context | Only the legal entity contribution, entity members in the project, entity risks/blockers, and entity participation approvals. |
| Workspace administration/lead context | Workspace progress, tasks, blockers, members, and milestones for that workspace. |
| Reporting manager/team lead context without project-wide authority | Only their reports' tasks, blockers, deadlines, and availability conflicts inside projects/workspaces they can access. |
| Project member context | Own tasks, watched tasks, assigned milestones, blockers they raised, and published project announcements. |
| Viewer/stakeholder context | Published summary, approved milestones, and published risks only. |

---

## Key Invariants

1. **All Work Management entities are tenant-scoped.** Project entities use `tenant_id` + `project_id`. Workspace entities use `tenant_id` + `workspace_id`. A project can link to multiple workspaces through `project_workspaces`, so `project_id` must not imply a single workspace.

1a. **Legal entity context is inferred.** When a user creates a project, `owning_legal_entity_id` is resolved from the active legal entity context. Users with access to multiple legal entities choose the context before creation; normal create forms do not ask for owning legal entity as a free field.

1b. **Cross-legal-entity participation requires approval.** A project can request participation from a workspace or member in another legal entity, but access begins only after the target workspace/legal-entity approver accepts the request. Approval grants project/workspace collaboration only; it does not grant reporting authority over that entity's employees.

2. **Work Management time logs feed HR analytics.** Time records store both `user_id` and `employee_id` where payroll, department, employment-status, or overtime reporting needs HR joins. `employee_id` is resolved from `employees.user_id` at write time.

3. **Documents are shared infrastructure.** The `documents` table is extended (not duplicated) with `workspace_id` and `project_id` for Work Management scope. The HR documents module and Work Management collaboration module share the same table with different `document_scope` values.

4. **Notifications are centralized.** Work Management domain events publish to the Notifications module exactly like HR events. No separate Work Management notification table.

5. **Roadmaps are Phase 1 for Work Management.** Although the HR phase plan originally deferred roadmaps to Phase 2, Work Management requires roadmaps in its Phase 4 user flow. `roadmaps` and `roadmap_items` are Phase 1 for Work Management.

---

## Database Schema Files

- [[database/schemas/wms-project-management|WMS Project Management Schema]]
- [[database/schemas/wms-task-management|WMS Task Management Schema]]
- [[database/schemas/wms-planning|WMS Planning Schema]]
- [[database/schemas/wms-chat|WMS Chat Schema]]
- [[database/schemas/wms-analytics|WMS Analytics Schema]]
- [[database/schemas/wms-collaboration|WMS Collaboration Schema]]
- [[database/schemas/wms-integrations|WMS Integrations Schema]]
- [[modules/integrations/microsoft-teams/overview|Microsoft Teams Integration]]

---

## Related

- [[Userflow/Work-Management/wm-overview|WorkSync Userflow Overview]] — user-facing module map
- [[Userflow/Work-Management/my-space-flow|My Space]] — personal boards, reminders, saved views
- [[Userflow/Work-Management/chat-ai-flow|Chat AI Flow]] — AI action detection and undo window
- [[Userflow/Work-Management/collaboration-flow|Work Management collaboration]] — documents, wiki, task document links
- [[Userflow/Work-Management/work-analytics-flow|WorkSync Analytics]] — dashboards, saved views, exports
- [[Userflow/Work-Management/integration-automation-flow|Integration Automation]] — repository events and automation rules
- [[Userflow/Work-Management/workspace-teams-sync|Workspace Teams Sync]] — Microsoft Teams workspace/channel linking

- [[ADE-START-HERE|ADE Start Here]] — Build order for WorkSync (Weeks 1–4)
- [[onevo-unified-entity-map|Entity Map]] — Sections 25–38 (all WorkSync tables)
- [[database/schema-catalog|Schema Catalog]] — WorkSync section
- [[modules/ide-extension/overview|IDE Extension]] — Uses WorkSync chat, tasks, sprints via tag engine
- [[current-focus/DEV5-wms-foundation|DEV5 Task Pack]]
- [[current-focus/DEV6-tasks-boards-planning|DEV6 Task Pack]]
- [[current-focus/DEV7-chat-ai-reminders|DEV7 Task Pack]]
- [[current-focus/DEV8-documents-github-ide|DEV8 Task Pack]]




