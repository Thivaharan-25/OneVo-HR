# Unified Brain Restructure — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Restructure the Obsidian knowledge brain from 3 isolated silos (backend/frontend/agent) into one unified, fully interconnected brain where every file links to related files via `[[wikilinks]]`.

**Architecture:** Merge all docs into a flat structure: `modules/` (unified backend+frontend+agent per feature), `cross-cutting/` (shared concerns), `current-focus/` (one file per task), `architecture/` (high-level). Every file gets a `## Related` section with wikilinks.

**Tech Stack:** Obsidian markdown, `[[wikilinks]]` for interconnection

---

## Frontend → Module Feature Mapping

These frontend page specs get split into `frontend.md` files inside the relevant module feature folders:

| Frontend Page | Target Module Feature(s) |
|:---|:---|
| `employees.md` | `core-hr/employee-profiles/frontend.md` |
| `leave.md` | `leave/leave-requests/frontend.md` |
| `performance.md` | `performance/review-cycles/frontend.md` |
| `payroll.md` | `payroll/payroll-execution/frontend.md` |
| `live-dashboard.md` | `workforce-presence/presence-sessions/frontend.md` |
| `employee-activity.md` | `activity-monitoring/application-tracking/frontend.md` |
| `reports.md` | `productivity-analytics/daily-reports/frontend.md` |
| `exceptions.md` | `exception-engine/alert-generation/frontend.md` |
| `settings.md` | `configuration/tenant-settings/frontend.md` |
| `overview-dashboard.md` | `shared-platform/overview-dashboard/frontend.md` (new feature folder) |
| `self-service.md` | `shared-platform/self-service/frontend.md` (new feature folder) |

## Cross-Cutting Mapping

| Source Files | Target |
|:---|:---|
| `backend/docs/security/*` + `frontend/docs/security/*` | `cross-cutting/security/` |
| `backend/docs/database/*` | `cross-cutting/database/` |
| `backend/docs/architecture/messaging/*` | `cross-cutting/messaging/` |
| `backend/docs/deployment/*` | `cross-cutting/deployment/` |
| `backend/docs/operations/*` | `cross-cutting/observability/` |
| `backend/docs/testing/*` + `frontend/docs/guides/testing.md` | `cross-cutting/testing/` |
| `backend/docs/guides/*` + `frontend/docs/guides/coding-standards.md` | `cross-cutting/guides/` |
| `backend/docs/architecture/multi-tenancy.md` | `cross-cutting/multi-tenancy.md` |
| `frontend/docs/design-system/*` | `design-system/` |

## Agent Docs Mapping

| Source | Target |
|:---|:---|
| `agent/docs/architecture/agent-server-protocol.md` | `modules/agent-gateway/agent-server-protocol.md` |
| `agent/docs/architecture/data-collection.md` | `modules/agent-gateway/data-collection.md` |
| `agent/docs/architecture/photo-capture.md` | `modules/identity-verification/photo-capture.md` |
| `agent/docs/architecture/tamper-resistance.md` | `modules/agent-gateway/tamper-resistance.md` |

---

### Task 1: Create New Folder Structure

**Files:**
- Create: `modules/`, `cross-cutting/security/`, `cross-cutting/database/`, `cross-cutting/messaging/`, `cross-cutting/deployment/`, `cross-cutting/observability/`, `cross-cutting/testing/`, `cross-cutting/guides/`, `architecture/`, `design-system/`, `current-focus/`
- Create: `modules/shared-platform/overview-dashboard/`, `modules/shared-platform/self-service/`

- [x] **Step 1: Create all target directories**

```bash
# Module directories (mirror existing backend module structure)
mkdir -p modules/activity-monitoring/{application-tracking,daily-aggregation,device-tracking,meeting-detection,raw-data-processing,screenshots}
mkdir -p modules/agent-gateway/{agent-registration,data-ingestion,heartbeat-monitoring,policy-distribution}
mkdir -p modules/auth/{audit-logging,authentication,authorization,gdpr-consent,mfa,session-management}
mkdir -p modules/calendar/{calendar-events,conflict-detection}
mkdir -p modules/configuration/{employee-overrides,integrations,monitoring-toggles,retention-policies,tenant-settings}
mkdir -p modules/core-hr/{compensation,dependents-contacts,employee-lifecycle,employee-profiles,offboarding,onboarding,qualifications}
mkdir -p modules/documents/{access-control,acknowledgements,categories,document-management,templates}
mkdir -p modules/exception-engine/{alert-generation,escalation-chains,evaluation-engine,exception-rules}
mkdir -p modules/expense/{expense-categories,expense-claims}
mkdir -p modules/grievance/{disciplinary-actions,grievance-cases}
mkdir -p modules/identity-verification/{biometric-devices,biometric-enrollment,photo-verification,verification-policies}
mkdir -p modules/infrastructure/{file-management,reference-data,tenant-management,user-management}
mkdir -p modules/leave/{balance-audit,leave-entitlements,leave-policies,leave-requests,leave-types}
mkdir -p modules/notifications/{notification-channels,notification-templates,signalr-real-time}
mkdir -p modules/org-structure/{cost-centers,departments,job-hierarchy,legal-entities,teams}
mkdir -p modules/payroll/{adjustments,allowances,audit-trail,payroll-execution,payroll-providers,pensions,tax-configuration}
mkdir -p modules/performance/{feedback,goals-okr,improvement-plans,recognitions,review-cycles,reviews,succession-planning}
mkdir -p modules/productivity-analytics/{daily-reports,monthly-reports,weekly-reports,workforce-snapshots}
mkdir -p modules/reporting-engine/{report-definitions,report-execution,report-templates}
mkdir -p modules/shared-platform/{compliance-governance,feature-flags,hardware-terminals,notification-infrastructure,real-time-integrations,sso-authentication,subscriptions-billing,tenant-branding,workflow-engine,overview-dashboard,self-service}
mkdir -p modules/skills/{certifications,courses-learning,development-plans,employee-skills,skill-assessments,skill-taxonomy}
mkdir -p modules/workforce-presence/{attendance-corrections,break-tracking,device-sessions,overtime,presence-sessions,shifts-schedules}

# Cross-cutting
mkdir -p cross-cutting/{security,database,messaging,deployment,observability,testing,guides}

# Architecture & design-system
mkdir -p architecture
mkdir -p design-system

# Current focus
mkdir -p current-focus
```

