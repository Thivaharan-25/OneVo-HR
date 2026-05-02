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
| Project Management | `WorkSync.Projects` | DEV5 | projects, project_members, epics, milestones, versions, release_calendar, labels | [[modules/work-management/projects\|Projects]] |
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
legal_entities (HR Org Structure) ──────────────────────────────────────>│
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

---

## Permission Model

WorkSync uses a **dual-layer** permission model:

1. **Tenant-level RBAC** (from HR Auth module): standard `roles` + `role_permissions` + `user_permission_overrides`. WorkSync-specific permissions like `tasks:write`, `projects:write`, `sprints:manage` are seeded here.

2. **Workspace-level roles** (from WorkSync Foundation): `workspace_roles` (Admin/Member/Viewer) scoped to a specific workspace. These are evaluated together with tenant-level permissions. A user must pass both checks to act.

3. **Team roles** (from HR Org Structure): `team_roles` + `team_role_permissions` stack on top of workspace roles. When a user belongs to multiple teams, permissions union (most permissive wins within workspace scope).

Authorization flow:
```
Request arrives →
  1. JWT validated (Auth module) — tenant_id, user_id confirmed
  2. Workspace-level check — is user a member of this workspace?
  3. Tenant RBAC check — does user have the required permission?
  4. Team role stacking — if workspace role is insufficient, do any team roles grant access?
  → Allow or 403
```

---

## Key Invariants

1. **All Work Management entities are tenant-scoped.** Every table has `tenant_id` + either `workspace_id` or `project_id` (which implies workspace). Global query filters enforce both.

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


