# Current Focus: ONEVO

**Current Phase:** Phase 1
**Team Size:** 4 developers
**Development Approach:** Agentic Development Environment (AI-assisted)

---

## How to Use This Folder

Each file below is a **self-contained task** for one developer. It includes:
1. **Step 1: Backend** — acceptance criteria, module docs links
2. **Step 2: Frontend** — pages to build, userflow links, API endpoints to consume

The dev builds backend first, then frontend for the same module. Each task file links to the relevant [[Userflow/README|Userflows]] so the AI knows the full user journey and API contracts.

---

## Task Assignment — Dev 1

| # | Task | Module | Priority | Task File |
|:--|:-----|:-------|:---------|:----------|
| 1 | Infrastructure & Foundation | Infrastructure + SharedKernel | Critical | [[current-focus/DEV1-infrastructure-setup\|DEV1 Infrastructure Setup]] |
| 2 | Employee Profile | CoreHR | Critical | [[current-focus/DEV1-core-hr-profile\|DEV1 Core Hr Profile]] |
| 3 | Leave | Leave | High | [[current-focus/DEV1-leave\|DEV1 Leave]] |
| 4 | Productivity Analytics | ProductivityAnalytics | High | [[current-focus/DEV1-productivity-analytics\|DEV1 Productivity Analytics]] |
| 5 | HR Import Onboarding | DataImport | High | [[current-focus/DEV1-hr-import-onboarding\|DEV1 HR Import Onboarding]] |

> Task 5 depends on Task 2 (Employee Profile) for the `employees` table target, DEV2 Auth for `employees:write` permission, and DEV3 Org Structure for department/job-family resolution in the ETL pipeline. Task 12 (Integrations Screen under Settings) is co-owned with Dev 4 — coordinate placement in `/settings/integrations`.

**Dev 1 Frontend Pages:** Dashboard layout, Employee list/detail/create, Leave management, Productivity reports, HR Import wizard (`/hr/import`)

---

## Task Assignment — Dev 2

| # | Task | Module | Priority | Task File |
|:--|:-----|:-------|:---------|:----------|
| 1 | Auth & Security | Auth | Critical | [[current-focus/DEV2-auth-security\|DEV2 Auth Security]] |
| 2 | Employee Lifecycle | CoreHR | Critical | [[current-focus/DEV2-core-hr-lifecycle\|DEV2 Core Hr Lifecycle]] |
| 3 | Exception Engine | ExceptionEngine | Critical | [[current-focus/DEV2-exception-engine\|DEV2 Exception Engine]] |
| 4 | Notifications | Notifications | High | [[current-focus/DEV2-notifications\|DEV2 Notifications]] |

**Dev 2 Frontend Pages:** Login/MFA/Password reset, Role/User management, Onboarding/Offboarding, Exception dashboard, Notification bell + preferences

---

## Task Assignment — Dev 3

| # | Task | Module | Priority | Task File |
|:--|:-----|:-------|:---------|:----------|
| 1 | Org Structure | OrgStructure | Critical | [[current-focus/DEV3-org-structure\|DEV3 Org Structure]] |
| 2 | Skills Core (Phase 1) | Skills (5 tables) | High | [[current-focus/DEV3-skills-core\|DEV3 Skills Core]] |
| 3 | Calendar | Calendar | High | [[current-focus/DEV3-calendar\|DEV3 Calendar]] |
| 4 | Workforce Presence (Setup) | WorkforcePresence | Critical | [[current-focus/DEV3-workforce-presence-setup\|DEV3 Workforce Presence Setup]] |
| 5 | Activity Monitoring | ActivityMonitoring | Critical | [[current-focus/DEV3-activity-monitoring\|DEV3 Activity Monitoring]] |

> Task 2 (Skills Core) depends on Task 1 (Org Structure) completing job families first. The job skill requirements UI on the job families page is the connection point.