- [x] **Step 2: Verify directories created**

```bash
ls modules/ | wc -l
# Expected: 22

ls cross-cutting/
# Expected: security database messaging deployment observability testing guides
```

- [x] **Step 3: Commit**

```bash
git add modules/ cross-cutting/ architecture/ design-system/ current-focus/
git commit -m "docs: create unified brain folder structure"
```

---

### Task 2: Move Module Docs (Backend → Unified modules/)

**Files:**
- Move: All files from `backend/docs/architecture/modules/*` → `modules/*`

- [x] **Step 1: Copy all module content to new location**

```bash
# Copy all 22 module folders with their feature subfolders
cp -r backend/docs/architecture/modules/* modules/
```

- [x] **Step 2: Verify file count matches**

```bash
find modules/ -name "*.md" | wc -l
find backend/docs/architecture/modules/ -name "*.md" | wc -l
# Both should output the same number
```

- [x] **Step 3: Commit**

```bash
git add modules/
git commit -m "docs: copy backend module docs to unified modules/"
```

---

### Task 3: Merge Frontend Page Specs into Module Feature Folders

**Files:**
- Read: `frontend/docs/pages/pillar1-hr/employees.md` → Write: `modules/core-hr/employee-profiles/frontend.md`
- Read: `frontend/docs/pages/pillar1-hr/leave.md` → Write: `modules/leave/leave-requests/frontend.md`
- Read: `frontend/docs/pages/pillar1-hr/performance.md` → Write: `modules/performance/review-cycles/frontend.md`
- Read: `frontend/docs/pages/pillar1-hr/payroll.md` → Write: `modules/payroll/payroll-execution/frontend.md`
- Read: `frontend/docs/pages/pillar2-workforce/live-dashboard.md` → Write: `modules/workforce-presence/presence-sessions/frontend.md`
- Read: `frontend/docs/pages/pillar2-workforce/employee-activity.md` → Write: `modules/activity-monitoring/application-tracking/frontend.md`
- Read: `frontend/docs/pages/pillar2-workforce/reports.md` → Write: `modules/productivity-analytics/daily-reports/frontend.md`
- Read: `frontend/docs/pages/pillar2-workforce/exceptions.md` → Write: `modules/exception-engine/alert-generation/frontend.md`
- Read: `frontend/docs/pages/pillar2-workforce/settings.md` → Write: `modules/configuration/tenant-settings/frontend.md`
- Read: `frontend/docs/pages/shared/overview-dashboard.md` → Write: `modules/shared-platform/overview-dashboard/frontend.md`
- Read: `frontend/docs/pages/shared/self-service.md` → Write: `modules/shared-platform/self-service/frontend.md`

- [x] **Step 1: Copy each frontend page spec to its module feature folder, adding a Related section with wikilinks**

For each file, copy it and append a `## Related` section linking back to the backend feature it belongs to. Example for `employees.md`:

```bash
cp frontend/docs/pages/pillar1-hr/employees.md modules/core-hr/employee-profiles/frontend.md
```

Then edit `modules/core-hr/employee-profiles/frontend.md` to append:

```markdown

## Related

- [[modules/core-hr/employee-profiles/overview|Backend: Employee Profiles]] — API and data model
- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]] — onboarding/offboarding flows
- [[security/auth-architecture|Auth Architecture]] — permission checks
- [[frontend/cross-cutting/authorization|RBAC]] — `employees:read`, `employees:write` permissions
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant-scoped queries
- [[current-focus/DEV1-core-hr-profile|DEV1: Core HR Profile]] — implementation task
```

- [x] **Step 2: Repeat for all 11 frontend page specs**

Full mapping (copy source → dest, then add Related section):

```bash
cp frontend/docs/pages/pillar1-hr/employees.md modules/core-hr/employee-profiles/frontend.md
cp frontend/docs/pages/pillar1-hr/leave.md modules/leave/leave-requests/frontend.md
cp frontend/docs/pages/pillar1-hr/performance.md modules/performance/review-cycles/frontend.md
cp frontend/docs/pages/pillar1-hr/payroll.md modules/payroll/payroll-execution/frontend.md
cp frontend/docs/pages/pillar2-workforce/live-dashboard.md modules/workforce-presence/presence-sessions/frontend.md
cp frontend/docs/pages/pillar2-workforce/employee-activity.md modules/activity-monitoring/application-tracking/frontend.md
cp frontend/docs/pages/pillar2-workforce/reports.md modules/productivity-analytics/daily-reports/frontend.md
cp frontend/docs/pages/pillar2-workforce/exceptions.md modules/exception-engine/alert-generation/frontend.md
cp frontend/docs/pages/pillar2-workforce/settings.md modules/configuration/tenant-settings/frontend.md
cp frontend/docs/pages/shared/overview-dashboard.md modules/shared-platform/overview-dashboard/frontend.md
cp frontend/docs/pages/shared/self-service.md modules/shared-platform/self-service/frontend.md
```

Each `frontend.md` gets a `## Related` section with links to:
- Its backend feature overview
- Related cross-cutting concerns (auth, multi-tenancy)
- Its implementation task file

- [x] **Step 3: Copy frontend architecture docs into cross-cutting or architecture**

```bash
cp frontend/docs/architecture/api-integration.md cross-cutting/guides/frontend-api-integration.md
cp frontend/docs/architecture/monitoring-data-flow.md architecture/monitoring-data-flow.md
cp frontend/docs/architecture/real-time.md architecture/real-time.md
cp frontend/docs/architecture/state-management.md architecture/frontend-state-management.md
```

- [x] **Step 4: Commit**

```bash
git add modules/ architecture/ cross-cutting/
git commit -m "docs: merge frontend page specs into unified module feature folders"
```

---

### Task 4: Merge Agent Docs into Module Folders

