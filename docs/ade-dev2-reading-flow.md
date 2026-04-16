# ADE Reading Flow: Dev 2 — Start to End

**What this document is:** The exact sequence of files an ADE agent reads, in order, when
given the command: "You are Dev 2. Build all your tasks."

This covers the full journey — orchestrator startup, base context loading, each of Dev 2's
4 tasks, and the WMS People Sync bridge Dev 2 owns.

---

## Phase 0: Orchestrator Startup

The orchestrator runs first and determines what to do. It reads:

```
1. ade/README.md                        ← How the orchestrator works, what repos to use
2. current-focus/README.md             ← Task assignment table: Dev 2 has 4 tasks
```

From `current-focus/README.md`, the orchestrator extracts:

| Task # | File | Module |
|:-------|:-----|:-------|
| 1 | `current-focus/DEV2-auth-security.md` | Auth |
| 2 | `current-focus/DEV2-core-hr-lifecycle.md` | CoreHR |
| 3 | `current-focus/DEV2-exception-engine.md` | ExceptionEngine |
| 4 | `current-focus/DEV2-notifications.md` | Notifications |

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
- Covert mode hides employee self-service views; does NOT exempt tenant from disclosure

### `AI_CONTEXT/project-context.md`
System architecture map. Key concepts absorbed:
- Two-pillar model: HR Management (Pillar 1) + Workforce Intelligence (Pillar 2)
- Hybrid Permission Model: NOT simple RBAC — roles are templates, Super Admin grants any feature
- Modular monolith: one .NET solution, 23 modules, strict boundaries
- Multi-tenant: every entity has `tenant_id`
- JWT RS256, access token in-memory, refresh in HttpOnly Secure cookie

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
- Resend for email, Azure Blob Storage

### `AI_CONTEXT/known-issues.md`
Gotchas. Key ones absorbed for Dev 2's work:
- BaseRepository handles tenant filtering — never bypass
- `organisation_id` is old/resolved — everything uses `tenant_id` now
- Device JWT uses `type: "agent"` claim — never grant user permissions to agent tokens
- Session chain: `replaced_by_id` links refresh token rotations — always query the active one
- `leave_policies.superseded_by_id` — always get the one where `IS NULL`

---

## Phase 2: ADE Entry Point Scan (First File Read)

The agent reads:

```
ADE-START-HERE.md
```

**What the agent learns:**
- Auth is the second foundational module (all other modules use RBAC from this)
- Phase 1: 16 modules to build (15 + Discrepancy Engine)
- Hybrid Permission Model: roles are templates, not fixed RBAC
- Cross-module communication: direct calls for sync queries, domain events for side effects
- All modules depend on Auth for `[RequirePermission(...)]` middleware
- Device JWT is a separate claim space from user JWT

---

## Phase 3: Task 1 — Auth & Security

### Dependency check
```
DEV1 Infrastructure Setup  ← checks: Does ONEVO.SharedKernel exist in backend repo?
```
If DEV1 Infrastructure is not done, the orchestrator skips Task 1 (and all tasks) and reports blocked.
Assuming Infrastructure is done, agent proceeds.

### Files read for Task 1

```
current-focus/DEV2-auth-security.md    ← Task spec: acceptance criteria, pages to build
```

Task-specific context injected by orchestrator:

```
modules/auth/authentication/overview.md        ← Login, JWT token issuance, device JWT
modules/auth/authorization/overview.md         ← RBAC, 90+ permissions, hybrid model
modules/auth/session-management/overview.md    ← Session tracking, device fingerprinting
modules/auth/mfa/overview.md                   ← TOTP setup, Email OTP, backup codes
modules/auth/audit-logging/overview.md         ← JSON diff interceptor, audit trail
modules/auth/gdpr-consent/overview.md          ← Consent records, monitoring consent type
security/data-classification.md               ← PII fields, data sensitivity levels
infrastructure/multi-tenancy.md               ← JWT tenant isolation, per-tenant branding
backend/shared-kernel.md                      ← RequirePermissionAttribute, ICurrentUser
```

