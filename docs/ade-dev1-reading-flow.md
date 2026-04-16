# ADE Reading Flow: Dev 1 — Start to End

**What this document is:** The exact sequence of files an ADE agent reads, in order, when
given the command: "You are Dev 1. Build all your tasks."

This covers the full journey — orchestrator startup, base context loading, each of Dev 1's
4 tasks, and the WMS bridges Dev 1 owns.

---

## Phase 0: Orchestrator Startup

The orchestrator runs first and determines what to do. It reads:

```
1. ade/README.md                        ← How the orchestrator works, what repos to use
2. current-focus/README.md             ← Task assignment table: Dev 1 has 4 tasks
```

From `current-focus/README.md`, the orchestrator extracts:

| Task # | File | Module |
|:-------|:-----|:-------|
| 1 | `current-focus/DEV1-infrastructure-setup.md` | Infrastructure + SharedKernel |
| 2 | `current-focus/DEV1-core-hr-profile.md` | CoreHR |
| 3 | `current-focus/DEV1-leave.md` | Leave |
| 4 | `current-focus/DEV1-productivity-analytics.md` | ProductivityAnalytics |

The orchestrator reads each task file's `## Related Tasks` section to check cross-dev
dependencies. If a dependency is missing in the code repo, the task is skipped. Tasks run
**sequentially** (1 → 2 → 3 → 4), never in parallel.

---

## Phase 1: Base Context (Injected Into Every Worker Agent)

Before any task starts, every worker agent receives these 4 files:

```
AI_CONTEXT/rules.md
AI_CONTEXT/project-context.md
AI_CONTEXT/tech-stack.md
AI_CONTEXT/known-issues.md
```

**What the agent learns from each:**

### `AI_CONTEXT/rules.md`
The agent's operating constitution. Key rules absorbed:
- Monolithic architecture, strict namespace boundaries (`ONEVO.Modules.{Name}`)
- Domain events for side effects, direct calls for sync queries
- `ITenantContext` injection in every repository — never skip
- `Result<T>` pattern instead of exceptions
- async + CancellationToken everywhere
- Naming: snake_case columns, PascalCase C#, kebab-case API routes
- Phase 2 guard: never build routes/pages/tables for deferred modules
- Checkbox tracking: mark `- [ ]` → `- [x]` as each criterion is completed
- Logging: structured Serilog, never log PII or activity content

### `AI_CONTEXT/project-context.md`
System architecture map. Key concepts absorbed:
- Two-pillar model: HR Management (Pillar 1) + Workforce Intelligence (Pillar 2)
- Employee is the central hub entity — almost all modules link through it
- Modular monolith: one .NET solution, 23 modules, strict boundaries
- Multi-tenant: every entity has `tenant_id`
- Activity data: buffer → aggregate pattern (raw buffer 48h, summaries 2 years)

### `AI_CONTEXT/tech-stack.md`
Technology choices. Key items absorbed:
- .NET 9, C# 13, Minimal APIs
- PostgreSQL 16 + EF Core 9 (snake_case convention)
- Redis for caching/rate limiting
- Hangfire for background jobs
- MediatR for command/query/event dispatch
- SignalR for real-time
- Next.js 14, TypeScript, shadcn/ui, TanStack Query
- JWT (RS256), Argon2id passwords
- Azure Blob Storage, Resend email

### `AI_CONTEXT/known-issues.md`
Gotchas. Key ones absorbed for Dev 1's work:
- BaseRepository handles tenant filtering — never bypass
- `TenantRlsInterceptor` uses Guid string interpolation — safe for Guids only
- Employee vs User distinction — query through `employees`, not `users`
- `organisation_id` is old/resolved — everything uses `tenant_id` now
- `account_number_encrypted` uses `IEncryptionService` (AES-256) — bytea type
- `leave_policies.superseded_by_id` — always get the one where `IS NULL`
- Activity data volume: 240 rows/employee/day — use partitioned tables
- Reporting data: use `activity_daily_summary`, never raw `activity_raw_buffer`
- Cursor-based pagination only — no offset pagination