**Files:**
- Copy: `agent/docs/architecture/agent-server-protocol.md` → `modules/agent-gateway/agent-server-protocol.md`
- Copy: `agent/docs/architecture/data-collection.md` → `modules/agent-gateway/data-collection.md`
- Copy: `agent/docs/architecture/tamper-resistance.md` → `modules/agent-gateway/tamper-resistance.md`
- Copy: `agent/docs/architecture/photo-capture.md` → `modules/identity-verification/photo-capture.md`

- [x] **Step 1: Copy agent docs to their module homes**

```bash
cp agent/docs/architecture/agent-server-protocol.md modules/agent-gateway/agent-server-protocol.md
cp agent/docs/architecture/data-collection.md modules/agent-gateway/data-collection.md
cp agent/docs/architecture/tamper-resistance.md modules/agent-gateway/tamper-resistance.md
cp agent/docs/architecture/photo-capture.md modules/identity-verification/photo-capture.md
```

- [x] **Step 2: Add Related sections to each file**

For `modules/agent-gateway/agent-server-protocol.md`, append:
```markdown

## Related

- [[modules/agent-gateway/overview|Agent Gateway Module]] — parent module overview
- [[modules/agent-gateway/data-ingestion/overview|Data Ingestion]] — how agent sends data to server
- [[modules/agent-gateway/heartbeat-monitoring/overview|Heartbeat]] — agent health checks
- [[modules/agent-gateway/tamper-resistance|Tamper Resistance]] — anti-tamper protections
- [[security/auth-architecture|Auth Architecture]] — device JWT authentication
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]] — implementation task
```

For `modules/agent-gateway/data-collection.md`, append:
```markdown

## Related

- [[modules/agent-gateway/agent-server-protocol|Agent Server Protocol]] — communication protocol
- [[modules/activity-monitoring/raw-data-processing/overview|Raw Data Processing]] — how server processes collected data
- [[modules/activity-monitoring/application-tracking/overview|Application Tracking]] — app usage tracking
- [[modules/activity-monitoring/device-tracking/overview|Device Tracking]] — device activity tracking
- [[security/data-classification|Data Classification]] — PII/RESTRICTED classification for collected data
- [[modules/configuration/retention-policies/overview|Retention Policies]] — data retention rules
```

For `modules/agent-gateway/tamper-resistance.md`, append:
```markdown

## Related

- [[modules/agent-gateway/agent-server-protocol|Agent Server Protocol]] — secure communication
- [[security/auth-architecture|Auth Architecture]] — device JWT, HMAC
- [[security/compliance|Compliance]] — security requirements
```

For `modules/identity-verification/photo-capture.md`, append:
```markdown

## Related

- [[modules/identity-verification/overview|Identity Verification Module]] — parent module
- [[modules/identity-verification/photo-verification/overview|Photo Verification]] — server-side verification
- [[modules/identity-verification/biometric-enrollment/overview|Biometric Enrollment]] — biometric data enrollment
- [[modules/identity-verification/verification-policies/overview|Verification Policies]] — when photos are required
- [[security/data-classification|Data Classification]] — RESTRICTED classification for photos
```

- [x] **Step 3: Copy agent AI_CONTEXT info into root AI_CONTEXT**

The agent `project-context.md` content should be merged into root `AI_CONTEXT/project-context.md` as a "Desktop Agent" section.

- [x] **Step 4: Commit**

```bash
git add modules/ AI_CONTEXT/
git commit -m "docs: merge agent docs into unified module folders"
```

---

### Task 5: Move Cross-Cutting Docs

**Files:**
- Copy: `backend/docs/security/*` → `cross-cutting/security/`
- Copy: `frontend/docs/security/*` → `cross-cutting/security/`
- Copy: `backend/docs/database/*` → `cross-cutting/database/`
- Copy: `backend/docs/architecture/messaging/*` → `cross-cutting/messaging/`
- Copy: `backend/docs/deployment/*` → `cross-cutting/deployment/`
- Copy: `backend/docs/operations/*` → `cross-cutting/observability/`
- Copy: `backend/docs/testing/*` → `cross-cutting/testing/`
- Copy: `backend/docs/guides/*` → `cross-cutting/guides/`
- Copy: `frontend/docs/guides/*` → `cross-cutting/guides/` (merge)
- Copy: `backend/docs/architecture/multi-tenancy.md` → `cross-cutting/multi-tenancy.md`

- [x] **Step 1: Copy all cross-cutting docs**

```bash
# Security (merge backend + frontend)
cp backend/docs/security/* cross-cutting/security/
cp frontend/docs/security/* cross-cutting/security/

# Database
cp backend/docs/database/* cross-cutting/database/

# Messaging
cp backend/docs/architecture/messaging/* cross-cutting/messaging/

# Deployment
cp backend/docs/deployment/* cross-cutting/deployment/

# Observability (from operations)
cp backend/docs/operations/* cross-cutting/observability/
cp -r backend/docs/operations/runbooks cross-cutting/observability/runbooks

# Testing (merge backend + frontend)
cp backend/docs/testing/* cross-cutting/testing/
cp frontend/docs/guides/testing.md cross-cutting/testing/frontend-testing.md

# Guides (merge backend + frontend)
cp backend/docs/guides/* cross-cutting/guides/
cp frontend/docs/guides/coding-standards.md cross-cutting/guides/frontend-coding-standards.md

# Multi-tenancy (standalone)
cp backend/docs/architecture/multi-tenancy.md cross-cutting/multi-tenancy.md
```

- [x] **Step 2: Add Related sections to each cross-cutting doc**

For `cross-cutting/security/auth-architecture.md`, append:
```markdown

## Related

- [[frontend/cross-cutting/authentication|Authentication]] — login flow feature
- [[frontend/cross-cutting/authorization|Authorization]] — RBAC feature
- [[mfa]] — multi-factor auth feature
- [[modules/auth/session-management/overview|Session Management]] — session tracking
- [[modules/agent-gateway/agent-server-protocol|Agent Server Protocol]] — device JWT
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant isolation
- [[security/compliance|Compliance]] — GDPR, PDPA, OWASP
- [[security/data-classification|Data Classification]] — PII inventory
- [[current-focus/DEV2-auth-security|DEV2: Auth Security]] — implementation task
```