Userflows:
```
Userflow/Auth-Access/login-flow.md             ← Login with MFA + SSO variations
Userflow/Auth-Access/password-reset.md         ← Forgot password + reset flow
Userflow/Auth-Access/mfa-setup.md              ← Enable/disable MFA
Userflow/Auth-Access/gdpr-consent.md           ← Consent collection after login
Userflow/Auth-Access/role-creation.md          ← Create and configure roles
Userflow/Auth-Access/permission-assignment.md  ← Assign permissions to roles
Userflow/Auth-Access/user-invitation.md        ← Invite new users
```

Frontend references:
```
frontend/architecture/app-structure.md
frontend/design-system/components/component-catalog.md   ← Input, Button, Dialog, Switch
frontend/design-system/foundations/color-tokens.md       ← Tenant branding colors
frontend/data-layer/api-integration.md                   ← Auth token management
frontend/data-layer/state-management.md                  ← Auth state in Zustand
```

### What the agent builds

**Step 1 — Backend:**
1. JWT auth (RS256): 15-min access tokens, signed with RSA key pair
2. Refresh token rotation: 7-day, HttpOnly Secure cookie, `replaced_by_id` chain audit
3. RBAC middleware: `[RequirePermission("resource:action")]` on every endpoint
4. 90+ permissions seeded for all 23 modules (workforce:*, exceptions:*, monitoring:*, agent:*, analytics:*, verification:*, leave:*, hr:*, org:*, skills:*, calendar:*, auth:*, settings:*, notifications:*)
5. Default roles: Employee, Manager, HR_Admin, Org_Owner — seeded per tenant
6. Device JWT: `type: "agent"` claim, `device_id` + `tenant_id`, no user permissions
7. GDPR consent type `monitoring` registered for employee monitoring opt-in
8. `sessions` table: device tracking, IP, user agent, last activity
9. MFA setup: TOTP (QR code generation + TOTP verification), Email OTP, backup codes
10. Audit log interceptor: JSON diffs of old/new values on every write command
11. GDPR consent records: type, version, timestamp, employee consent history
12. Argon2id password hashing (replaces any bcrypt from Infrastructure placeholder)
13. Rate limiting: 5 login attempts/min per IP via Redis
14. Account lockout after 10 failed attempts (exponential backoff)
15. Password reset flow: token generation → email → token validation → reset
16. `/api/v1/tenants/resolve?domain={hostname}` — return branding before login

**Step 2 — Frontend:**
1. `(auth)/layout.tsx`: centered card layout, brand logo from tenant resolve
2. `(auth)/login/page.tsx`: email/password form, "Remember me", SSO button, tenant branding (logo/colors)
3. `(auth)/mfa/page.tsx`: 6-digit TOTP input, backup code option, countdown timer
4. `(auth)/forgot-password/page.tsx`: email input for reset request
5. `(auth)/reset-password/page.tsx`: new password + confirmation + token from URL
6. Auth provider: React context, store access token in memory, auto-refresh on 401, redirect to login
7. `admin/roles/page.tsx`: list roles, create/edit with `RolePermissionMatrix` (checkboxes grouped by module)
8. `admin/users/page.tsx`: `UserTable` — invite, view sessions, revoke sessions, disable/enable
9. GDPR consent dialog: shown after login if pending consents, must accept before dashboard
10. User menu dropdown: profile link, security settings, active sessions, logout
11. `PermissionGate` component: wraps children, checks permissions from decoded JWT
12. Colocated: `UserTable.tsx`, `RolePermissionMatrix.tsx`

**After Step 2:** Marks all checkboxes `- [x]` in `DEV2-auth-security.md`. Commits to backend repo and frontend repo.

---

## Phase 4: Task 2 — Employee Lifecycle

### Dependency check
```
DEV1 Core HR Profile   ← checks: Does employees table exist in backend repo?
DEV4 Shared Platform   ← checks: Do workflow_definitions + workflow_instances tables exist?
```
If DEV4 Shared Platform workflow engine is missing → orchestrator skips Task 2 and reports:
"Lifecycle blocked — workflow engine missing. Re-run after DEV4 delivers Shared Platform."

If both dependencies are met, agent proceeds.

### Files read for Task 2

```
current-focus/DEV2-core-hr-lifecycle.md        ← Task spec
```

