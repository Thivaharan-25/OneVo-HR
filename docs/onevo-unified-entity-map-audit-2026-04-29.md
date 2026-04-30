# OneVo Unified Entity Map Audit

Date: 2026-04-29  
Scope reviewed: `Userflow/`, `modules/`, `database/`, `OneVo_WorkSync_final.md`, `Boards.docx`, `onevo-unified-entity-map.md`, and core backend/frontend planning docs.

## Verdict

The direction of `onevo-unified-entity-map.md` is mostly right: it correctly moves HRMS and WorkSync toward one tenant identity model, one database, shared users, shared notifications, shared documents/files, and workspace-scoped WMS data.

However, it is not yet reliable as the build source of truth. The knowledge base still describes WorkSync/WMS as an external system connected by bridge APIs, while the entity map describes it as internal tables in the same database. Several WorkSync flows also have no durable entities yet, especially boards/backlog/burndown, GitHub/IDE monitoring, document locking/task-document links, team permission stacking, and WMS module documentation.

## Highest-Risk Problems

### P0-1: The knowledge base still says WMS is external, but the entity map says WMS is internal

Evidence:

- `onevo-unified-entity-map.md` says single unified PostgreSQL database, no bridge API, no microservice split, and deprecates `bridge_clients`, `wms_tenant_links`, `wms_role_mappings`, `bridge_api_keys`.
- `README.md` still says WMS is built by the WMS team and consumed via bridge contracts.
- `docs/onevo-phase1-scope.md` still says OneVo connects to an external Work Management System through 5 bridge contracts.
- `backend/module-catalog.md` still says WMS is external and ONEVO communicates via HTTP bridge contracts only.
- `backend/bridge-api-contracts.md` still defines the bridge as the integration contract.
- `current-focus/WMS-bridge-integration.md` is still organized around Dev 1-4 bridge ownership.

Why this is a real problem:

Developers or AI agents will implement two incompatible architectures. One path builds direct EF entities and one `ApplicationDbContext`; the other builds bridge clients, bridge auth, tenant links, and external HTTP contracts. This is not just wording. It changes database shape, backend dependencies, auth, deployment, testing, and ownership.

Required correction:

Promote the single solution/single database decision to the top-level source of truth. Mark bridge docs as historical migration references or rewrite them as internal module integration docs.

### P0-2: Database source-of-truth conflict: 175/176 tables vs about 288 tables

Evidence:

- `database/schema-catalog.md` calls itself the single source of truth and says 175 Phase 1 tables.
- `backend/module-catalog.md` says all 176 tables live in one `ApplicationDbContext`.
- `backend/folder-structure.md` says `ApplicationDbContext.cs` has all 176 tables.
- `onevo-unified-entity-map.md` says about 288 tables across 38 modules.
- `database/schemas/` has no WMS schema files for projects, tasks, planning, OKR, chat, reminders, dashboards, integrations, or WMS collaboration.

Why this is a real problem:

The entity map cannot be trusted by implementation agents while the database catalog says a different canonical schema. EF Core migrations, module ownership, test plans, and task assignments will be generated from the wrong table list.

Required correction:

Either make `onevo-unified-entity-map.md` the new canonical schema and update `database/schema-catalog.md`, or split it into WMS schema files under `database/schemas/` and update the catalog/counts/cross-module FK map.

### P0-3: The implementation plan is still for 4 developers, not the current 8-member team

Evidence:

- `README.md` says a 4-week delivery plan with 4 developers.
- `current-focus/README.md` says `Team Size: 4 developers`.
- `ADE-START-HERE.md` assigns work only to Dev 1 through Dev 4.
- `docs/ade-dev1-reading-flow.md` through `docs/ade-dev4-reading-flow.md` only cover four developers.
- No equivalent current-focus task packs exist for WMS projects/tasks/chat/documents/boards/GitHub/analytics as internal modules.

Why this is a real problem:

The extra four team members have no canonical ownership. Worse, if the old bridge plan remains, the new members may build WMS externally or duplicate HR shared-platform work.

Required correction:

Re-cut `current-focus/README.md` for 8 members. Suggested split: Dev 1-4 continue HR/platform foundations; Dev 5 WMS foundation/workspaces/projects; Dev 6 tasks/boards/planning; Dev 7 chat/AI/reminders/collaboration; Dev 8 documents/wiki/GitHub/integrations/analytics.

## Entity Map Problems

