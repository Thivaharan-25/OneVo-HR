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
| 1 | Infrastructure & Foundation | Infrastructure + SharedKernel | Critical | [[current-focus/DEV1-infrastructure-setup|DEV1 Infrastructure Setup]] |
| 2 | Employee Profile | CoreHR | Critical | [[current-focus/DEV1-core-hr-profile|DEV1 Core Hr Profile]] |
| 3 | Leave | Leave | High | [[current-focus/DEV1-leave|DEV1 Leave]] |
| 4 | Productivity Analytics | ProductivityAnalytics | High | [[current-focus/DEV1-productivity-analytics|DEV1 Productivity Analytics]] |

**Dev 1 Frontend Pages:** Dashboard layout, Employee list/detail/create, Leave management, Productivity reports

---

## Task Assignment — Dev 2

| # | Task | Module | Priority | Task File |
|:--|:-----|:-------|:---------|:----------|
| 1 | Auth & Security | Auth | Critical | [[current-focus/DEV2-auth-security|DEV2 Auth Security]] |
| 2 | Employee Lifecycle | CoreHR | Critical | [[current-focus/DEV2-core-hr-lifecycle|DEV2 Core Hr Lifecycle]] |
| 3 | Exception Engine | ExceptionEngine | Critical | [[current-focus/DEV2-exception-engine|DEV2 Exception Engine]] |
| 4 | Notifications | Notifications | High | [[current-focus/DEV2-notifications|DEV2 Notifications]] |

**Dev 2 Frontend Pages:** Login/MFA/Password reset, Role/User management, Onboarding/Offboarding, Exception dashboard, Notification bell + preferences

---

## Task Assignment — Dev 3

| # | Task | Module | Priority | Task File |
|:--|:-----|:-------|:---------|:----------|
| 1 | Org Structure | OrgStructure | Critical | [[current-focus/DEV3-org-structure|DEV3 Org Structure]] |
| 2 | Calendar | Calendar | High | [[current-focus/DEV3-calendar|DEV3 Calendar]] |
| 3 | Workforce Presence (Setup) | WorkforcePresence | Critical | [[current-focus/DEV3-workforce-presence-setup|DEV3 Workforce Presence Setup]] |
| 4 | Activity Monitoring | ActivityMonitoring | Critical | [[current-focus/DEV3-activity-monitoring|DEV3 Activity Monitoring]] |

**Dev 3 Frontend Pages:** Department/Team/Job management, Unified calendar, Shift/Holiday management, Live workforce dashboard, Activity detail/screenshots

---

## Task Assignment — Dev 4

| # | Task | Module | Priority | Task File |
|:--|:-----|:-------|:---------|:----------|
| 1 | Shared Platform + Agent Gateway | SharedPlatform + AgentGateway | Critical | [[current-focus/DEV4-shared-platform-agent-gateway|DEV4 Shared Platform Agent Gateway]] |
| 2 | Configuration | Configuration | High | [[current-focus/DEV4-configuration|DEV4 Configuration]] |
| 3 | Identity Verification | IdentityVerification | High | [[current-focus/DEV4-identity-verification|DEV4 Identity Verification]] |
| 4 | Workforce Presence (Biometric) | WorkforcePresence | Critical | [[current-focus/DEV4-workforce-presence-biometric|DEV4 Workforce Presence Biometric]] |

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
DEV3 Calendar (task 2) ──> unblocks DEV1 Leave (task 3)
DEV3 Workforce Presence Setup (task 3) ──> unblocks DEV4 Biometric (task 4)
DEV3 Activity Monitoring (task 4) ──> unblocks DEV1 Productivity Analytics (task 4)
DEV4 Shared Platform (task 1) ──> unblocks DEV2 Notifications (task 4)
```

---

## What We Are NOT Working On Right Now

- **Payroll** — deferred to Phase 2
- **Performance** — deferred to Phase 2
- **Documents** — deferred to Phase 2
- **Grievance** — deferred to Phase 2
- **Expense** — deferred to Phase 2
- **Reporting Engine** — deferred to Phase 2
- **Skills & Learning** — deferred to Phase 2
- **AI Chatbot (Nexis)** — deferred to Phase 2
- **Mobile Application (Flutter)** — deferred to Phase 2
- **WorkManage Pro Bridges** — deferred to Phase 2
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

## Related

- [[AI_CONTEXT/project-context|Project Context]]
- [[AI_CONTEXT/tech-stack|Tech Stack]]
- [[backend/module-catalog|Module Catalog]]
- [[AI_CONTEXT/rules|Rules]]
- [[AI_CONTEXT/known-issues|Known Issues]]
- [[ade/README|ADE Orchestrator Instructions]]