For `cross-cutting/security/data-classification.md`, append:
```markdown

## Related

- [[security/auth-architecture|Auth Architecture]] — encryption, access control
- [[modules/configuration/retention-policies/overview|Retention Policies]] — data retention per classification
- [[modules/activity-monitoring/screenshots/overview|Screenshots]] — RESTRICTED data
- [[modules/identity-verification/photo-capture|Photo Capture]] — RESTRICTED data
- [[security/compliance|Compliance]] — GDPR rights
- [[code-standards/logging-standards|Logging Standards]] — PII scrubbing
```

For `cross-cutting/multi-tenancy.md`, append:
```markdown

## Related

- [[modules/infrastructure/tenant-management/overview|Tenant Management]] — tenant provisioning
- [[Userflow/Configuration/tenant-settings|Tenant Settings]] — per-tenant configuration
- [[security/auth-architecture|Auth Architecture]] — JWT tenant isolation
- [[backend/shared-kernel|Shared Kernel]] — ITenantContext
- [[database/performance|Performance]] — RLS performance impact
- [[current-focus/DEV1-infrastructure-setup|DEV1: Infrastructure]] — implementation task
```

For `cross-cutting/database/performance.md`, append:
```markdown

## Related

- [[modules/activity-monitoring/raw-data-processing/overview|Raw Data Processing]] — partitioned time-series tables
- [[modules/activity-monitoring/daily-aggregation/overview|Daily Aggregation]] — aggregation queries
- [[infrastructure/multi-tenancy|Multi Tenancy]] — RLS performance
- [[database/migration-patterns|Migration Patterns]] — EF Core migrations
```

For `cross-cutting/messaging/event-catalog.md`, append:
```markdown

## Related

- [[backend/module-boundaries|Module Boundaries]] — cross-module communication rules
- [[backend/messaging/exchange-topology|Exchange Topology]] — RabbitMQ topology (Phase 2)
- [[backend/messaging/error-handling|Error Handling]] — dead letter handling
- [[backend/shared-kernel|Shared Kernel]] — IDomainEvent interface
```

Apply similar `## Related` sections to ALL cross-cutting docs, linking to the modules and features that use them.

- [x] **Step 3: Commit**

```bash
git add cross-cutting/
git commit -m "docs: move cross-cutting docs to unified cross-cutting/"
```

---

### Task 6: Move Architecture Docs

**Files:**
- Copy: `backend/docs/architecture/module-catalog.md` → `architecture/module-catalog.md`
- Copy: `backend/docs/architecture/module-boundaries.md` → `architecture/module-boundaries.md`
- Copy: `backend/docs/architecture/shared-kernel.md` → `architecture/shared-kernel.md`
- Copy: `backend/docs/architecture/search-architecture.md` → `architecture/search-architecture.md`
- Copy: `backend/docs/architecture/external-integrations.md` → `architecture/external-integrations.md`
- Copy: `backend/docs/architecture/notification-system.md` → `architecture/notification-system.md`
- Copy: `backend/docs/api/README.md` → `architecture/api-conventions.md`
- Copy: `frontend/docs/architecture/README.md` → `architecture/frontend-structure.md`

- [x] **Step 1: Copy architecture docs**

```bash
cp backend/docs/architecture/module-catalog.md architecture/module-catalog.md
cp backend/docs/architecture/module-boundaries.md architecture/module-boundaries.md
cp backend/docs/architecture/shared-kernel.md architecture/shared-kernel.md
cp backend/docs/architecture/search-architecture.md architecture/search-architecture.md
cp backend/docs/architecture/external-integrations.md architecture/external-integrations.md
cp backend/docs/architecture/notification-system.md architecture/notification-system.md
cp backend/docs/api/README.md architecture/api-conventions.md
cp frontend/docs/architecture/README.md architecture/frontend-structure.md
```

- [x] **Step 2: Update module-catalog.md links to point to new module locations**

Replace all module links to use the new `modules/` paths. The catalog should link to each module's `overview.md` using wikilinks like `[[modules/auth/overview|Auth & Security]]`, `[[modules/core-hr/overview|Core HR]]`, etc.

- [x] **Step 3: Add Related sections**

For `architecture/module-boundaries.md`:
```markdown

## Related

- [[backend/module-catalog|Module Catalog]] — full module index
- [[backend/shared-kernel|Shared Kernel]] — cross-cutting code
- [[backend/messaging/event-catalog|Event Catalog]] — cross-module events
- [[backend/messaging/exchange-topology|Exchange Topology]] — message routing
```

For `architecture/shared-kernel.md`:
```markdown

## Related

- [[backend/module-boundaries|Module Boundaries]] — what belongs in shared kernel
- [[infrastructure/multi-tenancy|Multi Tenancy]] — ITenantContext
- [[security/auth-architecture|Auth Architecture]] — ICurrentUser, RequirePermissionAttribute
- [[backend/messaging/error-handling|Error Handling]] — Result<T> pattern
```

- [x] **Step 4: Commit**

```bash
git add architecture/
git commit -m "docs: move architecture docs to unified architecture/"
```

---

### Task 7: Move Design System Docs

**Files:**
- Copy: `frontend/docs/design-system/*` → `design-system/`

- [x] **Step 1: Copy design system docs**

```bash
cp frontend/docs/design-system/* design-system/
```

- [x] **Step 2: Add Related sections to each design system doc**

For `design-system/component-catalog.md`:
```markdown

## Related

- [[frontend/design-system/foundations/color-tokens|Color Tokens]] — color system
- [[frontend/design-system/foundations/typography|Typography]] — type scale
- [[frontend/design-system/patterns/layout-patterns|Layout Patterns]] — page layouts
- [[frontend/coding-standards|Frontend Coding Standards]] — component conventions
```

- [x] **Step 3: Commit**

```bash
git add design-system/
git commit -m "docs: move design system to root level"
```

---

### Task 8: Create current-focus/ Folder from Monolithic File + Task Files

**Files:**
- Read: `backend/AI_CONTEXT/current-focus.md` → Write: `current-focus/README.md` (overview only)
- Move: `tasks/active/WEEK*.md` → `current-focus/WEEK*.md`