---

## Phase 2: ADE Entry Point Scan (First File Read)

The agent reads:

```
ADE-START-HERE.md
```

**What the agent learns:**
- What ONEVO is (employee monitoring SaaS)
- Phase 1: 15 modules to build (+ Discrepancy Engine — see ARCH-02 in scan report)
- Phase 2: 6 modules + Skills LMS deferred — DO NOT build
- Build order / critical path (Dev 1 = Infrastructure week 1, then Core HR week 2, etc.)
- Hybrid Permission Model is NOT simple RBAC
- Monitoring Lifecycle = data only flows when employee is clocked in
- Three-tier App Allowlist
- Bidirectional SignalR architecture
- Domain events via MediatR
- Where to find module specs (`modules/*/overview.md`)

---

## Phase 3: Task 1 — Infrastructure & Foundation

### Dependency check
No dependencies (first task). Agent proceeds immediately.

### Files read for Task 1

```
current-focus/DEV1-infrastructure-setup.md    ← Task spec: acceptance criteria, pages to build
```

Task-specific context injected by orchestrator:

```
modules/infrastructure/overview.md            ← Infrastructure module: tenants, users, files, countries
backend/shared-kernel.md                      ← BaseEntity, BaseRepository, ITenantContext, Result<T>
infrastructure/multi-tenancy.md               ← Tenant isolation: RLS, ITenantContext, BaseRepository
database/migration-patterns.md                ← EF Core migrations, never raw DDL
infrastructure/environment-parity.md          ← Docker Compose, local dev setup
code-standards/backend-standards.md           ← Naming conventions, patterns
backend/module-catalog.md                     ← 23-module solution structure (namespace map)
Userflow/Platform-Setup/tenant-provisioning.md ← Tenant signup + industry profile userflow
```

Also reads any frontend references needed for Step 2:
```
frontend/architecture/app-structure.md         ← Next.js directory layout
frontend/design-system/README.md               ← Design system overview
frontend/design-system/components/component-catalog.md ← shadcn/ui components
frontend/design-system/foundations/color-tokens.md     ← Brand + semantic colors
frontend/design-system/patterns/layout-patterns.md     ← Sidebar, topbar, content areas
frontend/design-system/foundations/typography.md       ← Font scale
frontend/data-layer/api-integration.md                 ← API client pattern
frontend/data-layer/state-management.md                ← TanStack Query + Zustand
```

### What the agent builds

**Step 1 — Backend:**
1. Solution structure: 23 project files under `ONEVO.sln`
2. `ONEVO.SharedKernel`: `BaseEntity`, `BaseRepository<T>`, `ITenantContext`, `Result<T>`, `IEncryptionService`
3. EF Core config: `UseSnakeCaseNamingConvention()`, RLS policies, `TenantRlsInterceptor`
4. Redis connection via `IConnectionMultiplexer`
5. Tenant CRUD + provisioning: sign-up → seed → activate, with `industry_profile` → seeds `monitoring_feature_toggles`
6. User CRUD with Argon2id password hashing
7. File upload service (`IFileService`) — local disk for dev, configurable
8. Country reference data seeded (`LK`, `GB`, etc.)
9. Docker Compose: PostgreSQL 16 + Redis
10. Swagger/OpenAPI
11. Health check endpoints at `/health`

**Step 2 — Frontend:**
1. Root `layout.tsx`: QueryClientProvider, AuthProvider, PermissionProvider, SignalRProvider, ThemeProvider, ToastProvider
2. `(auth)/layout.tsx`: centered card, brand logo
3. `(dashboard)/layout.tsx`: sidebar + topbar shell (DashboardLayout)
4. Sidebar: collapsible, permission-gated nav sections
5. Topbar: CommandPalette (Cmd+K), NotificationBell, user menu
6. Breadcrumb component
7. Overview dashboard: placeholder KPI cards
8. `error.tsx`, `not-found.tsx`
9. Shared components: `PermissionGate`, `DataTable`, `StatusBadge`

