# Current Focus: ONEVO

**Current Phase:** Phase 1
**Team Size:** 8 developers
**Development Approach:** Agentic Development Environment (AI-assisted)

---

## How to Use This Folder

Each file below is a **self-contained task** for one developer. It includes:
1. **Step 1: Backend** — acceptance criteria, module doc links
2. **Step 2: Frontend** — pages to build, userflow links, API endpoints to consume

The dev builds backend first, then frontend for the same module. Each task file links to the relevant Userflows so the AI knows the full user journey.

> **Architecture note:** WorkSync (Pillar 3) is built internally — same backend, same database. There are no bridge APIs. `WMS-bridge-integration.md` is **DEPRECATED**. Do not implement it.

---

## Task Assignment — Dev 1 (HR Foundation + Analytics)

| # | Task | Module | Priority | Task File |
|:--|:-----|:-------|:---------|:----------|
| 1 | Infrastructure & Foundation | Infrastructure + SharedKernel | Critical | [[current-focus/DEV1-infrastructure-setup\|DEV1 Infrastructure Setup]] |
| 2 | Employee Profile | CoreHR | Critical | [[current-focus/DEV1-core-hr-profile\|DEV1 Core HR Profile]] |
| 3 | Leave | Leave | High | [[current-focus/DEV1-leave\|DEV1 Leave]] |
| 4 | Productivity Analytics | ProductivityAnalytics | High | [[current-focus/DEV1-productivity-analytics\|DEV1 Productivity Analytics]] |
| 5 | HR Import Onboarding | DataImport | High | [[current-focus/DEV1-hr-import-onboarding\|DEV1 HR Import Onboarding]] |

**Dev 1 Frontend Pages:** Dashboard layout, Employee list/detail/create, Leave management, Productivity reports, HR Import wizard

---

## Task Assignment — Dev 2 (Auth + Lifecycle + Intelligence)

| # | Task | Module | Priority | Task File |
|:--|:-----|:-------|:---------|:----------|
| 1 | Auth & Security | Auth | Critical | [[current-focus/DEV2-auth-security\|DEV2 Auth Security]] |
| 2 | Employee Lifecycle | CoreHR | Critical | [[current-focus/DEV2-core-hr-lifecycle\|DEV2 Core HR Lifecycle]] |
| 3 | Exception Engine | ExceptionEngine | Critical | [[current-focus/DEV2-exception-engine\|DEV2 Exception Engine]] |
| 4 | Notifications | Notifications | High | [[current-focus/DEV2-notifications\|DEV2 Notifications]] |

> Auth task must include `must_change_password`, `password_set_by_admin`, `temporary_password_expires_at` fields on `users` table and the forced-change flow (backend blocks session until password changed).

**Dev 2 Frontend Pages:** Login/MFA/Password reset/Forced-change flow, Role/User management, Onboarding/Offboarding, Exception dashboard, Notification bell + preferences

---

## Task Assignment — Dev 3 (Org + Monitoring + Calendar)

| # | Task | Module | Priority | Task File |
|:--|:-----|:-------|:---------|:----------|
| 1 | Org Structure | OrgStructure | Critical | [[current-focus/DEV3-org-structure\|DEV3 Org Structure]] |
| 2 | Skills Core (Phase 1) | Skills (5 tables) | High | [[current-focus/DEV3-skills-core\|DEV3 Skills Core]] |
| 3 | Workforce Presence (Setup) | WorkforcePresence | Critical | [[current-focus/DEV3-workforce-presence-setup\|DEV3 Workforce Presence Setup]] |
| 4 | Activity Monitoring | ActivityMonitoring | Critical | [[current-focus/DEV3-activity-monitoring\|DEV3 Activity Monitoring]] |
| 5 | Calendar | Calendar | High | [[current-focus/DEV3-calendar\|DEV3 Calendar]] |

> Org Structure task must include `team_roles`, `team_role_permissions`, `team_member_roles` tables for WorkSync team permission stacking.

**Dev 3 Frontend Pages:** Department/Team/Job management, Skill taxonomy admin, Employee skills profile, Shift/Holiday management, Live workforce dashboard, Activity detail/screenshots, Unified calendar

---