Task-specific context:

```
modules/core-hr/overview.md                    ← CoreHR module spec: lifecycle events, domain events
backend/notification-system.md                 ← Lifecycle notifications wiring
backend/messaging/event-catalog.md             ← Domain event definitions + consumers
modules/agent-gateway/overview.md              ← Agent revocation on EmployeeTerminated
infrastructure/multi-tenancy.md               ← Tenant-scoped lifecycle data
```

Userflows:
```
Userflow/Employee-Management/employee-onboarding.md   ← Full onboarding: hire → tasks → completion
Userflow/Employee-Management/employee-offboarding.md  ← Termination/resignation + knowledge risk
Userflow/Employee-Management/employee-promotion.md    ← Promotion with salary update
Userflow/Employee-Management/employee-transfer.md     ← Department/team transfer workflow
```

### What the agent builds

**Step 1 — Backend:**
1. `employee_lifecycle_events` table — append-only audit trail, never update/delete rows
2. Event types: `hired`, `promoted`, `transferred`, `salary_change`, `suspended`, `terminated`, `resigned`
3. `onboarding_templates` CRUD (per department or global, reusable task checklists)
4. `onboarding_tasks` — generated from template on hire, assigned to various users
5. Onboarding status tracking: `pending` → `in_progress` → `completed`
6. `offboarding_records` — initiated on termination/resignation
7. Knowledge risk assessment: `low`, `medium`, `high`, `critical` in offboarding record
8. Penalties tracking: outstanding loans, notice period violations in `penalties_json`
9. Offboarding workflow: routes through workflow engine for manager → HR approval chain
10. Domain events: `EmployeeCreated`, `EmployeePromoted`, `EmployeeTransferred`, `EmployeeTerminated`
11. `EmployeeTerminated` triggers: leave forfeiture, agent device revocation (via AgentGateway)
12. Promotion flow: update `job_title_id` + create `salary_history` entry + append lifecycle event
13. Transfer flow: update `department_id` / team + append lifecycle event
14. Unit tests ≥ 80% coverage

**Step 2 — Frontend:**
1. `hr/onboarding/page.tsx`: active onboarding pipeline — DataTable with `OnboardingProgress` bars per employee
2. `hr/onboarding/[id]/page.tsx`: `OnboardingChecklist` with assignees, due dates, completion toggles
3. `hr/onboarding/components/TaskTemplateEditor.tsx`: create/edit onboarding templates
4. `hr/offboarding/page.tsx`: active offboarding pipeline
5. `hr/offboarding/[id]/page.tsx`: `KnowledgeRiskForm` + penalties summary + `OffboardingChecklist`
6. Promotion dialog: on employee detail page — select new job title, set salary, effective date, reason
7. Transfer dialog: on employee detail page — select new department/team, effective date, reason
8. Lifecycle events timeline: chronological history at `employees/[id]/timeline` (within existing employee detail tabs)
9. `loading.tsx` skeletons for both onboarding and offboarding detail pages
10. Colocated: `OnboardingChecklist.tsx`, `TaskTemplateEditor.tsx`, `OnboardingProgress.tsx`, `OffboardingChecklist.tsx`, `KnowledgeRiskForm.tsx`

**After Step 2:** Marks all checkboxes. Commits.

---

## Phase 5: Task 3 — Exception Engine

### Dependency check
```
DEV3 Activity Monitoring    ← checks: Does IActivityMonitoringService exist in backend repo?
DEV3 Workforce Presence     ← checks: Does IWorkforcePresenceService exist in backend repo?
```
Both DEV3 tasks are Week 3 work. On a first ADE run for Dev 2, both are likely missing.

If either interface is missing → orchestrator skips Task 3 and reports:
"Exception Engine blocked — IActivityMonitoringService and/or IWorkforcePresenceService missing.
Re-run after DEV3 delivers Activity Monitoring and Workforce Presence Setup."

If both dependencies are met, agent proceeds.

### Files read for Task 3

```
current-focus/DEV2-exception-engine.md         ← Task spec
```

Task-specific context:

```
modules/exception-engine/overview.md           ← ExceptionEngine module spec: evaluation flow
modules/activity-monitoring/overview.md        ← IActivityMonitoringService interface
modules/workforce-presence/overview.md         ← IWorkforcePresenceService interface
modules/configuration/monitoring-toggles/overview.md ← Toggles gate evaluation
infrastructure/multi-tenancy.md               ← Tenant-configurable rules and escalation chains
```

Userflows:
```
Userflow/Exception-Engine/exception-rule-setup.md     ← Configure detection rules
Userflow/Exception-Engine/exception-dashboard.md      ← View and manage active exceptions
Userflow/Exception-Engine/alert-review.md             ← Review, acknowledge, dismiss alerts
Userflow/Exception-Engine/escalation-chain-setup.md   ← Configure escalation chains
```

### What the agent builds

**Step 1 — Backend:**

Rules & Configuration:
1. `exception_rules` table — configurable per tenant, severity levels
2. Rule types: `low_activity`, `excess_idle`, `unusual_pattern`, `excess_meeting`, `no_presence`, `break_exceeded`, `verification_failed`
3. `threshold_json` JSONB with per-type schema validation
4. Rules scoped: `all`, `department`, `team`, `employee`
5. Severity levels: `info`, `warning`, `critical`
6. `exception_schedules` table — work hours + days + timezone per tenant

Alert Generation:
7. `exception_alerts` table — generated when rule threshold breached
8. Alert deduplication: one active alert per rule per employee per evaluation window
9. `data_snapshot_json` — evidence captured at trigger time
10. Alert statuses: `new`, `acknowledged`, `dismissed`, `escalated`
11. `alert_acknowledgements` table — audit trail for manager actions

Escalation:
12. `escalation_chains` table — per-severity step ordering (reporting_manager → hr → ceo)
13. Time-based escalation: `delay_minutes` per step
14. `EscalationJob` Hangfire job (every 5 min) — auto-escalate unacknowledged alerts

Evaluation Engine:
15. `ExceptionEngineEvaluationJob` Hangfire job (every 5 min, High queue)
16. Only evaluates during configured work hours (checks `exception_schedules`)
17. Reads activity data via `IActivityMonitoringService` (direct interface call)
18. Reads presence data via `IWorkforcePresenceService` (direct interface call)
19. Checks monitoring toggles + employee overrides via `IConfigurationService` before evaluating
20. Domain events: `ExceptionAlertCreated`, `AlertEscalated`, `AlertAcknowledged`
21. SignalR push on `exception-alerts` channel for new alerts
22. `IExceptionEngineService` public interface implementation
23. Unit tests ≥ 80% coverage

**Step 2 — Frontend:**
1. `workforce/exceptions/page.tsx`:
   - Real-time alert feed (new alerts appear via SignalR `exception-alerts` channel)
   - Filter by severity, rule type, department, status
   - `AlertCard.tsx`: employee name, rule violated, evidence snapshot, timestamp, `SeverityBadge`
   - Actions: acknowledge, dismiss (with reason), escalate manually
2. `workforce/exceptions/[id]/page.tsx`: full `data_snapshot_json` visualization, escalation history, acknowledgement trail
3. `workforce/exceptions/rules/page.tsx` (admin):
   - List rules with enable/disable toggle
   - `RuleEditor.tsx`: type, threshold values, scope, severity with preview text
4. `workforce/exceptions/escalations/page.tsx`:
   - Define chains per severity, add steps with role + delay_minutes
5. Exception schedule configuration: work hours + work days + timezone
6. `SeverityBadge.tsx`: info (blue), warning (yellow), critical (red)
7. Real-time alert count badge in sidebar nav
8. Colocated: `AlertCard.tsx`, `RuleEditor.tsx`, `EscalationChainBuilder.tsx`, `SeverityBadge.tsx`

**After Step 2:** Marks all checkboxes. Commits.

---

## Phase 6: Task 4 — Notifications

### Dependency check
```
DEV4 Shared Platform      ← checks: Do notification_templates table + /hubs/notifications hub exist?
DEV2 Exception Engine     ← checks: Does IExceptionEngineService exist? (already done in Task 3)
```
If DEV4 Shared Platform scaffold is missing → orchestrator skips Task 4 and reports:
"Notifications blocked — notification channel scaffold from Shared Platform missing."

