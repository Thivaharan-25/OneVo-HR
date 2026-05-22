# ONEVO — ADE Entry Point

> **Read this file first.** It tells you what ONEVO is, what to build (Phase 1), what NOT to build (Phase 2), and where to find everything.

---

## What Is ONEVO?

ONEVO is a **unified multi-tenant SaaS** platform combining three product pillars in a single backend and database:

1. **HR Management** — Employee lifecycle, leave, org structure, payroll, skills, compliance
2. **Workforce Intelligence** — Desktop activity monitoring, presence tracking, biometric verification, exception detection, productivity analytics
3. **WorkSync** — Work management built internally: projects, tasks, sprints, boards, roadmaps, OKR, chat, AI, documents, GitHub integration — all in the same backend and database as HR, no bridge APIs

Plus an **IDE Extension** — a full chat sidebar and tag-based automation surface embedded in VS Code. Developers can trigger any OneVo action they have permission for without leaving their editor, using `@entity:action params` syntax.

**Core value propositions:**
- HR: "Who works here, what is their status, are they compliant?"
- Workforce Intelligence: "Is this employee present and productive? Any anomalies?"
- WorkSync: "What is the team building, in what sprint, by when?"
- IDE Extension: "Every OneVo action, one tag away, inside your editor."

---

## Tech Stack

| Layer | Technology |
|:------|:-----------|
| **Backend** | .NET 9 / C# 13 current; .NET 10 / C# 14 target after migration |
| **Database** | PostgreSQL 16.13 baseline / PostgreSQL 18 target after validation + EF Core 9 current / EF Core 10 target — single `ApplicationDbContext`, ~288 tables |
| **Frontend** | Angular 21, TypeScript, Angular Router, Angular Material, Angular Signals — two-app monorepo (`employee-app` + `management-app` + `shared` library) |
| **Real-time** | SignalR — agent↔server bidirectional; server→browser for WorkSync live updates and IDE extension |
| **Background Jobs** | Hangfire |
| **Messaging** | MediatR for command/query dispatch; optional in-process domain events by exception |
| **Caching** | Redis |
| **File Storage** | Cloudflare R2 object storage |
| **Email** | Resend |
| **Auth** | JWT (RS256) + refresh tokens, MFA (TOTP) |
| **Search** | PostgreSQL FTS (Phase 1) |
| **IDE Extension** | VS Code Extension API (TypeScript) |

**Architecture:** Clean Architecture + CQRS. Single `ApplicationDbContext` for all 38 modules. No microservices. No bridge APIs. Desktop monitoring agent is a separate solution (`ONEVO.Agent.sln`) with its own release cycle and ring-based deployment — it is not part of the main web deployment.

**Tenant domain model:** ONEVO owns the parent domain, for example `onevo.com`. Cloudflare manages DNS for `onevo.com` and wildcard `*.onevo.com`; Azure hosts the app/API. Default tenant URLs are `https://{tenantSlug}.onevo.com`. Do not buy a new domain per tenant; tenant access uses ONEVO-owned subdomains only.

---

## Phase 1 — Pillar 1: HR Management (15 Modules)