## Task Assignment — Dev 4 (Platform + Agent + Presence)

| # | Task | Module | Priority | Task File |
|:--|:-----|:-------|:---------|:----------|
| 1 | Shared Platform + Agent Gateway | SharedPlatform + AgentGateway | Critical | [[current-focus/DEV4-shared-platform-agent-gateway\|DEV4 Shared Platform Agent Gateway]] |
| 2 | Configuration | Configuration | High | [[current-focus/DEV4-configuration\|DEV4 Configuration]] |
| 3 | Identity Verification | IdentityVerification | High | [[current-focus/DEV4-identity-verification\|DEV4 Identity Verification]] |
| 4 | Workforce Presence (Biometric) | WorkforcePresence | Critical | [[current-focus/DEV4-workforce-presence-biometric\|DEV4 Workforce Presence Biometric]] |

> Shared Platform task must include `agent_install_entitlements` and `agent_install_jobs` tables. These are needed by DEV8's IDE extension agent provisioning flow.

**Dev 4 Frontend Pages:** Settings (monitoring config, tenant settings, integrations, retention), Agent management, Biometric devices, Attendance/Overtime, Verification log

---

## Task Assignment — Dev 5 (WorkSync Foundation + Projects + OKR + Time)

| # | Task | Module | Priority | Task File |
|:--|:-----|:-------|:---------|:----------|
| 1 | WorkSync Foundation | WorkSync (workspaces, members, roles) | Critical | [[current-focus/DEV5-wms-foundation\|DEV5 WMS Foundation]] |
| 2 | Project Management | Projects, members, epics, milestones, versions | Critical | [[current-focus/DEV5-wms-foundation\|DEV5 WMS Foundation]] |
| 3 | OKR | Objectives, key results, check-ins | High | [[current-focus/DEV5-wms-foundation\|DEV5 WMS Foundation]] |
| 4 | Time Management | Time logs, timesheets | High | [[current-focus/DEV5-wms-foundation\|DEV5 WMS Foundation]] |
| 5 | Resource Management | Resource plans, allocations | Medium | [[current-focus/DEV5-wms-foundation\|DEV5 WMS Foundation]] |

> WorkSync Foundation (workspaces) is the hardest dependency for DEV6 and DEV7. DEV5 task 1 must complete before DEV6 boards/tasks and DEV7 chat can proceed.

**Dev 5 Frontend Pages:** Workspace switcher, Project list/detail/create, OKR dashboard, Time tracking panel, Resource planner

---

## Task Assignment — Dev 6 (Tasks + Boards + Planning + Analytics)

| # | Task | Module | Priority | Task File |
|:--|:-----|:-------|:---------|:----------|
| 1 | Task Management | Tasks, assignments, checklists, custom fields | Critical | [[current-focus/DEV6-tasks-boards-planning\|DEV6 Tasks Boards Planning]] |
| 2 | Boards + Board Columns | Boards, board_columns, board_task_positions | Critical | [[current-focus/DEV6-tasks-boards-planning\|DEV6 Tasks Boards Planning]] |
| 3 | Sprint Planning | Sprints, sprint_backlog_items, sprint_daily_snapshots (burndown) | Critical | [[current-focus/DEV6-tasks-boards-planning\|DEV6 Tasks Boards Planning]] |
| 4 | Roadmaps | Roadmaps, roadmap_items, baselines (Phase 1 for WorkSync) | High | [[current-focus/DEV6-tasks-boards-planning\|DEV6 Tasks Boards Planning]] |
| 5 | Analytics | Dashboards, chart_widgets, sprint_reports, dashboard_shares, saved_view_shares | High | [[current-focus/DEV6-tasks-boards-planning\|DEV6 Tasks Boards Planning]] |

> Board columns (task 2) require boards (task 1). Burndown snapshots (task 3) require sprints. Roadmaps are Phase 1 for WorkSync — do not defer.

**Dev 6 Frontend Pages:** Task board (Kanban/Scrum), Sprint planning board, Backlog, Burndown chart, Roadmap timeline, Analytics dashboard

---

## Task Assignment — Dev 7 (Chat + AI + My Space + IDE Extension core)