**After Step 2:** Marks all checkboxes `- [x]` in `DEV1-infrastructure-setup.md`. Commits to backend repo and frontend repo.

---

## Phase 4: Task 2 — Core HR Employee Profile

### Dependency check
```
DEV1 Infrastructure Setup  ← checks: Does ONEVO.SharedKernel exist in backend repo?
DEV3 Org Structure         ← checks: Do departments/job_titles tables exist in backend repo?
```
If DEV3 Org Structure is not done, the orchestrator skips Task 2 and reports it as blocked.
Assuming both dependencies are met, agent proceeds.

### Files read for Task 2

```
current-focus/DEV1-core-hr-profile.md         ← Task spec
```

Task-specific context:

```
modules/core-hr/overview.md                    ← CoreHR module spec: tables, events, endpoints
backend/shared-kernel.md                       ← Already in base, but re-reads for IEncryptionService
security/data-classification.md               ← PII fields, encryption requirements, RESTRICTED data
infrastructure/multi-tenancy.md                ← Tenant-scoped employee queries
```

Userflows:
```
Userflow/Employee-Management/profile-management.md
Userflow/Employee-Management/dependent-management.md
Userflow/Employee-Management/qualification-tracking.md
Userflow/Employee-Management/compensation-setup.md
```

Frontend references:
```
frontend/architecture/app-structure.md
frontend/design-system/components/component-catalog.md   ← DataTable, PageHeader, Avatar
frontend/design-system/patterns/layout-patterns.md
frontend/data-layer/api-integration.md
frontend/coding-standards.md
```

### What the agent builds

**Step 1 — Backend:**
1. `employees` table + CRUD endpoints (list/get/create/update, cursor-based pagination)
2. Auto-generated employee number (tenant-scoped sequence)
3. 1:1 link to `users` via `user_id`
4. Self-referencing `manager_id` — CTE queries for org tree
5. `employee_addresses` CRUD (permanent, current, emergency)
6. `employee_dependents` CRUD
7. `employee_qualifications` CRUD + document upload via `IFileService`
8. `employee_work_history` CRUD
9. `employee_salary_history` — append-only
10. `employee_bank_details` — `account_number_encrypted` via `IEncryptionService` (AES-256 → `bytea`)
11. `employee_emergency_contacts` CRUD
12. `employee_custom_fields` CRUD
13. Avatar upload via `IFileService`
14. `GET /api/v1/employees/me` (own profile, `employees:read-own`)
15. `GET /api/v1/employees/{id}/team` (direct reports, `employees:read-team`)
16. FluentValidation for all commands
17. Unit tests ≥ 80% coverage

**Step 2 — Frontend:**
1. Employee list page: `app/(dashboard)/hr/employees/page.tsx` — DataTable with search, department filter, status filter
2. Employee detail page: tabs (Personal, Addresses, Dependents, Qualifications, Work History, Salary, Bank, Emergency Contacts)
3. Create wizard: 4-step client-side stepper (personal → employment → compensation → review)
4. Edit via intercepting route: `@panel/(.)edit/page.tsx` (slide-over panel)
5. Section-specific edit modals with `PermissionGate` per section
6. Employee self-service: own profile (read-only where not permitted)
7. `loading.tsx` skeleton + `not-found.tsx`
8. Colocated: `EmployeeDataTable.tsx`, `EmployeeTabs.tsx`, `EmployeeWizardSteps.tsx`, `AvatarUpload.tsx`

**After Step 2:** Marks all checkboxes. Commits.

---

## Phase 5: Task 3 — Leave Module

### Dependency check
```
DEV1 Infrastructure Setup    ← SharedKernel required
DEV1 Core HR Profile         ← employees table required (leave references employee)
DEV4 Shared Platform         ← workflow engine required for approval routing
DEV3 Calendar                ← ICalendarConflictService required
```
Key check: Does `ICalendarConflictService` exist in the backend repo?
If not → orchestrator skips Leave, reports: "Leave blocked — ICalendarConflictService missing. Re-run after DEV3 delivers Calendar."