| # | Module | Purpose | Spec |
|:--|:-------|:--------|:-----|
| 1 | **Infrastructure** | Multi-tenancy, file management, reference data | [[modules/infrastructure/overview\|Infrastructure]] |
| 2 | **Auth** | Login, MFA, JWT, hybrid permission model, temporary-password forced-change flow | [[modules/auth/overview\|Auth]] |
| 3 | **Core HR** | Employee profiles, lifecycle events, HR-managed credential creation | [[modules/core-hr/overview\|Core HR]] |
| 4 | **Org Structure** | Departments, teams, job titles, team roles, permission stacking | [[modules/org-structure/overview\|Org Structure]] |
| 5 | **Shared Platform** | SSO, workflow engine, approval routing, subscription plans, entitlements | [[modules/shared-platform/overview\|Shared Platform]] |
| 6 | **Agent Gateway** | Desktop agent communication, policy distribution, remote commands, agent install jobs | [[modules/agent-gateway/overview\|Agent Gateway]] |
| 7 | **Configuration** | Monitoring toggles, app allowlist (tenant→role→employee), retention policies | [[modules/configuration/overview\|Configuration]] |
| 8 | **Workforce Presence** | Clock in/out, biometric events, breaks, unified presence sessions | [[modules/workforce-presence/overview\|Workforce Presence]] |
| 9 | **Identity Verification** | Photo/fingerprint verification, on-demand capture from manager alerts | [[modules/identity-verification/overview\|Identity Verification]] |
| 10 | **Activity Monitoring** | App/device/meeting tracking, screenshots, daily summaries | [[modules/activity-monitoring/overview\|Activity Monitoring]] |
| 11a | **Discrepancy Engine** | WorkSync time log vs agent activity cross-check, discrepancy events | [[modules/discrepancy-engine/overview\|Discrepancy Engine]] |
| 11 | **Exception Engine** | Anomaly detection rules, alerts, escalation, remote capture trigger | [[modules/exception-engine/overview\|Exception Engine]] |
| 12 | **Notifications** | In-app, email (Resend), SignalR real-time push | [[modules/notifications/overview\|Notifications]] |
| 13 | **Leave** | Leave types, policies, entitlements, approval workflow | [[modules/leave/overview\|Leave]] |
| 14 | **Calendar** | Company events, public holidays, leave-conflict checks | [[modules/calendar/overview\|Calendar]] |
| 15 | **Productivity Analytics** | Daily/weekly/monthly reports, manager/CEO/employee dashboards | [[modules/productivity-analytics/overview\|Productivity Analytics]] |

---

## Phase 1 — Pillar 3: WorkSync (13 Internal Modules)

All WorkSync modules live in the same .NET solution, same `ApplicationDbContext`, same PostgreSQL database. No bridge APIs. No external WMS backend.

| # | Module | Purpose | Owner | Spec |
|:--|:-------|:--------|:------|:-----|
| W1 | **WorkSync Foundation** | Workspaces, workspace_members, workspace_roles | DEV5 | [[modules/work-management/foundation\|WS Foundation]] |
| W2 | **Project Management** | Projects, project_members, epics, milestones, versions, release_calendar | DEV5 | [[modules/work-management/projects\|WS Projects]] |
| W3 | **Task Management** | Tasks, task_assignments, task_checklists, task_tags, custom_field_values, task_approvals | DEV6 | [[modules/work-management/tasks\|WS Tasks]] |
| W4 | **Planning** | Sprints, sprint_backlog_items, sprint_daily_snapshots, boards, board_columns, board_task_positions | DEV6 | [[modules/work-management/planning\|WS Planning]] |
| W5 | **OKR** | Objectives, key_results, okr_check_ins | DEV5 | [[modules/work-management/okr\|WS OKR]] |
| W6 | **My Space** | Personal_boards, personal_board_columns, todos, saved_views | DEV7 | [[modules/work-management/my-space\|WS My Space]] |
| W7 | **Time Management** | Time_logs, timesheets, timesheet_entries | DEV5 | [[modules/work-management/time\|WS Time]] |
| W8 | **Resource Management** | Resource_plans, resource_allocations, resource_rates | DEV5 | [[modules/work-management/resources\|WS Resources]] |
| W9 | **Chat** | Channels, channel_members, messages, message_reactions, message_attachments | DEV7 | [[modules/work-management/chat\|WS Chat]] |
| W10 | **Chat AI** | Premium_ai_detections, ai_action_jobs (undo state machine), chat_reminder_items | DEV7 | [[modules/work-management/chat-ai\|WS Chat AI]] |
| W11 | **Collaboration** | Documents (WMS scope), document_approvals, wiki_pages, task_documents, document_versions | DEV8 | [[modules/work-management/collaboration\|WS Collaboration]] |
| W12 | **Insight & Analytics** | Dashboards, chart_widgets, sprint_reports, report_snapshots, dashboard_shares, saved_view_shares | DEV6 | [[modules/work-management/analytics\|WS Analytics]] |
| W13 | **Integration & API** | Repositories, task_repository_links, code_activity_events, commit_records, pull_request_records, ci_pipeline_runs, task_automation_rules, integration_connections | DEV8 | [[modules/work-management/integrations\|WS Integrations]] |

---

## Phase 1 — IDE Extension