If dependencies are met, agent proceeds.

### Files read for Task 4

```
current-focus/DEV2-notifications.md            ← Task spec
```

Task-specific context:

```
modules/notifications/overview.md                       ← Notifications module: pipeline, channels
modules/notifications/notification-templates/overview.md ← Template schema, rendering engine
modules/notifications/notification-channels/overview.md  ← Channel providers (Resend, in-app, SignalR)
modules/notifications/signalr-real-time/overview.md      ← Real-time push channel specs
backend/notification-system.md                          ← System-wide notification architecture
```

Userflows:
```
Userflow/Notifications/notification-preference-setup.md  ← Configure per-event preferences
Userflow/Notifications/notification-view.md              ← View notification inbox
```

### What the agent builds

**Step 1 — Backend:**
1. `notification_templates` table — per `event_type` per channel (email, in_app, signalr)
2. Template rendering via Liquid/Handlebars engine
3. `notification_channels` table — email (Resend), in-app, SignalR with encrypted credentials
4. 6-step pipeline: event → resolve recipients → load template → render → dispatch → log
5. Workforce Intelligence event types: `exception.alert.created`, `exception.alert.escalated`, `verification.failed`, `agent.heartbeat.lost`, `productivity.daily.report`, `productivity.weekly.report`
6. HR event types: `leave.requested`, `leave.approved`, `leave.rejected`, `review.cycle.started`, `onboarding.started`
7. SignalR hub at `/hubs/notifications`
8. SignalR channels: `notifications-{userId}`, `exception-alerts`, `workforce-live`, `agent-status`
9. `GET /api/v1/notifications` — list (paginated, cursor-based)
10. `PUT /api/v1/notifications/{id}/read` — mark as read
11. `PUT /api/v1/notifications/read-all` — mark all as read
12. `GET/PUT /api/v1/notifications/preferences` — user notification preferences
13. Domain event listeners for all registered event types
14. Unit tests ≥ 80% coverage

**Step 2 — Frontend:**
1. `NotificationBell` component in `DashboardLayout` topbar: dropdown of recent notifications, unread count badge, real-time updates via SignalR `notifications-{userId}` channel
2. `notifications/page.tsx`: full notification inbox — paginated list, filter, mark as read, bulk actions
3. `notifications/preferences/page.tsx`: per-event-type channel toggles (email on/off, in-app on/off)
4. Toast notifications for high-priority alerts (`critical` severity exceptions)
5. `PermissionGate`: `notifications:read`, `notifications:manage`

**After Step 2:** Marks all checkboxes. Commits.

---

## Phase 7: WMS Bridge (Dev 2 Owned)

After all 4 tasks complete, Dev 2 also owns this Phase 1 bridge:

### Bridge 1: People Sync (after Task 2 — Employee Lifecycle is done)

```
current-focus/WMS-bridge-integration.md       ← Bridge spec + all bridge schemas
docs/wms-integration-analysis.md              ← Context for why bridges exist
backend/bridge-api-contracts.md               ← Request/response schemas
backend/external-integrations.md              ← Bridge endpoint registry
```

Builds:
- `POST /api/v1/bridges/people/sync` — receives employee batch from WMS, upserts into `employees` table
- `bridge_api_keys` table with HMAC-SHA256 key hashing (NOT bcrypt — see SEC-01 fix)
- WMS webhook signature validation on every bridge request

---

## Phase 8: Orchestrator Final Report

After all tasks complete (or are blocked), the orchestrator outputs:

```
Session complete.
  ✓ Completed: Task 1 (Auth & Security), Task 2 (Employee Lifecycle)
  ✓ WMS Bridge: Bridge 1 (People Sync)
  ✗ Blocked: Task 3 (Exception Engine) — needs IActivityMonitoringService from DEV3, IWorkforcePresenceService from DEV3
  ✗ Blocked: Task 4 (Notifications) — needs DEV4 Shared Platform notification scaffold

  Re-run after DEV3 delivers Activity Monitoring + Workforce Presence Setup,
  and DEV4 delivers Shared Platform.
```

---

## Full File Read Order (Canonical Sequence)