If all dependencies met, agent proceeds.

### Files read for Task 3

```
current-focus/DEV1-leave.md                   ← Task spec
```

Task-specific context:

```
modules/leave/overview.md                     ← Leave module spec: tables, policies, events
modules/core-hr/overview.md                   ← Employee country + job level for policy matching
modules/workforce-presence/overview.md        ← Presence sessions updated on LeaveApproved
modules/calendar/overview.md                  ← ICalendarConflictService interface
infrastructure/multi-tenancy.md               ← Tenant-scoped leave types and policies
```

Userflows:
```
Userflow/Leave/leave-request-submission.md
Userflow/Leave/leave-approval.md
Userflow/Leave/leave-cancellation.md
Userflow/Leave/leave-balance-view.md
Userflow/Leave/leave-type-configuration.md
Userflow/Leave/leave-policy-setup.md
Userflow/Leave/leave-entitlement-assignment.md
```

Frontend references:
```
frontend/design-system/components/component-catalog.md  ← DataTable, Calendar, Badge, StatCard
frontend/design-system/foundations/color-tokens.md      ← Status colors for leave types
frontend/data-layer/api-integration.md
```

### What the agent builds

**Step 1 — Backend:**
1. `leave_types` CRUD (tenant-scoped)
2. `leave_policies` with versioning chain (`superseded_by_id`)
3. Policy matching: leave type + country + job level; active = `WHERE superseded_by_id IS NULL`
4. `leave_entitlements`: accrual methods + proration + carry-forward
5. `leave_requests`: submit/approve/reject/cancel workflow
6. Request validation: balance check, overlap check, max consecutive days
7. Calendar conflict: calls `ICalendarConflictService`, stores `conflict_snapshot_json`
8. Manager approval view: conflict snapshot (at submission) + live re-check
9. `LeaveRequested` notification includes conflict count
10. `leave_balances_audit` append-only log
11. Workflow integration for manager → HR routing (via SharedPlatform workflow engine)
12. Domain events: `LeaveRequested`, `LeaveApproved`, `LeaveRejected`, `LeaveCancelled`
13. `LeaveApproved` handler → updates `presence_sessions.status = 'on_leave'`
14. Unit tests ≥ 80% coverage

**Step 2 — Frontend:**
1. Leave list page: DataTable (employee, type, dates, status, actions) — permission-driven view
2. Leave request detail modal: conflict snapshot + approve/reject
3. Team leave calendar: monthly, color-coded by leave type
4. Leave balances page: cards per type (used / remaining / pending)
5. Leave policy admin: CRUD + version history
6. Submit request form: type, dates, reason, half-day toggle
7. Approval flow UI: approve/reject with comments
8. Conflict warning banner on submission
9. Colocated: `LeaveRequestForm.tsx`, `LeaveCalendar.tsx`, `LeaveBalanceCard.tsx`, `LeavePolicyEditor.tsx`
10. `PermissionGate`: `leave:create`, `leave:approve`, `leave:read-team`, `leave:read-own`

**After Step 2:** Marks all checkboxes. Commits.

---

## Phase 6: Task 4 — Productivity Analytics

### Dependency check
```
DEV3 Activity Monitoring     ← IActivityMonitoringService + activity_daily_summary required
DEV3 Workforce Presence      ← presence_sessions required
```
If either dependency is missing → orchestrator skips, reports blocked tasks.

### Files read for Task 4

```
current-focus/DEV1-productivity-analytics.md  ← Task spec
```

Task-specific context:

```
modules/productivity-analytics/overview.md    ← ProductivityAnalytics module spec
modules/reporting-engine/overview.md          ← Reporting Engine tables (report_definitions etc.)
modules/activity-monitoring/overview.md       ← activity_daily_summary is primary data source
modules/workforce-presence/overview.md        ← presence_sessions is primary data source
infrastructure/multi-tenancy.md               ← Tenant-scoped reports
```