| # | Module | Purpose | Owner | Spec |
|:--|:-------|:--------|:------|:-----|
| IDE | **IDE Extension** | VS Code plugin: embedded chat sidebar, tag engine for all OneVo actions, context engine (branch→task, file→task), entitlement-gated desktop agent provisioning | DEV7 + DEV8 | [[modules/ide-extension/overview\|IDE Extension]] |

### Tag Technology

Users type `@entity:action params` in the chat sidebar or in code comments/commit messages to trigger any OneVo action they have permission for. The backend validates the permission before executing. All tag executions are logged in `ide_tag_executions` with a reversible undo window.

**Supported tag entities:** `task`, `sprint`, `project`, `chat`, `time`, `leave`, `doc`, `review`, `notify`, `board`, `okr`

**Examples:**
```
@task:new "Fix OAuth redirect" #sprint:current @assign:sarah #priority:high
@task:status #TASK-456 done
@time:log 2h #TASK-456 "Authentication refactor"
@sprint:move #TASK-456 to:next
@chat:send #dev-backend "PR ready for review, closes #TASK-456"
@leave:request 2026-05-05 2026-05-07 "Conference"
@doc:view "API Guidelines"
@review:request #TASK-456 @reviewer:john
@board:move #TASK-456 column:"In Review"
@notify:send @sarah "Sprint planning in 15 minutes"
```

---

## Phase 1 — Partial Module (Skills Core)

5 Skills tables are built in Phase 1 as part of **Dev 3's** work (after Org Structure):

| Tables (Phase 1 only) | Purpose |
|:----------------------|:--------|
| `skill_categories` | Taxonomy root |
| `skills` | Individual skill records |
| `job_skill_requirements` | Required skills per job title |
| `employee_skills` | Employee skill proficiency |
| `skill_validation_requests` | Peer/manager validation requests |

The remaining 10 Skills tables (courses, LMS, assessments, dev plans, certifications) are Phase 2.

---

## Phase 2 — Do NOT Build These

| Item | Reason Deferred |
|:-----|:----------------|
| **Performance module** | Performance reviews not core to Phase 1 MVP |
| **Skills LMS** | 10 remaining tables — courses, assessments, dev plans, certifications |
| **Grievance module** | Case tracking |
| **Expense module** | Claims / routing |
| **Payroll module** | Full payroll engine; activity data feed is read-only in Phase 1 |
| **KPI targets** (`kpi_targets` table) | WorkSync Phase 2 |
| **Billable rates** (`billable_rates` table) | WorkSync Phase 2 |
| **MacOS desktop agent** | Windows only in Phase 1 |
| **Face recognition ML matching** | Identity Verification Phase 2 |

---

## Build Order / Critical Path