- [x] **Step 1: Create current-focus/README.md with overview content only**

Extract ONLY the overview/metadata from `backend/AI_CONTEXT/current-focus.md` — the week tables, deadlines, "not working on" section. Remove the Definition of Done checkboxes (those live in individual task files).

```markdown
# Current Focus: ONEVO

**Last Updated:** 2026-04-06
**Current Phase:** Phase 1 — Backend First, Then Frontend (React)
**Team Size:** 4 developers
**Delivery Deadline:** 2026-05-05 (1 month)
**Development Approach:** Agentic Development Environment (AI-assisted)

---

## Delivery Plan — 4 Weeks, 4 Developers

### Week 1 (Apr 7–11): Foundation & Infrastructure

| Developer | Module(s) | Task File | Key Deliverables |
|:----------|:----------|:----------|:----------------|
| Dev 1 | Infrastructure + Shared Kernel | [[current-focus/DEV1-infrastructure-setup\|DEV1: Infrastructure]] | Tenant provisioning, user CRUD, multi-tenancy, EF Core |
| Dev 2 | Auth & Security | [[current-focus/DEV2-auth-security\|DEV2: Auth Security]] | JWT (RS256), RBAC 90+ perms, MFA, audit logging |
| Dev 3 | Org Structure | [[current-focus/DEV3-org-structure\|DEV3: Org Structure]] | Departments, job hierarchy, teams, legal entities |
| Dev 4 | Shared Platform + Agent Gateway | [[current-focus/DEV4-shared-platform-agent-gateway\|DEV4: Shared Platform Agent Gateway]] | SSO, subscriptions, feature flags, Agent Gateway |

### Week 2 (Apr 14–18): Core HR + Workforce Presence

| Developer | Module(s) | Task File | Key Deliverables |
|:----------|:----------|:----------|:----------------|
| Dev 1 | Core HR (Profile) | [[current-focus/DEV1-core-hr-profile\|DEV1: Core HR Profile]] | Employee CRUD, full profile, salary, bank details |
| Dev 2 | Core HR (Lifecycle) | [[current-focus/DEV2-core-hr-lifecycle\|DEV2: Core HR Lifecycle]] | Onboarding, offboarding, lifecycle events |
| Dev 3 | Workforce Presence (Setup) | [[current-focus/DEV3-workforce-presence-setup\|DEV3: Workforce Presence]] | Shifts, schedules, presence/device sessions, breaks |
| Dev 4 | Workforce Presence (Biometric) | [[current-focus/DEV4-identity-verification\|DEV4: Identity Verification]] | Biometric devices, enrollment, overtime, corrections |

### Week 3 (Apr 21–25): Leave + Performance + Monitoring

| Developer | Module(s) | Task File | Key Deliverables |
|:----------|:----------|:----------|:----------------|
| Dev 1 | Leave | [[current-focus/DEV1-leave\|DEV1: Leave]] | Leave types, policies, entitlements, request/approval |
| Dev 2 | Performance | [[current-focus/DEV2-performance\|DEV2: Performance]] | Reviews, feedback, goals, recognition, succession |
| Dev 3 | Activity Monitoring | [[current-focus/DEV3-activity-monitoring\|DEV3: Activity Monitoring]] | Snapshots, app tracking, meetings, screenshots, aggregation |
| Dev 4 | Identity Verification | [[current-focus/DEV4-identity-verification\|DEV4: Identity Verification]] | Policies, photo capture, biometric matching |

### Week 4 (Apr 28–May 2): Exception Engine + Analytics + Payroll

| Developer | Module(s) | Task File | Key Deliverables |
|:----------|:----------|:----------|:----------------|
| Dev 1 | Productivity Analytics | [[current-focus/DEV1-productivity-analytics\|DEV1: Productivity Analytics]] | Daily/weekly/monthly reports, workforce snapshots |
| Dev 2 | Exception Engine | [[current-focus/DEV2-exception-engine\|DEV2: Exception Engine]] | Rules, triggers, alerts, escalation chains |
| Dev 3 | Payroll | [[current-focus/DEV3-payroll\|DEV3: Payroll]] | Providers, tax, allowances, batch execution |
| Dev 4 | Supporting + Bridges | [[current-focus/DEV4-shared-platform-agent-gateway\|DEV4: Supporting Bridges]] | Documents, notifications, grievance, expense, bridges |

---

## What We Are NOT Working On Right Now

- **AI Chatbot (Nexis)** — deferred to Phase 2
- **Mobile Application (Flutter)** — deferred to Phase 2
- **Frontend (React/Next.js)** — follows backend completion
- **Desktop Agent code** — follows Agent Gateway completion (see [[modules/agent-gateway/overview|Agent Gateway]])
- **WorkManage Pro features** — other team; we only build [[backend/external-integrations|bridge interfaces]]
- **Teams Graph API deep integration** — Phase 2
- **Meilisearch** — PostgreSQL FTS sufficient for Phase 1
- **RabbitMQ** — in-process domain events; RabbitMQ for scale later

## Key Dates & Deadlines

| Milestone | Date | Notes |
|:----------|:-----|:------|
| Week 1 complete | 2026-04-11 | Auth, RBAC, Org Structure, Shared Platform, Agent Gateway |
| Week 2 complete | 2026-04-18 | Employee lifecycle, workforce presence |
| Week 3 complete | 2026-04-25 | Leave, performance, activity monitoring, verification |
| Week 4 complete | 2026-05-02 | Exception engine, analytics, payroll, bridges |
| Final testing | 2026-05-05 | Buffer for integration testing |

## Related

- [[AI_CONTEXT/project-context|Project Context]] — what ONEVO is
- [[AI_CONTEXT/tech-stack|Tech Stack]] — technology decisions
- [[backend/module-catalog|Module Catalog]] — all 22 modules
- [[AI_CONTEXT/rules|Rules]] — AI agent operating rules
- [[AI_CONTEXT/known-issues|Known Issues]] — gotchas
```