### P1-1: WorkSync board model is too thin for Backlog, Scrum Board, Kanban Board, Task Board, and Burndown Chart

Evidence:

- `Boards.docx` defines Backlog, Sprint, Scrum, Scrum Board, Kanban Board, Task Board, and Burndown Chart as separate concepts.
- `OneVo_WorkSync_final.md` requires configurable personal board columns, drag/drop status sync, sprint boards, roadmap ordering, and Kanban/chat two-way sync.
- `onevo-unified-entity-map.md` only has `boards` and `board_views`. There is no `backlogs`, `board_columns`, `board_status_mappings`, `board_card_positions`, `sprint_backlog_items`, or burndown data table.

Why this matters:

A single `tasks.status` field and `boards.type` cannot preserve per-board column order, user-specific board customization, sprint commitment snapshots, Kanban WIP rules, or burndown history.

Recommended fix:

Add at least:

- `backlogs` or define project backlog as first-class behavior.
- `board_columns` with `board_id`, `name`, `status_key`, `position`, `wip_limit`.
- `board_task_positions` or `task_board_states` for column and card ordering.
- `sprint_backlog_items` to snapshot planned sprint scope.
- `sprint_burndown_points` or `sprint_daily_snapshots` for burndown chart history.

### P1-2: GitHub repository linking and IDE extension monitoring are missing from the entity map

Evidence:

- `OneVo_WorkSync_final.md` requires GitHub OAuth, repository-task links, multi-repo task linking, commits, branch events, pull requests, CI/CD results, branch naming warnings, code activity reports, and two-way GitHub-WorkSync sync.
- `onevo-unified-entity-map.md` only has generic `integrations` with provider `github`, but no repository, task link, commit, branch, pull request, CI result, or automation-rule tables.
- New product requirement: when the IDE/coding-tool extension is installed, the desktop monitoring agent must also install automatically only if the tenant/user has purchased the monitoring desktop agent entitlement. If they have not purchased monitoring, only the IDE extension should install.

Why this matters:

The WorkSync flow cannot be built or reported from the current schema. Code Activity Reports especially need queryable event tables, not just opaque integration config JSON.
The automatic monitoring-agent install also creates a licensing/provisioning gap: extension install cannot blindly install the monitoring agent for every WorkSync user, because monitoring is a paid capability and likely has privacy/consent implications.

Recommended fix:

Add WMS development integration tables such as `repositories`, `task_repository_links`, `code_activity_events`, `commit_records`, `branch_events`, `pull_request_records`, `ci_pipeline_runs`, and `task_automation_rules`.
Also add or confirm entitlement/install-control tables or fields, for example `tenant_feature_flags`, `subscription_usage`, `agent_install_entitlements`, `ide_extension_installs`, and `agent_install_jobs`. The install workflow should be:

1. User installs IDE extension.
2. Extension authenticates to OneVo/WorkSync.
3. Backend checks whether the tenant/user has active monitoring desktop-agent entitlement.
4. If entitled, backend provisions/launches desktop agent installer or prompts secure install.
5. If not entitled, backend completes IDE extension setup only and does not install or activate monitoring agent.
6. All decisions are audit logged.

### P1-2a: IDE extension and desktop monitoring agent ownership boundary is undefined

Evidence:

- `OneVo_WorkSync_final.md` describes the IDE extension capturing code activity and coding time.
- Existing `modules/agent-gateway/` and `backend/folder-structure.md` treat the desktop monitoring agent as a separate agent solution/release path.
- New product requirement says the monitoring agent should be installed automatically through the IDE extension only for customers who bought monitoring.

Why this matters:

There are now two installation surfaces for monitoring: direct desktop agent deployment and IDE-extension-triggered install. Without one owner and one entitlement check, the team could build duplicate installers, bypass licensing, or create mismatched device/agent registration records.

Recommended fix:

Define the IDE extension as an installer/bootstrapper client for the existing Agent Gateway, not a second monitoring system. The extension should request install eligibility from the backend and the backend should create the official `registered_agents` / install job records. The extension should never decide entitlement locally.

### P1-3: Document merge is directionally right, but not sufficient for WorkSync document behavior

Evidence:

- `OneVo_WorkSync_final.md` requires platform document editing, version history, restore, Draft/In Review/Approved/Archived statuses, document approval comments, approval locking, task attachment, and project wiki.
- `onevo-unified-entity-map.md` merges WMS documents into `documents` and has `document_versions`, `document_approvals`, and `wiki_pages`.
- The `documents.status` enum uses `draft / in_review / published / archived`, not the WorkSync `Approved` status.
- There is no explicit lock/finalization field such as `locked_at`, `locked_by`, `is_locked`, or `approved_version_id`.
- There is no explicit `task_documents` join table. `attachments` links tasks to `file_assets`, but not tasks to editable `documents`.

Why this matters:

Approved WorkSync documents need to lock a specific version, not just mark the document row. Task-attached documents need a durable relationship to the document editor/version history, not only a file attachment.

Recommended fix:

Update `documents.status` to include `approved` or map `published` explicitly to approved. Add lock/version fields and a `task_documents` or generic `entity_documents` relation.

### P1-4: HR-managed WorkSync onboarding requires temporary-password state, but `users` does not model it

Evidence:

- `OneVo_WorkSync_final.md` says HR sets temporary credentials, first login detects temporary password, redirects to forced password change, and blocks navigation until changed.
- `onevo-unified-entity-map.md` has `users.password_hash` and `password_reset_tokens`, but no `must_change_password`, `password_set_by_admin`, `temporary_password_expires_at`, or first-login completion state.

Why this matters:

Forced password change is an auth/security state, not just UI behavior. Without a DB field, the backend cannot enforce the navigation block reliably across sessions/devices.

Recommended fix:

Add auth fields or an `auth_password_state` table covering temporary credential mode, expiry, and forced change completion.

### P1-5: WorkSync team permission stacking is not represented clearly

Evidence:

- `OneVo_WorkSync_final.md` says a user can belong to multiple teams and permissions stack accordingly.
- `onevo-unified-entity-map.md` has `workspace_roles` on `workspace_members`, and `team_members.role` only supports `lead / member`.
- There is no `team_roles`, `team_role_permissions`, or `team_member_roles` table.

Why this matters:

If team assignments affect authorization, the model needs a durable permission source. Otherwise, the system cannot explain or audit why a user gained a permission through multiple teams.

Recommended fix:

Either remove permission stacking from the WorkSync flow or add team-scoped roles and define the merge rule with workspace roles and HR tenant permissions.

### P1-6: Roadmap is required by the WorkSync user flow but marked Phase 2 in the entity map

Evidence:

- `OneVo_WorkSync_final.md` Phase 4 requires Team Lead to open Roadmap, view all sprints across a timeline, drag sprints, attach versions, and save arrangement.
- `onevo-unified-entity-map.md` marks `roadmaps`, `roadmap_items`, and `baselines` as Phase 2.

Why this matters:

If WorkSync is now being built as part of the unified product, Phase 4 of the WorkSync flow cannot be delivered without these tables or a revised UX.

Recommended fix:

Move `roadmaps` and `roadmap_items` to Phase 1 for WorkSync, or revise the WorkSync flow to defer roadmap UI.

### P1-7: WorkSync analytics/reporting requirements exceed the current entity map

Evidence:

- `OneVo_WorkSync_final.md` requires sprint velocity, time report, resource allocation report, code activity report, exports, dashboard sharing, KPI targets, and snapshots.
- `onevo-unified-entity-map.md` has `dashboards`, `chart_widgets`, `saved_views`, `report_snapshots`, `report_exports`, and `sprint_reports`.
- `kpi_targets` is Phase 2, `billable_rates` is Phase 2, GitHub code activity tables are absent, and dashboard sharing is not modeled except `dashboards.is_shared`.

Why this matters:

Dashboard sharing to selected users/teams and code activity reporting cannot be implemented from the listed tables.

Recommended fix:

Add dashboard/share ACL tables such as `dashboard_shares` and `saved_view_shares`. Add code activity tables listed in P1-2. Decide whether KPI targets are Phase 1 or remove KPI target flow from the WorkSync Phase 9 flow.

### P1-8: Chat AI auto-create/undo behavior needs persistence

Evidence:

- `OneVo_WorkSync_final.md` says premium AI auto-creates a task and shows a 10-second undo option.
- `onevo-unified-entity-map.md` has `premium_ai_detections`, `ai_suggestions`, and `chat_reminder_items`, but no undo window, pending auto-create state, expiration timestamp, or reversal audit.

Why this matters:

If the task is created immediately, undo must either soft-delete/reverse it or keep it pending until the window expires. Both approaches need explicit persistence and audit behavior.

Recommended fix:

Add fields such as `undo_expires_at`, `undone_at`, `created_task_id`, `finalized_at`, or use an `ai_action_jobs` table with pending/finalized/undone states.