```
Week 1 (Foundation — all 8 devs in parallel):
  DEV1: Infrastructure (tenants, users, file storage, legal_entities)
  DEV2: Auth & Security (roles, permissions, sessions, JWT, temporary-password fields on users)
  DEV3: Org Structure (departments, teams, job_titles, team_roles, team_role_permissions)
  DEV4: Shared Platform + Agent Gateway (subscriptions, entitlements, agent_install_entitlements)
  DEV5: WorkSync Foundation (workspaces, workspace_members, workspace_roles)
  DEV6: Task foundation (tasks, task_assignments — depends on DEV5 workspaces + DEV3 legal_entities)
  DEV7: Chat foundation (channels, channel_members, messages — depends on DEV5)
  DEV8: Documents + file_assets WMS scope (depends on DEV1 Infrastructure)

  DEPENDENCY: DEV5 must complete workspaces before DEV6 tasks and DEV7 channels can start.
  DEV5 workspaces depends on DEV1 tenants + DEV3 legal_entities being done first.

Week 2 (Core modules):
  DEV1: Core HR — Employee Profile (users.must_change_password + password auth state)
  DEV2: Core HR — Employee Lifecycle (hire/terminate/transfer domain events)
  DEV3: Workforce Presence (shifts, schedules, clock-in/out)
  DEV4: Workforce Presence — Biometric integration
  DEV5: Projects + project_members + epics + milestones + versions
  DEV6: Boards + board_columns + board_task_positions + sprint_backlog_items
  DEV7: Chat AI — premium_ai_detections + ai_action_jobs undo state machine
  DEV8: wiki_pages + document_approvals + task_documents (documents locked_at/locked_by fields)

Week 3 (Intelligence + planning):
  DEV1: Leave (leave_types, leave_requests, leave_balances, approval workflow)
  DEV2: Exception Engine (anomaly rules, alerts, escalation)
  DEV3: Activity Monitoring (app_sessions, screenshots, browser_activity, daily_summaries)
  DEV4: Identity Verification (biometric_snapshots, verification_logs)
  DEV5: OKR (objectives, key_results, okr_check_ins) + Time Management (time_logs, timesheets)
  DEV6: Sprint planning — sprint_daily_snapshots (burndown) + roadmaps + roadmap_items (Phase 1 for WorkSync)
  DEV7: Reminders + My Space (personal_boards, personal_board_columns, todos, saved_views)
  DEV8: GitHub/GitLab integration (repositories, task_repository_links, code_activity_events)

Week 4 (Analytics + AI + CI):
  DEV1: Productivity Analytics (aggregation jobs, dashboards, report exports)
  DEV2: Exception Engine (continued — alert batching, email escalation)
  DEV3: Calendar (calendar_events, public_holidays, conflict checks)
  DEV4: Notifications + Configuration (monitoring toggles, app allowlist)
  DEV5: Resource Management (resource_plans, resource_allocations)
  DEV6: Insight & Analytics (dashboards, chart_widgets, dashboard_shares, saved_view_shares, sprint_reports)
  DEV7: Chat AI refinements + ai_action_jobs full state machine (pending/finalized/undone/failed)
  DEV8: commit_records + pull_request_records + ci_pipeline_runs + task_automation_rules

Week 5 (IDE Extension — core):
  DEV7: IDE Extension VS Code — OAuth auth, WebSocket to SignalR hub, sidebar panels
        (Chat panel with message send/receive, Tasks panel, Notifications panel)
  DEV8: IDE Extension VS Code — IDE context engine (branch→task linking, file→task detection)
        + ide_extension_installs + ide_sessions tables

Week 6 (IDE Extension — tag engine + entitlement):
  DEV7: IDE Extension — tag parser, autocomplete, all @entity:action types, permission validation
        + ide_tag_executions table (undo window, audit)
  DEV8: IDE Extension — agent install entitlement flow
        (check agent_install_entitlements → create agent_install_jobs → download installer)
        + ide_context_links table
```

**Hard dependencies:**
- DEV1 Infrastructure before ALL other modules (tenant context)
- DEV2 Auth before ALL other modules (RBAC on every endpoint)
- DEV3 Org Structure before DEV5 WorkSync Foundation (legal_entities in workspaces)
- DEV5 WorkSync Foundation before DEV6 boards/tasks and DEV7 chat
- DEV8 Documents before DEV8 task_documents (documents table must exist)
- DEV6 Boards + Sprints before DEV6 burndown snapshots
- DEV7 Chat before DEV7 Chat AI (messages table must exist)
- DEV4 Agent Gateway + entitlements before DEV8 IDE agent provisioning
- IDE Extension auth (DEV7 Week 5) before tag engine (DEV7 Week 6)

---

## Key Architecture Concepts

### Single Database — No Bridge APIs
All 38 modules share one `ApplicationDbContext`. WorkSync tables (`projects`, `tasks`, `sprints`, `boards`, `channels`, etc.) are EF Core entities exactly like HR tables. `backend/bridge-api-contracts.md` is **DEPRECATED**. Do not implement it.

### Hybrid Permission Model
NOT simple RBAC. Roles are **templates**. Tenant Super Admin / tenant owner can grant permissions only from that tenant's enabled module catalog (subscription plan modules + paid add-ons + trial modules + approved feature grants - disabled modules). Tenant Super Admin does not bypass commercial entitlement; disabled or unpurchased module permissions must not be shown, assigned, or accepted by APIs. Platform Super Admin is separate and applies only to Developer Platform / operator routes. Access is hierarchy-scoped (manager sees their team only), with explicit bypass grants for approved exceptions. WorkSync adds workspace-level roles (Admin/Member/Viewer) on top of HR tenant-level roles. Both are evaluated together for cross-module flows. Team roles (`team_roles`, `team_role_permissions`) stack on top of workspace roles. See [[modules/auth/overview|Auth]].