- [x] **Step 2: Copy task files from tasks/active/ to current-focus/**

```bash
cp tasks/active/WEEK*.md current-focus/
```

- [x] **Step 3: Add Related sections to each task file**

For each WEEK task file, ensure a `## Related` section exists linking to the modules and features it covers. Example for `current-focus/WEEK1-auth-security.md` — verify and update its existing Related Files section to use correct wikilinks to new paths:

```markdown
## Related

- [[modules/auth/overview|Auth Module Overview]] — module overview
- [[frontend/cross-cutting/authentication|Authentication]] — login flow feature
- [[frontend/cross-cutting/authorization|Authorization]] — RBAC feature
- [[mfa]] — multi-factor auth feature
- [[modules/auth/session-management/overview|Session Management]] — session feature
- [[modules/auth/audit-logging/overview|Audit Logging]] — audit trail feature
- [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]] — GDPR consent feature
- [[security/auth-architecture|Auth Architecture]] — security architecture
- [[security/data-classification|Data Classification]] — PII handling
- [[infrastructure/multi-tenancy|Multi Tenancy]] — JWT tenant isolation
- [[backend/shared-kernel|Shared Kernel]] — RequirePermissionAttribute, ICurrentUser
- [[security/compliance|Compliance]] — GDPR consent requirements
```

- [x] **Step 4: Merge frontend current-focus into README.md**

Add the frontend priority order from `frontend/AI_CONTEXT/current-focus.md` as a "Frontend Phase" section at the bottom of `current-focus/README.md`.

- [x] **Step 5: Commit**

```bash
git add current-focus/
git commit -m "docs: create current-focus folder with individual task files"
```

---

### Task 9: Merge AI_CONTEXT Files to Root

**Files:**
- Merge: `backend/AI_CONTEXT/project-context.md` + `frontend/AI_CONTEXT/project-context.md` + `agent/AI_CONTEXT/project-context.md` → `AI_CONTEXT/project-context.md`
- Merge: `backend/AI_CONTEXT/tech-stack.md` + `frontend/AI_CONTEXT/tech-stack.md` + `agent/AI_CONTEXT/tech-stack.md` → `AI_CONTEXT/tech-stack.md`
- Merge: `backend/AI_CONTEXT/rules.md` + `frontend/AI_CONTEXT/rules.md` + `agent/AI_CONTEXT/rules.md` → `AI_CONTEXT/rules.md`
- Merge: `backend/AI_CONTEXT/known-issues.md` + `frontend/AI_CONTEXT/known-issues.md` + `agent/AI_CONTEXT/known-issues.md` → `AI_CONTEXT/known-issues.md`
- Keep: `backend/AI_CONTEXT/changelog/` → `AI_CONTEXT/changelog/` (already exists or copy)

- [x] **Step 1: Merge project-context.md**

Read all three `project-context.md` files. Create a unified `AI_CONTEXT/project-context.md` that has:
- Main ONEVO platform description (from backend)
- Desktop Agent section (from agent)
- Frontend section (from frontend)
- All linked together with wikilinks

Add `## Related` section:
```markdown
## Related

- [[AI_CONTEXT/tech-stack|Tech Stack]] — technology decisions
- [[current-focus/README|Current Focus]] — what we're building now
- [[backend/module-catalog|Module Catalog]] — all 22 modules
- [[AI_CONTEXT/rules|Rules]] — AI operating rules
```

- [x] **Step 2: Merge tech-stack.md**

Combine backend tech stack (primary), frontend tech stack, and agent tech stack into one unified file with clear sections: Backend, Frontend, Desktop Agent, Infrastructure.

Add `## Related`:
```markdown
## Related

- [[AI_CONTEXT/project-context|Project Context]] — platform overview
- [[frontend/architecture/app-structure|App Structure]] — frontend architecture
- [[modules/agent-gateway/agent-server-protocol|Agent Server Protocol]] — agent communication
```

- [x] **Step 3: Merge rules.md**

Combine backend rules (primary — largest), frontend rules, and agent rules into one unified file with sections:
1. General Operating Principles
2. .NET 9 / C# Code Generation Rules (from backend)
3. Workforce Intelligence Rules (from backend)
4. Frontend / React / Next.js Rules (from frontend)
5. Desktop Agent Rules (from agent)
6. Database Rules
7. Testing Rules
8. Task Completion Rules (NEW — see Task 10)
9. Git Workflow
10. Logging Rules

Update the "Contextual Awareness" reading order to reference new paths:
```markdown
1. [[AI_CONTEXT/project-context|Project Context]] — What ONEVO is
2. [[AI_CONTEXT/tech-stack|Tech Stack]] — .NET 9, PostgreSQL, Redis, Next.js, etc.
3. [[current-focus/README|Current Focus]] — Current sprint/week priorities
4. [[AI_CONTEXT/known-issues|Known Issues]] — Gotchas and deprecated patterns
5. The specific module doc in `modules/` for the module you're working on
```

- [x] **Step 4: Merge known-issues.md**

Combine all three known-issues files. Add wikilinks to relevant modules/features.

- [x] **Step 5: Copy changelog to root AI_CONTEXT if not already there**

```bash
# If AI_CONTEXT/changelog doesn't exist at root, copy from backend
cp -r backend/AI_CONTEXT/changelog AI_CONTEXT/changelog 2>/dev/null || true
```

- [x] **Step 6: Commit**

```bash
git add AI_CONTEXT/
git commit -m "docs: merge all AI_CONTEXT files into unified root"
```

---

### Task 10: Add Task Completion Rules to rules.md

**Files:**
- Modify: `AI_CONTEXT/rules.md`

- [x] **Step 1: Add Section 8 to unified rules.md**

Append after the Git Workflow section:

```markdown
## 8. Task Completion Rules

- **Checkbox tracking:** When a feature or acceptance criterion is implemented, mark its checkbox `- [x]` → `- [x]` in the relevant task file under `current-focus/`
- **Status updates:** Update the task file's **Status** field as work progresses:
  - `Planned` → `In Progress` → `Complete`
- **Changelog logging:** After completing significant work, create a new entry in `AI_CONTEXT/changelog/` with format `YYYY-MM-DD-<description>.md`
- **One source of truth:** Checkboxes live ONLY in individual task files (`current-focus/WEEK*.md`), NOT in `current-focus/README.md`. The README tracks high-level status only.
- **Cross-reference:** When checking a box, verify the related module feature docs are up-to-date with any implementation changes.
```

- [x] **Step 2: Commit**

```bash
git add AI_CONTEXT/rules.md
git commit -m "docs: add task completion rules (section 8)"
```

---

### Task 11: Add [[wikilinks]] to All Module Overview Files

**Files:**
- Modify: All 22 `modules/*/overview.md` files

- [x] **Step 1: Update each module overview.md with comprehensive Related section**

Every module `overview.md` must link to:
- All its feature subfolders: `[[frontend/cross-cutting/authentication|Authentication]]`, `[[frontend/cross-cutting/authorization|Authorization]]`, etc.
- Cross-cutting concerns it uses: `[[infrastructure/multi-tenancy|Multi Tenancy]]`, `[[security/auth-architecture|Auth Architecture]]`, `[[backend/messaging/error-handling|Error Handling]]`, etc.
- Other modules it depends on or is consumed by (from the Dependencies table)
- Its task file: `[[current-focus/DEV2-auth-security|DEV2: Auth Security]]`
- Frontend pages if applicable

Example for `modules/auth/overview.md` — ensure the Related/Dependencies sections use wikilinks:

```markdown
## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/infrastructure/overview\|Infrastructure]] | `IUserService` | User identity |
| **Consumed by** | All modules | `ICurrentUser`, `RequirePermissionAttribute` | Auth context |
| **Consumed by** | [[modules/agent-gateway/overview\|Agent Gateway]] | `ITokenService` | Device JWT issuance |

