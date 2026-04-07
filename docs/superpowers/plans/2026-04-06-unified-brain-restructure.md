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

- [[employee-profiles|Backend: Employee Profiles]] — API and data model
- [[employee-lifecycle|Employee Lifecycle]] — onboarding/offboarding flows
- [[auth-architecture|Auth Architecture]] — permission checks
- [[authorization|RBAC]] — `employees:read`, `employees:write` permissions
- [[multi-tenancy]] — tenant-scoped queries
- [[WEEK2-core-hr-profile]] — implementation task
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

- [[agent-gateway|Agent Gateway Module]] — parent module overview
- [[data-ingestion|Data Ingestion]] — how agent sends data to server
- [[heartbeat-monitoring|Heartbeat]] — agent health checks
- [[tamper-resistance]] — anti-tamper protections
- [[auth-architecture]] — device JWT authentication
- [[WEEK1-shared-platform]] — implementation task
```

For `modules/agent-gateway/data-collection.md`, append:
```markdown

## Related

- [[agent-server-protocol]] — communication protocol
- [[raw-data-processing]] — how server processes collected data
- [[application-tracking]] — app usage tracking
- [[device-tracking]] — device activity tracking
- [[data-classification]] — PII/RESTRICTED classification for collected data
- [[retention-policies]] — data retention rules
```

For `modules/agent-gateway/tamper-resistance.md`, append:
```markdown

## Related

- [[agent-server-protocol]] — secure communication
- [[auth-architecture]] — device JWT, HMAC
- [[compliance]] — security requirements
```

For `modules/identity-verification/photo-capture.md`, append:
```markdown

## Related

- [[identity-verification|Identity Verification Module]] — parent module
- [[photo-verification]] — server-side verification
- [[biometric-enrollment]] — biometric data enrollment
- [[verification-policies]] — when photos are required
- [[data-classification]] — RESTRICTED classification for photos
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

- [[authentication]] — login flow feature
- [[authorization]] — RBAC feature
- [[mfa]] — multi-factor auth feature
- [[session-management]] — session tracking
- [[agent-server-protocol]] — device JWT
- [[multi-tenancy]] — tenant isolation
- [[compliance]] — GDPR, PDPA, OWASP
- [[data-classification]] — PII inventory
- [[WEEK1-auth-security]] — implementation task
```

For `cross-cutting/security/data-classification.md`, append:
```markdown

## Related

- [[auth-architecture]] — encryption, access control
- [[retention-policies]] — data retention per classification
- [[screenshots]] — RESTRICTED data
- [[photo-capture]] — RESTRICTED data
- [[compliance]] — GDPR rights
- [[logging-standards]] — PII scrubbing
```

For `cross-cutting/multi-tenancy.md`, append:
```markdown

## Related

- [[tenant-management]] — tenant provisioning
- [[tenant-settings]] — per-tenant configuration
- [[auth-architecture]] — JWT tenant isolation
- [[shared-kernel]] — ITenantContext
- [[performance]] — RLS performance impact
- [[WEEK1-infrastructure-setup]] — implementation task
```

For `cross-cutting/database/performance.md`, append:
```markdown

## Related

- [[raw-data-processing]] — partitioned time-series tables
- [[daily-aggregation]] — aggregation queries
- [[multi-tenancy]] — RLS performance
- [[migration-patterns]] — EF Core migrations
```

For `cross-cutting/messaging/event-catalog.md`, append:
```markdown

## Related

- [[module-boundaries]] — cross-module communication rules
- [[exchange-topology]] — RabbitMQ topology (Phase 2)
- [[error-handling]] — dead letter handling
- [[shared-kernel]] — IDomainEvent interface
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

Replace all module links to use the new `modules/` paths. The catalog should link to each module's `overview.md` using wikilinks like `[[auth|Auth & Security]]`, `[[core-hr|Core HR]]`, etc.

- [x] **Step 3: Add Related sections**

For `architecture/module-boundaries.md`:
```markdown

## Related

- [[module-catalog]] — full module index
- [[shared-kernel]] — cross-cutting code
- [[event-catalog]] — cross-module events
- [[exchange-topology]] — message routing
```