Userflows:
```
Userflow/Analytics-Reporting/productivity-dashboard.md
Userflow/Analytics-Reporting/report-creation.md
Userflow/Analytics-Reporting/scheduled-report-setup.md
Userflow/Analytics-Reporting/data-export.md
Userflow/Analytics-Reporting/workforce-snapshot.md
```

Frontend references:
```
frontend/design-system/components/component-catalog.md   ← DataTable, StatCard, DateRangePicker
frontend/design-system/patterns/data-visualization.md   ← Charts, sparklines, heatmaps
frontend/data-layer/api-integration.md
```

### What the agent builds

**Step 1 — Backend:**

Productivity Analytics:
1. `daily_employee_report`: aggregated from `activity_daily_summary` + `presence_sessions`
2. `weekly_employee_report`: weekly trend vs previous week
3. `monthly_employee_report`: monthly patterns + department rank
4. `workforce_snapshot`: tenant-wide daily metrics
5. `GenerateDailyReportsJob` (Hangfire, daily 11:30 PM)
6. `GenerateWeeklyReportsJob` (Monday 1:00 AM)
7. `GenerateMonthlyReportsJob` (1st of month 2:00 AM)
8. Department rank by `active%` (`comparative_rank_in_department`)
9. `IProductivityAnalyticsService` public interface
10. Domain events: `DailyReportReady`, `WeeklyReportReady`, `MonthlyReportReady`

Reporting Engine (built within ProductivityAnalytics namespace):
11. `report_definitions`: configurable with cron schedule
12. `report_executions`: execution log
13. `report_templates`: column definitions + default filters
14. Report types: `headcount`, `turnover`, `leave_utilization`, `productivity_daily`, `productivity_weekly`, `workforce_summary`, `exception_summary`
15. On-demand + scheduled execution via Hangfire
16. CSV export
17. Excel (xlsx) export
18. Generated reports via `IFileService`
19. Unit tests ≥ 80%

**Step 2 — Frontend:**
1. Productivity dashboard: `app/(dashboard)/workforce/productivity/page.tsx`
   - Toggle: daily / weekly / monthly
   - DataTable: active %, idle %, app usage breakdown, `TrendSparkline`, department rank
   - Department/team/date filters
2. Workforce snapshot widget on overview dashboard
3. Report builder: `/reports/builder/page.tsx`
   - Select template → configure filters → schedule cron
   - Execution history
4. CSV/Excel export buttons on all report views
5. Colocated: `ProductivityChart.tsx`, `TrendSparkline.tsx`, `AppUsageBreakdown.tsx`, `ReportBuilder.tsx`, `ReportScheduleForm.tsx`

**After Step 2:** Marks all checkboxes. Commits.

---

## Phase 7: WMS Bridges (Dev 1 Owned)

After all 4 tasks are complete, Dev 1 also owns these Phase 1 bridges:

### Bridge 2: Availability (after Task 3 — Leave is done)

```
current-focus/WMS-bridge-integration.md       ← Bridge spec
docs/wms-integration-analysis.md              ← Context for why bridges exist
backend/bridge-api-contracts.md               ← Request/response schemas
backend/external-integrations.md              ← Bridge endpoint registry
```

Builds: `GET /api/v1/bridges/availability/{employeeId}` — leave periods + today's presence status + shift info

### Bridge 3: Work Activity (before Discrepancy Engine goes live)

Builds: `POST /api/v1/bridges/work-activity/time-logs` — accepts WMS time logs, aggregates into `wms_daily_time_logs`

---

## Phase 8: Orchestrator Final Report

After all tasks complete (or are blocked), the orchestrator outputs:

```
Session complete.
  ✓ Completed: Task 1 (Infrastructure), Task 2 (Employee Profile), Task 3 (Leave), Task 4 (Productivity Analytics)
  ✓ WMS Bridges: Bridge 2 (Availability), Bridge 3 (Work Activity)
  ✗ Blocked: [any skipped tasks with reason]

  All Dev 1 Phase 1 tasks complete.
```