**Dev 3 Frontend Pages:** Department/Team/Job management, Skill taxonomy admin, Employee skills profile, My Skills self-service, Unified calendar, Shift/Holiday management, Live workforce dashboard, Activity detail/screenshots

---

## Task Assignment — Dev 4

| # | Task | Module | Priority | Task File |
|:--|:-----|:-------|:---------|:----------|
| 1 | Shared Platform + Agent Gateway | SharedPlatform + AgentGateway | Critical | [[current-focus/DEV4-shared-platform-agent-gateway\|DEV4 Shared Platform Agent Gateway]] |
| 2 | Configuration | Configuration | High | [[current-focus/DEV4-configuration\|DEV4 Configuration]] |
| 3 | Identity Verification | IdentityVerification | High | [[current-focus/DEV4-identity-verification\|DEV4 Identity Verification]] |
| 4 | Workforce Presence (Biometric) | WorkforcePresence | Critical | [[current-focus/DEV4-workforce-presence-biometric\|DEV4 Workforce Presence Biometric]] |

**Dev 4 Frontend Pages:** Settings (monitoring config, tenant settings, integrations, retention), Agent management, Biometric devices, Attendance/Overtime, Verification log

---

## Task Execution Order

Tasks are numbered 1-4 per developer. **Task 1 should be built first** (it's the foundation). Tasks 2-4 proceed after task 1 is complete, but some have cross-dev dependencies noted in each task file.

### Critical Path

```
DEV1: Infrastructure Setup ──> (all other tasks depend on this)
DEV2: Auth & Security ──────> (all modules use RBAC from this)
```

These two tasks **must be completed first** before other devs can make progress.

### Cross-Dev Dependencies

```
DEV3 Org Structure (task 1) ──> unblocks DEV3 Skills Core (task 2) [job families needed for skill requirements]
DEV3 Skills Core (task 2) ──> unblocks Required Skills tab in DEV3 Org Structure job families page
DEV3 Calendar (task 3) ──> unblocks DEV1 Leave (task 3)
DEV3 Workforce Presence Setup (task 4) ──> unblocks DEV4 Biometric (task 4)
DEV3 Activity Monitoring (task 5) ──> unblocks DEV1 Productivity Analytics (task 4)
DEV4 Shared Platform (task 1) ──> unblocks DEV2 Notifications (task 4)
DEV1 Core HR Profile (task 2) ──> needed by DEV3 Skills Core (employees table for employee_skills)
DEV1 Core HR Profile (task 2) ──> unblocks DEV1 HR Import Onboarding (task 5) [employees table target for bulk writes]
DEV3 Org Structure (task 1) ──> unblocks DEV1 HR Import Onboarding (task 5) [departments + job families for ETL resolution]
DEV2 Auth & Security (task 1) ──> unblocks DEV1 HR Import Onboarding (task 5) [employees:write permission required]
```

---

## What We Are NOT Working On Right Now

- **Payroll** — deferred to Phase 2
- **Performance** — deferred to Phase 2
- **Documents** — deferred to Phase 2
- **Grievance** — deferred to Phase 2
- **Expense** — deferred to Phase 2
- **Reporting Engine** — deferred to Phase 2
- **Skills & Learning (partial)** — 5 core tables (`skill_categories`, `skills`, `job_skill_requirements`, `employee_skills`, `skill_validation_requests`) are Phase 1 (see [[current-focus/DEV3-skills-core|DEV3 Skills Core]]). LMS integrations, courses, assessments, development plans, certifications — deferred to Phase 2
- **AI Chatbot (Nexis)** — deferred to Phase 2
- **Mobile Application (Flutter)** — deferred to Phase 2
- **WorkManage Pro Bridges (Phase 2)** — Productivity Metrics + Skills bidirectional bridges are Phase 2. **People Sync, Availability, and Work Activity bridges are Phase 1** — see [[current-focus/WMS-bridge-integration|WMS Bridge Integration]]
- **Desktop Agent code** — in scope, follows Agent Gateway completion (see `agent/AI_CONTEXT/`)
- **Teams Graph API deep integration** — Phase 2; Phase 1 uses process name detection
- **Meilisearch** — PostgreSQL FTS sufficient for Phase 1
- **RabbitMQ** — using in-process domain events; RabbitMQ for scale later

---

## Milestones

| Milestone | Scope | Notes |
|:----------|:------|:------|
| Foundation complete | DEV1 task 1 + DEV2 task 1 | All other tasks depend on this |
| Core modules complete | All devs task 2 | Calendar, Lifecycle, Configuration, Employee Profile |
| Extended modules complete | All devs task 3 | Leave, Exception Engine, Presence, Identity Verification |
| All Phase 1 modules complete | All devs task 4 | Productivity, Notifications, Activity Monitoring, Biometric |
| Integration testing | All devs | Buffer for cross-module testing |

---

## Frontend Phase (Per Module)

Each dev builds the frontend for their module **immediately after** completing the backend for that module. Frontend tasks are defined in each task file under "Step 2: Frontend".

### Key Frontend Resources

- [[frontend/architecture/app-structure|Frontend Structure]] — Next.js app directory layout
- [[frontend/design-system/README|Design System]] — shadcn/ui components, design tokens
- [[frontend/design-system/components/component-catalog|Component Catalog]] — all UI components
- [[frontend/data-layer/api-integration|API Integration]] — API client, error handling, pagination
- [[frontend/data-layer/state-management|State Management]] — TanStack Query + Zustand
- [[frontend/coding-standards|Frontend Coding Standards]] — conventions

### Frontend Priority Order (if time is tight)

1. **Auth flow** — login, MFA, token management (DEV2)
2. **Dashboard layout** — sidebar, topbar, permission-based navigation (DEV1)
3. **Workforce Intelligence pages** — live dashboard, activity detail, exceptions (DEV3 + DEV2)
4. **HR pages** — employees, leave, calendar (DEV1 + DEV3)
5. **Settings** — monitoring configuration, tenant settings (DEV4)
6. **Employee self-service** — own dashboard, own leave (DEV1)

---

## WMS Bridge Integration (Cross-Dev)

| Task | Owner | Phase | Task File |
|:-----|:------|:------|:----------|
| Knowledge Brain Fixes (docs only) | All devs | Before code | [[docs/wms-integration-analysis\|WMS Integration Analysis]] |
| People Sync Bridge | Dev 2 | Phase 1 | [[current-focus/WMS-bridge-integration\|WMS Bridge Integration]] |
| Availability Bridge | Dev 1 | Phase 1 | [[current-focus/WMS-bridge-integration\|WMS Bridge Integration]] |
| Work Activity Bridge | Dev 1 | Phase 1 | [[current-focus/WMS-bridge-integration\|WMS Bridge Integration]] |
| Productivity Metrics Bridge | Dev 1 | Phase 2 | [[current-focus/WMS-bridge-integration\|WMS Bridge Integration]] |
| Skills Bridge (bidirectional) | Dev 3 | Phase 2 | [[current-focus/WMS-bridge-integration\|WMS Bridge Integration]] |
| WMS Tenant Provisioning + Role Mapping | Dev 4 | Phase 1 | [[current-focus/WMS-bridge-integration\|WMS Bridge Integration]] |

> **⚠ Knowledge brain fixes must be done before any bridge code is written.** See [[docs/wms-integration-analysis|WMS Integration Analysis]] for the full issue list and open questions.

---

## Related

- [[AI_CONTEXT/project-context|Project Context]]
- [[AI_CONTEXT/tech-stack|Tech Stack]]
- [[backend/module-catalog|Module Catalog]]
- [[AI_CONTEXT/rules|Rules]]
- [[AI_CONTEXT/known-issues|Known Issues]]
- [[ade/README|ADE Orchestrator Instructions]]