### Temporary Password Flow
HR sets temporary credentials when creating a WorkSync user via the onboarding flow. The `users` table has `must_change_password` (boolean), `password_set_by_admin` (boolean), and `temporary_password_expires_at` (timestamptz). On first login, if `must_change_password = true`, the backend returns a 403 with code `MUST_CHANGE_PASSWORD` — the frontend blocks all navigation and forces password change before issuing a full session.

### Tag Technology (IDE Extension)
The IDE extension parses `@entity:action params` syntax in:
1. Chat sidebar input (primary surface — always available)
2. Code comments (opt-in per repo, via `.onevo` config file)
3. Commit message template (injected by extension)

The tag engine calls the same backend API endpoints as the web frontend. The backend validates permissions — the extension never decides authorization locally. Executions are logged in `ide_tag_executions`. Reversible actions get an `undo_expires_at` timestamp. Clicking undo sends a DELETE/PATCH to the backend before the window expires.

### IDE Extension Entitlement — Agent Install
When the IDE extension connects and the user authenticates:
1. Extension calls `GET /api/v1/ide/entitlements` — returns monitoring entitlement status
2. If `has_monitoring_entitlement = true` → extension shows "Set up desktop monitoring?" prompt
3. User clicks Yes → backend creates `agent_install_jobs` record and returns installer download URL
4. Extension downloads and runs the official signed installer
5. Installer registers with Agent Gateway → creates `registered_agents` record
6. If `has_monitoring_entitlement = false` → no prompt, no install, IDE extension features only

**The extension never installs the agent silently. The extension never decides entitlement locally.**

### AI Action State Machine
`ai_action_jobs` handles all reversible AI-triggered actions (auto-create task from chat, tag-triggered creates). States: `pending → finalized` (after undo window) | `pending → undone` (user clicked undo). The frontend polls or receives a SignalR event when the state transitions. `undo_expires_at` is 10 seconds for chat AI auto-create, configurable for IDE tag creates.

### Monitoring Lifecycle
Desktop agent data collection is controlled by clock-in/break/clock-out from Workforce Presence. No data captured before clock-in, during breaks, or after clock-out. GDPR requirement. See [[modules/agent-gateway/monitoring-lifecycle/overview|Monitoring Lifecycle]].

### Bidirectional SignalR
- **Agent → Server:** Heartbeats, data push (screenshots, app usage, device sessions)
- **Server → Agent:** Commands (start/stop/pause monitoring, request screenshot/photo, update policy)
- **Server → IDE Extension:** Real-time task updates, chat messages, notifications, tag action results, undo window countdown

---

## How to Read a Module Spec

Every module overview (`modules/*/overview.md`) follows the same structure:

1. **Header** — Namespace, Phase, Pillar, Owner, Tables
2. **Purpose** — What this module does
3. **Dependencies** — What it depends on and what consumes it
4. **Public Interface** — The C# interface other modules call
5. **Database Tables** — Full schema with columns, types, indexes
6. **Optional Domain Events** - only events with justified post-save consumers; omit when none exist
7. **Key Business Rules** — Critical logic constraints
8. **API Endpoints** — REST routes with permissions
9. **Hangfire Jobs** — Background jobs with schedules
10. **Features** — Links to sub-feature specs
11. **Related** — Cross-references

---

## Essential Reference Docs

| Doc | Purpose | Link |
|:----|:--------|:-----|
| **Project Context** | Full project background | [[AI_CONTEXT/project-context\|Project Context]] |
| **Tech Stack** | All technology choices with versions | [[AI_CONTEXT/tech-stack\|Tech Stack]] |
| **Rules** | AI coding standards and conventions | [[AI_CONTEXT/rules\|Rules]] |
| **Current Focus** | Dev assignments, deadlines, task files | [[current-focus/README\|Current Focus]] |
| **Module Catalog** | Quick index of all 38 modules | [[backend/module-catalog\|Module Catalog]] |
| **Schema Catalog** | Authoritative table list (~288 tables) | [[database/schema-catalog\|Schema Catalog]] |
| **Entity Map** | Full unified entity map with all tables | [[onevo-unified-entity-map\|Entity Map]] |
| **IDE Extension Spec** | Full IDE extension build plan | [[modules/ide-extension/overview\|IDE Extension]] |
| **Shared Kernel** | Cross-cutting code (Result, AuditableEntity) | [[backend/shared-kernel\|Shared Kernel]] |
| **API Conventions** | REST patterns, pagination, error format | [[backend/api-conventions\|API Conventions]] |
| **Domain Events** | Optional event rules and examples | [[backend/domain-events\|Domain Events]] |
| **Multi-Tenancy** | Tenant isolation patterns | [[infrastructure/multi-tenancy\|Multi-Tenancy]] |
| **Known Issues** | Gotchas and deprecated patterns | [[AI_CONTEXT/known-issues\|Known Issues]] |