| # | Task | Module | Priority | Task File |
|:--|:-----|:-------|:---------|:----------|
| 1 | Chat | Channels, messages, reactions, attachments | Critical | [[current-focus/DEV7-chat-ai-reminders\|DEV7 Chat AI Reminders]] |
| 2 | Chat AI | Premium AI detection, ai_action_jobs, undo state machine | High | [[current-focus/DEV7-chat-ai-reminders\|DEV7 Chat AI Reminders]] |
| 3 | My Space + Reminders | Personal boards, personal board columns, todos, reminders | High | [[current-focus/DEV7-chat-ai-reminders\|DEV7 Chat AI Reminders]] |
| 4 | IDE Extension Core | VS Code sidebar (Chat panel, Tasks panel, Notifications panel), WebSocket connection | High | [[current-focus/DEV7-chat-ai-reminders\|DEV7 Chat AI Reminders]] |
| 5 | IDE Extension Tag Engine | Tag parser, all @entity:action types, permission validation, ide_tag_executions | High | [[current-focus/DEV7-chat-ai-reminders\|DEV7 Chat AI Reminders]] |

> Chat (task 1) must complete before Chat AI (task 2) — the `messages` table is required. IDE Extension tasks are Weeks 5–6.

**Dev 7 Frontend Pages:** Chat sidebar, Channel/DM view, My Space personal board, Todo list, Reminder notifications
**Dev 7 IDE Extension:** Chat panel, task quick-view, notification feed, `@entity:action` tag parser

---

## Task Assignment — Dev 8 (Documents + GitHub + IDE Tag Engine + Agent Entitlement)

| # | Task | Module | Priority | Task File |
|:--|:-----|:-------|:---------|:----------|
| 1 | Documents (WMS scope) | Documents, document_approvals, wiki_pages, task_documents | Critical | [[current-focus/DEV8-documents-github-ide\|DEV8 Documents GitHub IDE]] |
| 2 | GitHub Integration | Repositories, task_repository_links, code_activity_events | High | [[current-focus/DEV8-documents-github-ide\|DEV8 Documents GitHub IDE]] |
| 3 | CI/CD + Automation | commit_records, pull_request_records, ci_pipeline_runs, task_automation_rules | High | [[current-focus/DEV8-documents-github-ide\|DEV8 Documents GitHub IDE]] |
| 4 | IDE Context Engine | ide_extension_installs, ide_sessions, ide_context_links, branch→task detection | High | [[current-focus/DEV8-documents-github-ide\|DEV8 Documents GitHub IDE]] |
| 5 | IDE Agent Entitlement | agent_install_entitlements check, agent_install_jobs provisioning flow | Critical | [[current-focus/DEV8-documents-github-ide\|DEV8 Documents GitHub IDE]] |

> Documents (task 1) must exist before task_documents join can be created. IDE tasks are Weeks 5–6. Agent entitlement flow depends on DEV4's `agent_install_entitlements` table.

**Dev 8 Frontend Pages:** Document editor, Document approval flow, Wiki page view/edit, GitHub repository linking, CI/CD status on tasks
**Dev 8 IDE Extension:** Context engine (branch→task, file→task), agent install prompt flow

---

## Task Execution Order

### Critical Path

```
DEV1 Infrastructure Setup ──────────────> (all modules depend on this)
DEV2 Auth & Security ───────────────────> (all modules use RBAC from this)
DEV3 Org Structure ─────────────────────> (legal_entities needed by DEV5 workspaces)
DEV5 WorkSync Foundation ───────────────> (workspaces needed by DEV6 + DEV7)
```

These four tasks are the foundation. Everything else can proceed once they are done.

### Cross-Dev Dependencies