## Knowledge-Base Gaps Created by the Unified Product Decision

### P1-9: There are Work-Management userflows, but no matching `modules/work-management` implementation module

Evidence:

- `Userflow/Work-Management/` exists.
- `modules/` has no WMS project/task/planning/chat/OKR module folders.
- `database/schemas/` has no WMS schema files.

Why this matters:

Agents reading module docs will not find implementation guidance for the new internal WorkSync modules. They may fall back to old bridge docs.

Recommended fix:

Create module docs for WMS domains or one `modules/work-management/` tree with submodules matching the entity map sections.

### P1-10: Documents are still treated as HR/Phase-2 in parts of the knowledge base, but WorkSync makes them core

Evidence:

- `Userflow/Documents/` and `modules/documents/` are HR-oriented.
- `docs/phase1-userflow.md` says Phase 2 modules include Documents.
- `OneVo_WorkSync_final.md` Phase 7 requires WorkSync document creation, approval, locking, and wiki.
- `onevo-unified-entity-map.md` puts Documents in Phase 1 and extends them with workspace/project scope.

Why this matters:

If the team follows the old HR phase plan, a core WorkSync flow will be missing. The unified product needs documents as a shared platform capability, not only HR employee-document storage.

Recommended fix:

Reclassify Documents as shared Phase 1 if WorkSync Phase 7 remains in scope. Update `modules/documents/overview.md`, `database/schemas/documents.md`, and phase docs accordingly.

### P2-1: Single solution/deployment wording still conflicts with separate agent/developer-platform docs

Evidence:

- User direction: one codebase solution file and deployed as a single unit.
- `backend/folder-structure.md` says `ONEVO.Agent.sln` is a separate solution with its own release cycle.
- `docs/onevo-phase1-scope.md` says `console.onevo.io` is a completely separate application.

Why this matters:

If "single unit" includes the desktop agent and operator console, current docs violate that requirement. If "single unit" only means HR + WorkSync web/backend, the docs need to say that clearly.

Recommended fix:

Clarify deployment boundary:

- Option A: Single web/backend product unit; desktop agent remains separate installer.
- Option B: One repository and one `.sln` containing backend, admin host, and agent projects, with separate runtime artifacts.

Do not leave this ambiguous.

## Lower-Risk Entity Concerns

### P2-2: Calendar events may need participant and meeting tables

`calendar_events` supports polymorphic `entity_type/entity_id`, but WorkSync mentions meetings and unified user calendars. If meetings require attendees, RSVPs, or recurrence exceptions, add `calendar_event_participants` and possibly `meeting_records`.

### P2-3: Time logs and HR overtime/payroll mapping need a stronger employee bridge

`time_logs` and `timesheets` are user/workspace scoped, while HR payroll and overtime are employee scoped. Because `employees.user_id` is the bridge, this can work, but reports/payroll approval rules should explicitly require a resolvable employee for HR-impacting time.

### P2-4: `labels` are project-scoped only

Personal boards, cross-project dashboards, and chat-created tasks may need workspace-level labels. If labels are project-only, cross-project personal boards will duplicate label taxonomies.

## What Is Correct in the Entity Map

- `users` as the shared identity root is correct.
- `employees.user_id` as the HR bridge is correct.
- `workspace_members` is the right core junction for WMS access.
- `workspaces.legal_entity_id` is a good way to preserve HR topbar/legal-entity scope.
- Keeping `employee_id` canonical for HR flows is correct.
- Merging `notifications`, `audit_logs`, `calendar_events`, `overtime_records`, `file_records/file_assets`, and `documents` is the right architecture for one deployment.
- Deprecating bridge tables is correct if the product decision is now truly single database and single deployment.

## Recommended Fix Order

1. Decide and document the final deployment boundary: HR + WorkSync definitely one backend/database; clarify whether desktop agent/admin console are in the same solution/deployment.
2. Update top-level knowledge-base docs to remove external-WMS bridge architecture as the active plan.
3. Replace the 4-dev task plan with an 8-member plan.
4. Promote the unified entity map into `database/schema-catalog.md` and split WMS schemas into `database/schemas/`.
5. Add missing WorkSync entity groups: board/backlog/burndown, GitHub/IDE monitoring, document locking/task-document links, dashboard sharing, team-role stacking, temporary-password state.
6. Create WMS module docs under `modules/` so developers do not rely on old bridge files.