---

## For Each Developer

- **Dev 1:** [[current-focus/DEV1-infrastructure-setup|Infrastructure]], [[current-focus/DEV1-core-hr-profile|Core HR Profile]], [[current-focus/DEV1-leave|Leave]], [[current-focus/DEV1-productivity-analytics|Productivity Analytics]]
- **Dev 2:** [[current-focus/DEV2-auth-security|Auth]], [[current-focus/DEV2-core-hr-lifecycle|Core HR Lifecycle]], [[current-focus/DEV2-exception-engine|Exception Engine]], [[current-focus/DEV2-notifications|Notifications]]
- **Dev 3:** [[current-focus/DEV3-org-structure|Org Structure]], [[current-focus/DEV3-workforce-presence-setup|Workforce Presence]], [[current-focus/DEV3-activity-monitoring|Activity Monitoring]], [[current-focus/DEV3-calendar|Calendar]], [[current-focus/DEV3-skills-core|Skills Core]]
- **Dev 4:** [[current-focus/DEV4-shared-platform-agent-gateway|Shared Platform + Agent Gateway]], [[current-focus/DEV4-workforce-presence-biometric|Workforce Presence Biometric]], [[current-focus/DEV4-identity-verification|Identity Verification]], [[current-focus/DEV4-configuration|Configuration]]
  - **ADE task note:** For Agent Gateway, create one task named **"Implement login-based Windows agent enrollment"**. Use [[modules/agent-gateway/overview|Agent Gateway]], [[modules/agent-gateway/agent-registration/overview|Agent Registration]], [[modules/agent-gateway/agent-server-protocol|Agent Server Protocol]], [[modules/agent-gateway/tray-app-ui|Tray App UI]], [[modules/agent-gateway/agent-installer|Agent Installer]], [[modules/auth/overview|Auth]], and [[modules/agent-gateway/monitoring-lifecycle/overview|Monitoring Lifecycle]]. Do not create tenant-key registration as the default install task.
- **Dev 5:** [[current-focus/DEV5-wms-foundation|WorkSync Foundation + Projects + OKR + Time + Resources]]
- **Dev 6:** [[current-focus/DEV6-tasks-boards-planning|Tasks + Boards + Planning + Roadmaps + Analytics]]
- **Dev 7:** [[current-focus/DEV7-chat-ai-reminders|Chat + Chat AI + My Space + Reminders + IDE Extension core]]
- **Dev 8:** [[current-focus/DEV8-documents-github-ide|Documents + Wiki + GitHub Integration + CI/CD + IDE Tag Engine + Agent Entitlement]]

**Target delivery:** 8 weeks from start.

---

## What NOT to Do

1. **Do not build Phase 2 modules** — check `**Phase:**` marker in each module overview
2. **Do not implement bridge API contracts** — `backend/bridge-api-contracts.md` is **DEPRECATED**. WorkSync is internal.
3. **Do not create a separate WMS backend or WMS database** — single `ApplicationDbContext` for everything
4. **Do not introduce RabbitMQ/MassTransit/IEventBus** - Phase 1 uses MediatR for CQRS; domain events are optional and in-process only
5. **Do not use Meilisearch** — PostgreSQL FTS is sufficient for Phase 1
6. **Optional Domain Events** - only events with justified post-save consumers; omit when none exist
7. **Do not capture agent data outside monitoring lifecycle** — no data before clock-in, during breaks, or after clock-out
8. **Do not install the desktop monitoring agent via the IDE extension without entitlement check** — always validate `agent_install_entitlements` server-side; never silently install
9. **Do not validate permissions in the IDE extension client** — the extension sends actions to the backend; the backend validates and rejects if unauthorized
10. **Do not build KPI targets or billable rates** — Phase 2 WorkSync features