---

## Full File Read Order (Canonical Sequence)

This is the definitive ordered list of every file the ADE agent reads for Dev 1, top to bottom:

```
## ORCHESTRATOR PHASE
ade/README.md
current-focus/README.md

## BASE CONTEXT (every task)
AI_CONTEXT/rules.md
AI_CONTEXT/project-context.md
AI_CONTEXT/tech-stack.md
AI_CONTEXT/known-issues.md

## ENTRY POINT
ADE-START-HERE.md

## TASK 1 — Infrastructure
current-focus/DEV1-infrastructure-setup.md
modules/infrastructure/overview.md
backend/shared-kernel.md
infrastructure/multi-tenancy.md
database/migration-patterns.md
infrastructure/environment-parity.md
code-standards/backend-standards.md
backend/module-catalog.md
Userflow/Platform-Setup/tenant-provisioning.md
frontend/architecture/app-structure.md
frontend/design-system/README.md
frontend/design-system/components/component-catalog.md
frontend/design-system/foundations/color-tokens.md
frontend/design-system/patterns/layout-patterns.md
frontend/design-system/foundations/typography.md
frontend/data-layer/api-integration.md
frontend/data-layer/state-management.md

## TASK 2 — Core HR Employee Profile
current-focus/DEV1-core-hr-profile.md
modules/core-hr/overview.md
security/data-classification.md
Userflow/Employee-Management/profile-management.md
Userflow/Employee-Management/dependent-management.md
Userflow/Employee-Management/qualification-tracking.md
Userflow/Employee-Management/compensation-setup.md
frontend/coding-standards.md

## TASK 3 — Leave
current-focus/DEV1-leave.md
modules/leave/overview.md
modules/calendar/overview.md               ← for ICalendarConflictService interface
modules/workforce-presence/overview.md     ← for presence_sessions side effect
Userflow/Leave/leave-request-submission.md
Userflow/Leave/leave-approval.md
Userflow/Leave/leave-cancellation.md
Userflow/Leave/leave-balance-view.md
Userflow/Leave/leave-type-configuration.md
Userflow/Leave/leave-policy-setup.md
Userflow/Leave/leave-entitlement-assignment.md

## TASK 4 — Productivity Analytics
current-focus/DEV1-productivity-analytics.md
modules/productivity-analytics/overview.md
modules/reporting-engine/overview.md
modules/activity-monitoring/overview.md    ← for IActivityMonitoringService interface
Userflow/Analytics-Reporting/productivity-dashboard.md
Userflow/Analytics-Reporting/report-creation.md
Userflow/Analytics-Reporting/scheduled-report-setup.md
Userflow/Analytics-Reporting/data-export.md
Userflow/Analytics-Reporting/workforce-snapshot.md
frontend/design-system/patterns/data-visualization.md

## WMS BRIDGES (Dev 1)
current-focus/WMS-bridge-integration.md
docs/wms-integration-analysis.md
backend/bridge-api-contracts.md
backend/external-integrations.md
```

**Total unique files read: ~50**

---

## Notes for ADE Implementation

1. **Base context files are read ONCE** at session start, not per-task. They stay in the agent's context window throughout all 4 tasks.

2. **Task files include exact acceptance criteria as checkboxes.** The agent marks each `- [ ]` → `- [x]` as it completes each item. The orchestrator reads these to determine remaining work.

3. **The agent does NOT read all 23 module overviews.** It reads only the modules referenced by its task files plus cross-module interface modules (e.g., Calendar for `ICalendarConflictService`).

4. **Step 1 (Backend) always completes before Step 2 (Frontend).** Backend commit happens first.

5. **If a cross-dev dependency is missing, the orchestrator skips the task entirely** — it does NOT attempt a partial implementation. The checkbox stays unchecked.

6. **The agent never reads Phase 2 module specs** — only Phase 1 modules it directly works on or depends on.