This is the definitive ordered list of every file the ADE agent reads for Dev 2, top to bottom:

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

## TASK 1 — Auth & Security
current-focus/DEV2-auth-security.md
modules/auth/authentication/overview.md
modules/auth/authorization/overview.md
modules/auth/session-management/overview.md
modules/auth/mfa/overview.md
modules/auth/audit-logging/overview.md
modules/auth/gdpr-consent/overview.md
security/data-classification.md
infrastructure/multi-tenancy.md
backend/shared-kernel.md
Userflow/Auth-Access/login-flow.md
Userflow/Auth-Access/password-reset.md
Userflow/Auth-Access/mfa-setup.md
Userflow/Auth-Access/gdpr-consent.md
Userflow/Auth-Access/role-creation.md
Userflow/Auth-Access/permission-assignment.md
Userflow/Auth-Access/user-invitation.md
frontend/architecture/app-structure.md
frontend/design-system/components/component-catalog.md
frontend/design-system/foundations/color-tokens.md
frontend/data-layer/api-integration.md
frontend/data-layer/state-management.md

## TASK 2 — Employee Lifecycle
current-focus/DEV2-core-hr-lifecycle.md
modules/core-hr/overview.md
backend/notification-system.md
backend/messaging/event-catalog.md
modules/agent-gateway/overview.md        ← for agent revocation on EmployeeTerminated
Userflow/Employee-Management/employee-onboarding.md
Userflow/Employee-Management/employee-offboarding.md
Userflow/Employee-Management/employee-promotion.md
Userflow/Employee-Management/employee-transfer.md

## TASK 3 — Exception Engine
current-focus/DEV2-exception-engine.md
modules/exception-engine/overview.md
modules/activity-monitoring/overview.md  ← for IActivityMonitoringService interface
modules/workforce-presence/overview.md   ← for IWorkforcePresenceService interface
modules/configuration/monitoring-toggles/overview.md
Userflow/Exception-Engine/exception-rule-setup.md
Userflow/Exception-Engine/exception-dashboard.md
Userflow/Exception-Engine/alert-review.md
Userflow/Exception-Engine/escalation-chain-setup.md
frontend/design-system/foundations/color-tokens.md  ← severity colors
frontend/design-system/patterns/data-visualization.md

## TASK 4 — Notifications
current-focus/DEV2-notifications.md
modules/notifications/overview.md
modules/notifications/notification-templates/overview.md
modules/notifications/notification-channels/overview.md
modules/notifications/signalr-real-time/overview.md
backend/notification-system.md
Userflow/Notifications/notification-preference-setup.md
Userflow/Notifications/notification-view.md

## WMS BRIDGES (Dev 2)
current-focus/WMS-bridge-integration.md
docs/wms-integration-analysis.md
backend/bridge-api-contracts.md
backend/external-integrations.md
```

**Total unique files read: ~48**

---

## Notes for ADE Implementation

1. **Task 1 (Auth) is the only non-blocked task on a fresh start.** Tasks 3 and 4 require DEV3
   and DEV4 work. Expect typical first-run result: Task 1 ✓, Task 2 ✓ (if DEV4 done), Task 3 ✗, Task 4 ✗.

2. **The 90+ permissions seeded in Task 1 must include permissions for ALL 23 modules,** including
   modules Dev 2 doesn't build. An agent reading only its own task files must be reminded (via
   `modules/auth/authorization/overview.md`) to seed permissions for all modules.

3. **Exception Engine evaluation reads data via interfaces, never directly.** The agent must call
   `IActivityMonitoringService` and `IWorkforcePresenceService` — never query those module's tables
   directly. Module boundary enforcement is critical here.

4. **Notifications is the integration hub.** Dev 2's Notifications module wires together events from
   Leave (Dev 1), Exception Engine (Dev 2), Productivity (Dev 1), and Agent Gateway (Dev 4). The
   agent must understand the full event catalog, not just its own events.

5. **Step 1 (Backend) always completes before Step 2 (Frontend).** Backend commit happens first.

6. **If a cross-dev dependency is missing, the orchestrator skips the task entirely** — no partial
   implementation. Checkboxes stay unchecked.