```
DEV1 Infrastructure ──────────────────────> unblocks ALL other modules
DEV2 Auth & Security ─────────────────────> unblocks ALL other modules
DEV3 Org Structure ───────────────────────> unblocks DEV3 Skills Core
                                           > unblocks DEV5 WorkSync Foundation (legal_entities)
DEV5 WorkSync Foundation ─────────────────> unblocks DEV6 Tasks + Boards
                                           > unblocks DEV7 Chat + Chat AI
DEV4 Shared Platform + Agent Gateway ─────> unblocks DEV8 IDE agent entitlement
DEV1 Core HR Profile ─────────────────────> unblocks DEV1 HR Import
                                           > unblocks DEV3 Skills Core (employees table)
DEV3 Workforce Presence Setup ────────────> unblocks DEV4 Biometric
DEV3 Activity Monitoring ─────────────────> unblocks DEV1 Productivity Analytics
DEV7 Chat ────────────────────────────────> unblocks DEV7 Chat AI
DEV8 Documents ───────────────────────────> unblocks DEV8 task_documents
DEV6 Boards + Sprints ────────────────────> unblocks DEV6 Burndown snapshots
DEV7 IDE Extension Core (Week 5) ─────────> unblocks DEV7 Tag Engine (Week 6)
DEV8 IDE Context Engine (Week 5) ─────────> unblocks DEV8 Agent Entitlement flow (Week 6)
```

---

## What We Are NOT Working On Right Now

- **Payroll** — deferred to Phase 2
- **Performance** — deferred to Phase 2
- **Grievance** — deferred to Phase 2
- **Expense** — deferred to Phase 2
- **Skills & Learning (LMS)** — 5 core tables are Phase 1 (see DEV3 Skills Core). Courses, assessments, dev plans, certifications deferred to Phase 2
- **KPI Targets** — WorkSync Phase 2 feature
- **Billable Rates** — WorkSync Phase 2 feature
- **JetBrains Plugin** — IDE extension Phase 1 is VS Code only; JetBrains in Phase 2
- **MacOS Desktop Agent** — Windows only in Phase 1
- **Teams Graph API deep integration** — Phase 2; Phase 1 uses process-name detection
- **Meilisearch** — PostgreSQL FTS sufficient for Phase 1
- **RabbitMQ** — using in-process domain events; RabbitMQ for scale later
- **Bridge APIs** — `WMS-bridge-integration.md` is DEPRECATED. WorkSync is internal.

---

## Milestones

| Milestone | Scope | Notes |
|:----------|:------|:------|
| Foundation | DEV1 infra + DEV2 auth + DEV3 org + DEV5 workspaces | All other tasks depend on this |
| HR Core complete | DEV1/2/3/4 tasks 1–2 | Employee, lifecycle, presence, auth flows working |
| WorkSync Core complete | DEV5/6/7/8 tasks 1–2 | Projects, tasks, boards, chat working |
| Intelligence + Planning | DEV1/2/3/4 tasks 3–4 + DEV5/6/7/8 tasks 3–4 | Leave, exception, monitoring, sprints, roadmaps |
| IDE Extension core | DEV7/8 Weeks 5–6 | Chat sidebar, tag engine, agent entitlement |
| Integration testing | All devs | Cross-module flows, WorkSync ↔ HR, IDE ↔ backend |
| Deployment ready | All devs | Load testing, security review |

---

## Frontend Phase (Per Module)

Each dev builds the frontend for their module **immediately after** completing the backend for that module.

### Key Frontend Resources

**Shell layout:**
- [[frontend/design-system/components/shell-layout|Shell Layout]] — floating-cards layout
- [[frontend/design-system/components/nav-rail|Nav Rail]] — icon rail (52px, dark, pillars)
- [[frontend/design-system/components/expansion-panel|Expansion Panel]] — slide-out panel
- [[frontend/architecture/topbar|Topbar]] — topbar with workspace switcher

**General:**
- [[frontend/architecture/app-structure|Frontend Structure]] — Next.js app directory layout
- [[frontend/design-system/README|Design System]] — shadcn/ui components, design tokens
- [[frontend/data-layer/api-integration|API Integration]] — API client, error handling, pagination
- [[frontend/data-layer/state-management|State Management]] — TanStack Query + Zustand

---

## Related

- [[AI_CONTEXT/project-context|Project Context]]
- [[AI_CONTEXT/tech-stack|Tech Stack]]
- [[backend/module-catalog|Module Catalog]]
- [[database/schema-catalog|Schema Catalog]]
- [[onevo-unified-entity-map|Entity Map]]
- [[modules/ide-extension/overview|IDE Extension Spec]]
- [[AI_CONTEXT/rules|Rules]]
- [[AI_CONTEXT/known-issues|Known Issues]]