For `architecture/shared-kernel.md`:
```markdown

## Related

- [[module-boundaries]] — what belongs in shared kernel
- [[multi-tenancy]] — ITenantContext
- [[auth-architecture]] — ICurrentUser, RequirePermissionAttribute
- [[error-handling]] — Result<T> pattern
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

- [[color-tokens]] — color system
- [[typography]] — type scale
- [[layout-patterns]] — page layouts
- [[frontend-coding-standards]] — component conventions
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
| Dev 1 | Infrastructure + Shared Kernel | [[WEEK1-infrastructure-setup]] | Tenant provisioning, user CRUD, multi-tenancy, EF Core |
| Dev 2 | Auth & Security | [[WEEK1-auth-security]] | JWT (RS256), RBAC 90+ perms, MFA, audit logging |
| Dev 3 | Org Structure | [[WEEK1-org-structure]] | Departments, job hierarchy, teams, legal entities |
| Dev 4 | Shared Platform + Agent Gateway | [[WEEK1-shared-platform]] | SSO, subscriptions, feature flags, Agent Gateway |

### Week 2 (Apr 14–18): Core HR + Workforce Presence

| Developer | Module(s) | Task File | Key Deliverables |
|:----------|:----------|:----------|:----------------|
| Dev 1 | Core HR (Profile) | [[WEEK2-core-hr-profile]] | Employee CRUD, full profile, salary, bank details |
| Dev 2 | Core HR (Lifecycle) | [[WEEK2-core-hr-lifecycle]] | Onboarding, offboarding, lifecycle events |
| Dev 3 | Workforce Presence (Setup) | [[WEEK2-workforce-presence-setup]] | Shifts, schedules, presence/device sessions, breaks |
| Dev 4 | Workforce Presence (Biometric) | [[WEEK2-workforce-presence-biometric]] | Biometric devices, enrollment, overtime, corrections |

### Week 3 (Apr 21–25): Leave + Performance + Monitoring

| Developer | Module(s) | Task File | Key Deliverables |
|:----------|:----------|:----------|:----------------|
| Dev 1 | Leave | [[WEEK3-leave]] | Leave types, policies, entitlements, request/approval |
| Dev 2 | Performance | [[WEEK3-performance]] | Reviews, feedback, goals, recognition, succession |
| Dev 3 | Activity Monitoring | [[WEEK3-activity-monitoring]] | Snapshots, app tracking, meetings, screenshots, aggregation |
| Dev 4 | Identity Verification | [[WEEK3-identity-verification]] | Policies, photo capture, biometric matching |

### Week 4 (Apr 28–May 2): Exception Engine + Analytics + Payroll

| Developer | Module(s) | Task File | Key Deliverables |
|:----------|:----------|:----------|:----------------|
| Dev 1 | Productivity Analytics | [[WEEK4-productivity-analytics]] | Daily/weekly/monthly reports, workforce snapshots |
| Dev 2 | Exception Engine | [[WEEK4-exception-engine]] | Rules, triggers, alerts, escalation chains |
| Dev 3 | Payroll | [[WEEK4-payroll]] | Providers, tax, allowances, batch execution |
| Dev 4 | Supporting + Bridges | [[WEEK4-supporting-bridges]] | Documents, notifications, grievance, expense, bridges |

---

## What We Are NOT Working On Right Now

- **AI Chatbot (Nexis)** — deferred to Phase 2
- **Mobile Application (Flutter)** — deferred to Phase 2
- **Frontend (React/Next.js)** — follows backend completion
- **Desktop Agent code** — follows Agent Gateway completion (see [[agent-gateway]])
- **WorkManage Pro features** — other team; we only build [[external-integrations|bridge interfaces]]
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

- [[project-context]] — what ONEVO is
- [[tech-stack]] — technology decisions
- [[module-catalog]] — all 22 modules
- [[rules]] — AI agent operating rules
- [[known-issues]] — gotchas
```