## Features

- [[frontend/cross-cutting/authentication|Authentication]] — JWT login, RS256 tokens
- [[frontend/cross-cutting/authorization|Authorization]] — RBAC, 90+ permissions
- [[modules/auth/session-management/overview|Session Management]] — user sessions, device tracking
- [[mfa]] — TOTP, Email OTP
- [[modules/auth/audit-logging/overview|Audit Logging]] — JSON diff audit trail
- [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]] — consent records, monitoring opt-in

## Related

- [[security/auth-architecture|Auth Architecture]] — security design doc
- [[security/data-classification|Data Classification]] — PII handling
- [[security/compliance|Compliance]] — GDPR, PDPA requirements
- [[infrastructure/multi-tenancy|Multi Tenancy]] — JWT tenant isolation
- [[backend/shared-kernel|Shared Kernel]] — RequirePermissionAttribute, ICurrentUser
- [[current-focus/DEV2-auth-security|DEV2: Auth Security]] — implementation task
```

- [x] **Step 2: Repeat for all 22 module overviews**

Apply the same pattern: list features as wikilinks, dependencies as wikilinks, Related section with cross-cutting + task links. Each module will have different links — refer to the existing Dependencies tables in each overview.md.

Modules to update:
1. `modules/activity-monitoring/overview.md`
2. `modules/agent-gateway/overview.md`
3. `modules/auth/overview.md`
4. `modules/calendar/overview.md`
5. `modules/configuration/overview.md`
6. `modules/core-hr/overview.md`
7. `modules/documents/overview.md`
8. `modules/exception-engine/overview.md`
9. `modules/expense/overview.md`
10. `modules/grievance/overview.md`
11. `modules/identity-verification/overview.md`
12. `modules/infrastructure/overview.md`
13. `modules/leave/overview.md`
14. `modules/notifications/overview.md`
15. `modules/org-structure/overview.md`
16. `modules/payroll/overview.md`
17. `modules/performance/overview.md`
18. `modules/productivity-analytics/overview.md`
19. `modules/reporting-engine/overview.md`
20. `modules/shared-platform/overview.md`
21. `modules/skills/overview.md`
22. `modules/workforce-presence/overview.md`

- [x] **Step 3: Commit**

```bash
git add modules/
git commit -m "docs: add wikilinks to all 22 module overview files"
```

---

### Task 12: Add [[wikilinks]] to All Feature Files

**Files:**
- Modify: All `modules/*/*/overview.md`, `end-to-end-logic.md`, `testing.md` files (106 feature dirs × 3 files = ~318 files)

- [x] **Step 1: Add Related section to every feature overview.md**

Each feature `overview.md` should link to:
- Parent module: `[[modules/auth/overview|Auth Module]]`
- Sibling features: `[[frontend/cross-cutting/authentication|Authentication]]`, `[[frontend/cross-cutting/authorization|Authorization]]`, etc.
- Cross-cutting concerns: `[[infrastructure/multi-tenancy|Multi Tenancy]]`, `[[backend/messaging/error-handling|Error Handling]]`, `[[security/auth-architecture|Auth Architecture]]`, etc.
- Frontend page if exists: `[[modules/activity-monitoring/application-tracking/frontend|Frontend]]` (in same folder)

Example for `modules/auth/authentication/overview.md`:
```markdown
## Related