- [x] **Step 2: Copy task files from tasks/active/ to current-focus/**

```bash
cp tasks/active/WEEK*.md current-focus/
```

- [x] **Step 3: Add Related sections to each task file**

For each WEEK task file, ensure a `## Related` section exists linking to the modules and features it covers. Example for `current-focus/WEEK1-auth-security.md` — verify and update its existing Related Files section to use correct wikilinks to new paths:

```markdown
## Related

- [[auth|Auth Module Overview]] — module overview
- [[authentication]] — login flow feature
- [[authorization]] — RBAC feature
- [[mfa]] — multi-factor auth feature
- [[session-management]] — session feature
- [[audit-logging]] — audit trail feature
- [[gdpr-consent]] — GDPR consent feature
- [[auth-architecture]] — security architecture
- [[data-classification]] — PII handling
- [[multi-tenancy]] — JWT tenant isolation
- [[shared-kernel]] — RequirePermissionAttribute, ICurrentUser
- [[compliance]] — GDPR consent requirements
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

- [[tech-stack]] — technology decisions
- [[current-focus/README|Current Focus]] — what we're building now
- [[module-catalog]] — all 22 modules
- [[rules]] — AI operating rules
```

- [x] **Step 2: Merge tech-stack.md**

Combine backend tech stack (primary), frontend tech stack, and agent tech stack into one unified file with clear sections: Backend, Frontend, Desktop Agent, Infrastructure.

Add `## Related`:
```markdown
## Related

- [[project-context]] — platform overview
- [[frontend-structure]] — frontend architecture
- [[agent-server-protocol]] — agent communication
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
1. [[project-context]] — What ONEVO is
2. [[tech-stack]] — .NET 9, PostgreSQL, Redis, Next.js, etc.
3. [[current-focus/README|Current Focus]] — Current sprint/week priorities
4. [[known-issues]] — Gotchas and deprecated patterns
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
- All its feature subfolders: `[[authentication]]`, `[[authorization]]`, etc.
- Cross-cutting concerns it uses: `[[multi-tenancy]]`, `[[auth-architecture]]`, `[[error-handling]]`, etc.
- Other modules it depends on or is consumed by (from the Dependencies table)
- Its task file: `[[WEEK1-auth-security]]`
- Frontend pages if applicable

Example for `modules/auth/overview.md` — ensure the Related/Dependencies sections use wikilinks:

```markdown
## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[infrastructure]] | `IUserService` | User identity |
| **Consumed by** | All modules | `ICurrentUser`, `RequirePermissionAttribute` | Auth context |
| **Consumed by** | [[agent-gateway]] | `ITokenService` | Device JWT issuance |

## Features

- [[authentication]] — JWT login, RS256 tokens
- [[authorization]] — RBAC, 90+ permissions
- [[session-management]] — user sessions, device tracking
- [[mfa]] — TOTP, Email OTP
- [[audit-logging]] — JSON diff audit trail
- [[gdpr-consent]] — consent records, monitoring opt-in

## Related

- [[auth-architecture]] — security design doc
- [[data-classification]] — PII handling
- [[compliance]] — GDPR, PDPA requirements
- [[multi-tenancy]] — JWT tenant isolation
- [[shared-kernel]] — RequirePermissionAttribute, ICurrentUser
- [[WEEK1-auth-security]] — implementation task
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
- Parent module: `[[auth|Auth Module]]`
- Sibling features: `[[authentication]]`, `[[authorization]]`, etc.
- Cross-cutting concerns: `[[multi-tenancy]]`, `[[error-handling]]`, `[[auth-architecture]]`, etc.
- Frontend page if exists: `[[frontend]]` (in same folder)

Example for `modules/auth/authentication/overview.md`:
```markdown
## Related

- [[auth|Auth Module]] — parent module
- [[authorization]] — RBAC checks after authentication
- [[session-management]] — session created on login
- [[mfa]] — MFA challenge after password verification
- [[auth-architecture]] — JWT RS256 design
- [[multi-tenancy]] — tenant_id in JWT claims
- [[error-handling]] — Result<T> for login failures
- [[logging-standards]] — audit logging on auth events
- [[WEEK1-auth-security]] — implementation task
```

- [x] **Step 2: Add Related section to every end-to-end-logic.md**

Each `end-to-end-logic.md` should link to:
- Its feature overview: `[[authentication|Overview]]`
- Other features in the flow: `[[session-management]]`, `[[audit-logging]]`
- Cross-cutting docs relevant to the flow: `[[event-catalog]]`, `[[error-handling]]`

- [x] **Step 3: Add Related section to every testing.md**

Each `testing.md` should link to:
- Its feature overview: `[[authentication|Overview]]`
- Testing standards: `[[testing/README|Testing Standards]]`
- Database testing: `[[migration-patterns]]` if relevant

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