- [[modules/auth/overview|Auth Module]] — parent module
- [[frontend/cross-cutting/authorization|Authorization]] — RBAC checks after authentication
- [[modules/auth/session-management/overview|Session Management]] — session created on login
- [[mfa]] — MFA challenge after password verification
- [[security/auth-architecture|Auth Architecture]] — JWT RS256 design
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant_id in JWT claims
- [[backend/messaging/error-handling|Error Handling]] — Result<T> for login failures
- [[code-standards/logging-standards|Logging Standards]] — audit logging on auth events
- [[current-focus/DEV2-auth-security|DEV2: Auth Security]] — implementation task
```

- [x] **Step 2: Add Related section to every end-to-end-logic.md**

Each `end-to-end-logic.md` should link to:
- Its feature overview: `[[frontend/cross-cutting/authentication|Overview]]`
- Other features in the flow: `[[modules/auth/session-management/overview|Session Management]]`, `[[modules/auth/audit-logging/overview|Audit Logging]]`
- Cross-cutting docs relevant to the flow: `[[backend/messaging/event-catalog|Event Catalog]]`, `[[backend/messaging/error-handling|Error Handling]]`

- [x] **Step 3: Add Related section to every testing.md**

Each `testing.md` should link to:
- Its feature overview: `[[frontend/cross-cutting/authentication|Overview]]`
- Testing standards: `[[code-standards/testing-strategy|Testing Standards]]`
- Database testing: `[[database/migration-patterns|Migration Patterns]]` if relevant

- [x] **Step 4: Commit**

```bash
git add modules/
git commit -m "docs: add wikilinks to all feature files (overview, e2e, testing)"
```

---

### Task 13: Clean Up Old Folders

**Files:**
- Delete: `backend/docs/` (all content moved to modules/, cross-cutting/, architecture/)
- Delete: `frontend/docs/` (all content moved to modules/, design-system/, cross-cutting/)
- Delete: `agent/docs/` (all content moved to modules/)
- Delete: `backend/AI_CONTEXT/` (merged into root AI_CONTEXT/)
- Delete: `frontend/AI_CONTEXT/` (merged into root AI_CONTEXT/)
- Delete: `agent/AI_CONTEXT/` (merged into root AI_CONTEXT/)
- Delete: `tasks/` (replaced by current-focus/)
- Keep: `backend/`, `frontend/`, `agent/` folders themselves if they contain non-doc files (like `.cursor/rules/`)

- [x] **Step 1: Verify all content has been moved**

```bash
# Count files in old locations
find backend/docs -name "*.md" | wc -l
find frontend/docs -name "*.md" | wc -l
find agent/docs -name "*.md" | wc -l

# Count files in new locations
find modules/ -name "*.md" | wc -l
find cross-cutting/ -name "*.md" | wc -l
find architecture/ -name "*.md" | wc -l
find design-system/ -name "*.md" | wc -l
find current-focus/ -name "*.md" | wc -l
```

- [x] **Step 2: Remove old doc folders**

```bash
rm -rf backend/docs
rm -rf frontend/docs
rm -rf agent/docs
rm -rf backend/AI_CONTEXT
rm -rf frontend/AI_CONTEXT
rm -rf agent/AI_CONTEXT
rm -rf tasks
```

- [x] **Step 3: Update .cursor/rules if they reference old paths**

Check `.cursor/rules/` files and update any references to `backend/docs/`, `frontend/docs/`, `tasks/active/`, etc. to use the new paths.

- [x] **Step 4: Remove empty parent folders if nothing else remains**

```bash
# Check what's left in backend/, frontend/, agent/
ls backend/ 2>/dev/null
ls frontend/ 2>/dev/null
ls agent/ 2>/dev/null
# If only .cursor/rules remains, keep it. If empty, remove.
```

- [x] **Step 5: Commit**

```bash
git add -A
git commit -m "docs: remove old silo folders (backend/frontend/agent docs merged)"
```

---

### Task 14: Update Changelog

**Files:**
- Create: `AI_CONTEXT/changelog/2026-04-06-unified-brain-restructure.md`

- [x] **Step 1: Write the changelog entry**

```markdown
# 2026-04-06 - Unified Brain Restructure

- **Changed:** Merged 3 separate silos (backend/, frontend/, agent/) into one unified knowledge brain
- **Changed:** All module docs moved from `backend/docs/architecture/modules/` → `modules/`
- **Changed:** Frontend page specs merged into module feature folders as `frontend.md` (11 pages → 11 frontend.md files)
- **Changed:** Agent docs merged into `modules/agent-gateway/` and `modules/identity-verification/`
- **Changed:** Cross-cutting docs (security, database, messaging, deployment, observability, testing, guides) moved to `cross-cutting/`
- **Changed:** Architecture docs moved to `architecture/`
- **Changed:** Design system docs moved to `design-system/`
- **Changed:** `current-focus.md` monolithic file → `current-focus/` folder with README.md + 16 individual task files
- **Changed:** 3 separate `AI_CONTEXT/` dirs (backend, frontend, agent) merged into root `AI_CONTEXT/`
- **Added:** `[[wikilinks]]` to ALL files — every file now links to related modules, features, cross-cutting concerns, and task files
- **Added:** Section 8 "Task Completion Rules" in `rules.md` — checkbox tracking, status updates, changelog logging
- **Removed:** `backend/docs/`, `frontend/docs/`, `agent/docs/`, `backend/AI_CONTEXT/`, `frontend/AI_CONTEXT/`, `agent/AI_CONTEXT/`, `tasks/`
- **Why:** Files were completely disconnected (0 wikilinks across 446 files). Obsidian graph showed isolated nodes. Separate backend/frontend/agent silos made cross-referencing impossible for both humans and AI agents.
```

- [x] **Step 2: Remove the earlier partial changelog entry**

Delete `AI_CONTEXT/changelog/2026-04-06-feature-wise-module-restructure.md` since this changelog supersedes it.

- [x] **Step 3: Commit**

```bash
git add AI_CONTEXT/changelog/
git commit -m "docs: add changelog for unified brain restructure"
```

---

### Task 15: Final Verification

- [x] **Step 1: Verify wikilink count**

```bash
grep -rl '\[\[' . --include="*.md" | grep -v '.git' | wc -l
# Expected: 350+ files should now contain wikilinks
```

- [x] **Step 2: Verify no orphaned files**

```bash
# Check for markdown files outside the new structure
find . -name "*.md" -not -path './.git/*' -not -path './.obsidian/*' -not -path './modules/*' -not -path './cross-cutting/*' -not -path './architecture/*' -not -path './design-system/*' -not -path './current-focus/*' -not -path './AI_CONTEXT/*' -not -path './decisions/*' -not -path './meetings/*' -not -path './docs/superpowers/*' | sort
# Should only show: README.md, and files in decisions/, meetings/, scripts/
```

- [x] **Step 3: Open Obsidian graph view and verify interconnection**

The graph should now show a dense, connected web instead of isolated floating dots. Core hubs should be:
- `auth-architecture` (connected to auth features + many modules)
- `multi-tenancy` (connected to nearly everything)
- `module-catalog` (connected to all 22 modules)
- `current-focus/README` (connected to all task files)
- `shared-kernel` (connected to many modules)

- [x] **Step 4: Final commit if any fixes needed**

```bash
git add -A
git commit -m "docs: final cleanup after brain restructure"
```
