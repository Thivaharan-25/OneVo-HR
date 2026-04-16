# ADE Reading Flow: Dev 4 — Start to End

**What this document is:** The exact sequence of files an ADE agent reads, in order, when
given the command: "You are Dev 4. Build all your tasks."

This covers the full journey — orchestrator startup, base context loading, each of Dev 4's
4 tasks, and the WMS Tenant Provisioning bridge Dev 4 owns.

> **⚠️ CRITICAL ADE ORDERING PROBLEM — Read before running Dev 4's session.**
> Task 3 (Identity Verification) depends on the `biometric_devices` table, which is built in
> Task 4 (Workforce Presence Biometric). Since tasks run sequentially 1→2→3→4, Task 3 will
> always be SKIPPED on the first ADE run. Task 4 will run, then on a second ADE run Task 3
> will become unblocked. See flagged issues section at the end of this document.

---

## Phase 0: Orchestrator Startup

The orchestrator runs first and determines what to do. It reads:

```
1. ade/README.md                        ← How the orchestrator works, what repos to use
2. current-focus/README.md             ← Task assignment table: Dev 4 has 4 tasks
```

From `current-focus/README.md`, the orchestrator extracts:

| Task # | File | Module |
|:-------|:-----|:-------|
| 1 | `current-focus/DEV4-shared-platform-agent-gateway.md` | SharedPlatform + AgentGateway |
| 2 | `current-focus/DEV4-configuration.md` | Configuration |
| 3 | `current-focus/DEV4-identity-verification.md` | IdentityVerification |
| 4 | `current-focus/DEV4-workforce-presence-biometric.md` | WorkforcePresence (Biometric) |

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
- Never capture agent data outside monitoring lifecycle (clock-in → clock-out)
- Phase 2 guard: macOS agent support is Phase 2 — do not build
- API key hashing: use SHA-256 (HMAC-SHA256 for bridge keys) — NOT bcrypt
- Checkbox tracking: mark `- [ ]` → `- [x]` as each criterion is completed

### `AI_CONTEXT/project-context.md`
System architecture map. Key concepts absorbed:
- Dev 4 owns the foundational platform layer (SharedPlatform + AgentGateway) that all other modules depend on
- Bidirectional SignalR: agent → server (data push), server → agent (commands)
- Three-tier App Allowlist: tenant → role → employee; most specific wins
- Workflow engine: `resource_type + resource_id` pattern — usable by any module
- Device JWT: completely separate from user JWT, `type: "agent"` claim, no HR permissions
- Monitoring Lifecycle: agent only sends data while employee is clocked in (GDPR)

### `AI_CONTEXT/tech-stack.md`
Technology choices. Key items absorbed:
- .NET 9 MAUI for WorkPulse Agent (Windows desktop client)
- SignalR for bidirectional agent ↔ server communication
- Redis for feature flag cache (5-min TTL)
- Stripe for subscription management
- HMAC-SHA256 for biometric webhook signature validation
- Azure Blob Storage for verification photos (RESTRICTED classification)
- `pg_partman` for partitioned activity tables

### `AI_CONTEXT/known-issues.md`
Gotchas. Key ones absorbed for Dev 4's work:
- Device JWT uses `type: "agent"` claim — never grant user permissions to agent tokens
- Feature flag cache has 5-min TTL — don't cache longer than this
- Biometric webhook must validate HMAC-SHA256 signature on every request
- `monitoring_feature_toggles` seeding: when tenant is provisioned with industry_profile, seed default toggles (office_it, manufacturing, retail, healthcare)
- Agent rate limiting: 30 req/min/device — enforced via Redis sliding window
- Verification photos are RESTRICTED — serve via SAS tokens, never permanent URLs

---

## Phase 2: ADE Entry Point Scan (First File Read)

The agent reads:

```
ADE-START-HERE.md
```

**What the agent learns:**
- SharedPlatform + AgentGateway is Week 1 — the foundational gateway layer
- Agent Gateway provides the data pipeline all of Workforce Intelligence depends on
- macOS agent is Phase 2 — do NOT build
- Screen recording is Phase 2 — do NOT build
- App blocking is Phase 2 — do NOT build
- `IConfigurationService` is a key public interface consumed by Activity Monitoring, Exception Engine, Agent Policy merge
- Tenant Provisioning WMS bridge (Bridge 4) is Phase 1 — owned by Dev 4
- Productivity Metrics bridge and Skills bridge are Phase 2 — do NOT build

---

## Phase 3: Task 1 — Shared Platform + Agent Gateway

### Dependency check
```
DEV1 Infrastructure Setup  ← checks: Does ONEVO.SharedKernel exist in backend repo?
DEV2 Auth & Security       ← checks: Does Device JWT validation exist (type: "agent" claim)?
```
If Auth is not done → orchestrator skips Task 1 and reports:
"Shared Platform blocked — Device JWT validation missing. Re-run after DEV2 delivers Auth."

If both dependencies are met, agent proceeds.

### Files read for Task 1

```
current-focus/DEV4-shared-platform-agent-gateway.md    ← Task spec: acceptance criteria, pages to build
```

Task-specific context injected by orchestrator:

```
modules/agent-gateway/overview.md                      ← AgentGateway module: ingest, policy, registration
modules/configuration/monitoring-toggles/overview.md   ← Policy merge: toggles + employee overrides
backend/external-integrations.md                       ← Stripe integration pattern
backend/notification-system.md                         ← Notification pipeline scaffold
backend/messaging/event-catalog.md                     ← Workflow events, agent events
infrastructure/multi-tenancy.md                        ← Tenant context for all platform services
```

Userflows:
```
Userflow/Platform-Setup/sso-configuration.md          ← SSO provider setup
Userflow/Platform-Setup/billing-subscription.md       ← Manage subscription and billing
Userflow/Platform-Setup/feature-flag-management.md    ← Manage feature flags
Userflow/Platform-Setup/tenant-branding.md            ← Customize tenant branding
Userflow/Workforce-Intelligence/agent-deployment.md   ← Deploy and manage desktop agents
Userflow/Notifications/notification-preference-setup.md ← Configure notification channels
```

Frontend references:
```
frontend/design-system/components/component-catalog.md   ← DataTable, StatusBadge, Switch, Card
frontend/design-system/foundations/color-tokens.md       ← Status + brand colors
frontend/data-layer/api-integration.md
```

### What the agent builds

**Step 1 — Backend:**

Shared Platform:
1. SSO provider config (SAML, OIDC — metadata URL, client ID/secret; config only, not full flow)
2. Refresh token rotation table with `replaced_by_id` chain
3. Subscription plans seeded: Free, Pro, Enterprise with feature limits
4. Tenant subscription management: Stripe webhook integration (`/api/v1/stripe/webhook`)
5. Feature flag system: 4 types (global, org, user, percentage rollout)
6. Feature flag Redis cache with 5-min TTL
7. Tenant branding: custom domain, logo, primary/secondary colors
8. **Workflow engine:**
   - `workflow_definitions` — reusable workflow schemas with steps and conditions
   - `workflow_steps` — ordered steps with JSONB conditions and SLA timeouts
   - `workflow_instances` — active workflow runs keyed to `resource_type + resource_id`
   - `approval_actions` — audit trail of approvals, rejections, delegations
   - Supports: conditional routing, SLA timeouts, delegation
   - Usable by any module via `resource_type` + `resource_id`
9. Notification templates table + channel configuration with encrypted credentials (scaffold for DEV2 Notifications)

Agent Gateway:
10. `registered_agents` CRUD (device registration, device JWT issuance)
11. `agent_policies` table — JSON schema validated, includes `document_tracking`, `communication_tracking`, `browser_extension_enabled` flags
12. `agent_health_logs` table
13. `POST /api/v1/agent/register` — register device, return device JWT
14. `POST /api/v1/agent/heartbeat` — update `last_heartbeat_at`, report health metrics
15. `GET /api/v1/agent/policy` — fetch merged policy (tenant toggles + employee overrides)
16. `POST /api/v1/agent/ingest` — high-throughput data ingestion (202 Accepted, async queue); handles `document_usage` and `communication_usage` batch types
17. `POST /api/v1/agent/login` — link employee to device
18. `POST /api/v1/agent/logout` — unlink employee
19. Device JWT authentication (`type: "agent"` claim, validated separately from user JWT)
20. Rate limiting per device: 30 req/min/device via Redis sliding window
21. `DetectOfflineAgentsJob` Hangfire job — flag agents with no heartbeat for 5+ min

WorkPulse Agent (Windows .NET MAUI):
22. `DocumentTracker.cs` — foreground process matching for Word/Excel/PPT/Figma/Photoshop
23. `CommunicationTracker.cs` — Outlook/Slack/Teams active time + UIAutomation send event counts
24. Screenshot trigger: `manual` and `on_demand` only — NO `scheduled` or `random` triggers
25. `Package.appxmanifest` — update `DisplayName` to "WorkPulse Agent"
26. Personal break toggle in TrayApp — pauses all collectors, records period as "Personal Time"

**Step 2 — Frontend:**
1. `admin/agents/page.tsx`: DataTable — device name, employee, status badge (green/red/yellow), last heartbeat, OS, version
2. `admin/agents/[id]/page.tsx`: health log, policy view, registration info; `AgentCommandPanel.tsx` for bulk actions
3. `admin/audit/page.tsx`: `AuditLogViewer.tsx` — filterable audit log
4. `admin/devices/page.tsx`: hardware terminal listing
5. `admin/compliance/page.tsx`: GDPR, data governance settings
6. SSO configuration page: provider setup form (SAML/OIDC), test connection button
7. Billing page: current plan card, upgrade/downgrade → Stripe checkout, invoice history
8. Feature flag management page (super admin): DataTable + toggle on/off + targeting rules
9. Notification settings page: channel config, template preview per event type
10. Tenant branding page: logo upload, colors, custom domain, live preview
11. Colocated: `AgentStatusCard.tsx`, `AgentCommandPanel.tsx`, `AuditLogViewer.tsx`

**After Step 2:** Marks all checkboxes in `DEV4-shared-platform-agent-gateway.md`. Commits.

---

## Phase 4: Task 2 — Configuration

### Dependency check
```
DEV1 Infrastructure Setup  ← checks: Does ONEVO.SharedKernel exist? Does industry_profile seeding exist?
DEV4 Shared Platform       ← checks: Do workflow_definitions table + tenant context exist? (just completed in Task 1)
```
Task 1 just completed, so DEV4 Shared Platform is met. DEV1 Infrastructure should be done. Agent proceeds.

### Files read for Task 2

```
current-focus/DEV4-configuration.md                    ← Task spec
```

Task-specific context:

```
modules/configuration/overview.md                      ← Configuration module spec + IConfigurationService
modules/configuration/monitoring-toggles/overview.md   ← Toggle schema, industry defaults
modules/configuration/employee-overrides/overview.md   ← Override merge logic (employee wins)
modules/configuration/tenant-settings/overview.md      ← Settings schema
modules/configuration/retention-policies/overview.md   ← Per-type retention periods
infrastructure/multi-tenancy.md
```

Userflows:
```
Userflow/Configuration/monitoring-toggles.md           ← Toggle monitoring features
Userflow/Configuration/employee-override.md            ← Override monitoring per employee
Userflow/Configuration/retention-policy-setup.md       ← Configure data retention
Userflow/Configuration/tenant-settings.md              ← Manage tenant settings
```

### What the agent builds

**Step 1 — Backend:**
1. `tenant_settings` table — timezone, date format, work hours, privacy mode (`full`, `partial`, `covert`)
2. `monitoring_feature_toggles` table — global ON/OFF per monitoring feature per tenant
3. Industry profile default seeding: `office_it`, `manufacturing`, `retail`, `healthcare`, `custom` — seeds `monitoring_feature_toggles` on tenant provisioning
4. `employee_monitoring_overrides` table — per-employee feature overrides
5. Merge logic: employee override wins over tenant toggle
6. Bulk override API: `POST /api/v1/config/employee-overrides/bulk` — set by department/team/job family
7. `integration_connections` table — external service connections with encrypted credentials
8. `retention_policies` table — per data type retention periods
9. `app_allowlist` table — application allowlist scoped to tenant/department/team/employee
10. Resolved allowlist API: merge tenant → department → team → employee (most specific wins)
11. `IConfigurationService` public interface — all methods: `GetToggleAsync`, `GetEmployeeOverrideAsync`, `GetRetentionPolicyAsync`, `GetAllowlistAsync`
12. Full CRUD endpoints for all configuration entities
13. Unit tests ≥ 80% coverage

**Step 2 — Frontend:**
1. `settings/monitoring/page.tsx`: master toggle per feature (screenshots, app tracking, meeting detection, browser activity, verification), employee override management
2. Bulk override: select department/team, apply feature toggles
3. `settings/general/page.tsx`: `SettingsForm.tsx` — timezone, date format, work hours, privacy mode
4. `settings/integrations/page.tsx`: `IntegrationCard.tsx` list — add, test connections
5. Colocated: `SettingsForm.tsx`, `IntegrationCard.tsx`
6. `PermissionGate`: `monitoring:view-settings`, `monitoring:configure`, `settings:manage`

**After Step 2:** Marks all checkboxes in `DEV4-configuration.md`. Commits.

---

## Phase 5: Task 3 — Identity Verification

### Dependency check
```
DEV4 Shared Platform + Agent Gateway  ← checks: Does POST /api/v1/agent/ingest exist? (done in Task 1)
DEV4 Workforce Presence Biometric     ← checks: Does biometric_devices table exist in backend repo?
```

> **⚠️ CRITICAL ORDERING PROBLEM:**
> `biometric_devices` is built in Task 4 (Workforce Presence Biometric), which has NOT run yet.
> This means **Task 3 will always be SKIPPED on the first ADE run for Dev 4.**
>
> The orchestrator will report:
> "Identity Verification blocked — biometric_devices table missing (needs DEV4 Biometric, Task 4).
>  Task 4 will run this session. Re-run Dev 4 session after this session completes to unblock Task 3."
>
> On the **second ADE run**, both dependencies will be met and Task 3 will execute.
>
> **Recommended fix:** Swap Task 3 and Task 4 in `current-focus/README.md` so Biometric runs first.
> See flagged issues section below.

If (on second run) both dependencies are met, agent proceeds.

### Files read for Task 3

```
current-focus/DEV4-identity-verification.md            ← Task spec
```

Task-specific context:

```
modules/identity-verification/overview.md              ← IdentityVerification module spec
modules/configuration/monitoring-toggles/overview.md   ← Monitoring overrides gate verification
modules/workforce-presence/overview.md                 ← VerificationCompleted confirms presence
security/data-classification.md                       ← Verification photos are RESTRICTED
infrastructure/multi-tenancy.md                       ← Per-tenant verification policies
```

Userflows:
```
Userflow/Workforce-Intelligence/identity-verification-setup.md   ← Configure policies
Userflow/Workforce-Intelligence/identity-verification-review.md  ← Review records + failures
```

### What the agent builds

**Step 1 — Backend:**
1. `verification_policies` table — per-tenant config: login/logout/interval triggers, match threshold (default 80.0)
2. `verification_records` table — each verification event with confidence score (0–100)
3. Photo verification endpoint: agent sends photo → compare against employee avatar → return match result
4. Verification statuses: `verified`, `failed`, `skipped`, `expired`
5. Failure reason tracking for failed verifications
6. `IIdentityVerificationService` public interface implementation
7. Domain events: `VerificationFailed` → triggers exception engine alert + notification; `VerificationCompleted` → updates workforce presence session
8. Verification respects monitoring overrides: skip if `identity_verification = false` for employee
9. `PurgeExpiredVerificationPhotosJob` (daily 2 AM) — delete photos past retention period
10. `CheckBiometricDeviceHealthJob` (every 5 min) — flag offline devices (uses `biometric_devices` from Task 4)
11. Verification photos: RESTRICTED data, blob storage, default 30-day retention
12. Phase 1: simple photo comparison against employee avatar. Phase 2: ML matching (do not build)
13. Unit tests ≥ 80% coverage

**Step 2 — Frontend:**
1. `workforce/verification/page.tsx`:
   - `VerificationLogTable.tsx`: DataTable — employee, timestamp, status badge, confidence score, trigger (login/logout/interval)
   - Filter by status, date range, department
   - Failed verifications highlighted with `SeverityBadge`
   - Click row: captured photo vs profile photo side-by-side, confidence score, failure reason
2. `workforce/verification/pending/page.tsx`:
   - `PendingRequestCard.tsx`: pending verification details
3. Verification policy configuration (admin):
   - Trigger settings: on login, on logout, periodic interval (minutes)
   - Match threshold slider (0–100, default 80)
   - Retention period for verification photos
   - Enable/disable per tenant
4. Verification statistics widget: success rate %, total verifications today, failed count, trend chart
5. `PermissionGate`: `verification:read`, `verification:configure`
6. Colocated: `VerificationLogTable.tsx`, `PendingRequestCard.tsx`

**After Step 2:** Marks all checkboxes in `DEV4-identity-verification.md`. Commits.

---

## Phase 6: Task 4 — Workforce Presence Biometric

### Dependency check
```
DEV4 Shared Platform + Agent Gateway  ← checks: Does workflow engine exist? (Task 1, done)
DEV2 Auth & Security                  ← checks: Does HMAC webhook secret management exist?
DEV3 Workforce Presence Setup         ← checks: Do presence_sessions + device_sessions tables exist?
```
If DEV3 Workforce Presence Setup is missing → orchestrator skips Task 4 and reports:
"Biometric blocked — presence_sessions table missing from DEV3 Workforce Presence Setup."

If dependencies are met, agent proceeds.

### Files read for Task 4

```
current-focus/DEV4-workforce-presence-biometric.md     ← Task spec
```

Task-specific context:

```
modules/workforce-presence/overview.md                 ← WorkforcePresence module: biometric integration
modules/identity-verification/overview.md              ← biometric_devices table is shared here
modules/agent-gateway/overview.md                      ← Agent data integration
backend/notification-system.md                         ← Presence event notifications
infrastructure/multi-tenancy.md                        ← Tenant-scoped biometric data
```

Userflows:
```
Userflow/Workforce-Presence/biometric-device-setup.md  ← Register and manage biometric devices
Userflow/Workforce-Presence/attendance-correction.md   ← Correct attendance records
Userflow/Workforce-Presence/overtime-management.md     ← Request and approve overtime
Userflow/Workforce-Presence/break-tracking.md          ← Break records from biometric + agent
```

### What the agent builds

**Step 1 — Backend:**

Biometric Integration:
1. `biometric_devices` CRUD (from identity verification module namespace — shared table)
2. `biometric_enrollments` — employee fingerprint enrollment with consent tracking
3. `biometric_events` — raw clock-in/out events from terminals
4. `biometric_audit_logs` — tamper detection, device health records
5. `POST /api/v1/biometric/webhook` — HMAC-SHA256 signature verification on every request
6. Biometric event flow: webhook → `biometric_events` → `attendance_records` → `presence_sessions` (via reconciliation job from DEV3)

Attendance Operations:
7. `attendance_records` — clock-in/out records (biometric source)
8. `overtime_requests` + approval workflow via workflow engine
9. `attendance_corrections` — manager corrections with audit trail
10. Overtime auto-flagging: `total_present_minutes > scheduled_minutes`

Agent Data Integration:
11. Agent device session data (from `/api/v1/agent/ingest`) → `device_sessions` table
12. Agent data merged into `presence_sessions` by reconciliation job (DEV3's `ReconcilePresenceSessions`)
13. Source tracking: `biometric`, `agent`, `manual`, `mixed`
14. Deduplication: earliest `first_seen` + latest `last_seen` from all sources

Domain Events:
15. `PresenceSessionStarted` → notifications
16. `PresenceSessionEnded` → activity monitoring pipeline trigger
17. `BreakExceeded` → exception engine evaluation
18. `OvertimeRequested` → notifications

Now **unblocks DEV4 Identity Verification (Task 3)**: `biometric_devices` table exists.
On the second ADE run, Task 3 will be unblocked.

**Step 2 — Frontend:**
Builds into `workforce/presence/` alongside DEV3's pages:
1. `workforce/presence/attendance/page.tsx` (`AttendanceTable.tsx` — shared with DEV3's skeleton):
   - DataTable: employee, date, check-in, check-out, source badge (biometric/agent/manual/mixed), total hours
   - Filter by date range, department, source
2. Attendance correction dialog: select employee + date, modify times, reason, audit trail
3. `workforce/presence/overtime/page.tsx` (`OvertimeTable.tsx` — shared with DEV3's skeleton):
   - Pending requests for manager approval
   - Request detail: employee, date, scheduled hours, actual hours, overtime hours
   - Approve/reject with comments
   - Auto-flagged overtime list
4. `BiometricDeviceCard.tsx` (populates DEV3's placeholder component):
   - DataTable: device name, type, location, status (online/offline), last event
   - Device registration form (name, type, API key, location)
   - Device health alert for offline devices
5. Employee enrollment management: list enrolled per device, enrollment flow with consent
6. `PermissionGate`: `workforce:manage-biometric`, `workforce:correct-attendance`, `workforce:approve-overtime`

**After Step 2:** Marks all checkboxes in `DEV4-workforce-presence-biometric.md`. Commits.

---

## Phase 7: WMS Bridge (Dev 4 Owned)

After all 4 tasks complete, Dev 4 also owns this Phase 1 bridge:

### Bridge 4: Tenant Provisioning (after Task 1 — Shared Platform is done)

```
current-focus/WMS-bridge-integration.md       ← Bridge spec + all bridge schemas
docs/wms-integration-analysis.md              ← Context for why bridges exist
backend/bridge-api-contracts.md               ← Request/response schemas
backend/external-integrations.md              ← Bridge endpoint registry
```

Builds:
- `POST /api/v1/bridges/tenants/provision` — provision a new ONEVO tenant from WMS
  (WMS sends tenant details → creates tenant + seeds defaults + returns tenant_id)
- `POST /api/v1/bridges/tenants/{tenantId}/roles/map` — map WMS roles to ONEVO roles
- Bridge authenticated via HMAC-SHA256 bridge API key (NOT bcrypt — see SEC-01 fix)

---

## Phase 8: Orchestrator Final Report

**First ADE run (expected):**
```
Session complete.
  ✓ Completed: Task 1 (Shared Platform + Agent Gateway), Task 2 (Configuration)
  ✗ Blocked: Task 3 (Identity Verification) — biometric_devices table missing (needs Task 4)
  ✓ Completed: Task 4 (Workforce Presence Biometric)
  ✓ WMS Bridge: Bridge 4 (Tenant Provisioning)

  Task 3 is now unblocked (Task 4 just built biometric_devices).
  Re-run Dev 4 ADE session to complete Identity Verification.
```

**Second ADE run:**
```
Session complete.
  ✓ Completed: Task 3 (Identity Verification)
  All Dev 4 Phase 1 tasks complete.
```

---

## Full File Read Order (Canonical Sequence)

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

## TASK 1 — Shared Platform + Agent Gateway
current-focus/DEV4-shared-platform-agent-gateway.md
modules/agent-gateway/overview.md
modules/configuration/monitoring-toggles/overview.md
backend/external-integrations.md
backend/notification-system.md
backend/messaging/event-catalog.md
infrastructure/multi-tenancy.md
Userflow/Platform-Setup/sso-configuration.md
Userflow/Platform-Setup/billing-subscription.md
Userflow/Platform-Setup/feature-flag-management.md
Userflow/Platform-Setup/tenant-branding.md
Userflow/Workforce-Intelligence/agent-deployment.md
Userflow/Notifications/notification-preference-setup.md
frontend/design-system/components/component-catalog.md
frontend/design-system/foundations/color-tokens.md
frontend/data-layer/api-integration.md

## TASK 2 — Configuration
current-focus/DEV4-configuration.md
modules/configuration/overview.md
modules/configuration/monitoring-toggles/overview.md  ← already loaded, re-reads for full spec
modules/configuration/employee-overrides/overview.md
modules/configuration/tenant-settings/overview.md
modules/configuration/retention-policies/overview.md
Userflow/Configuration/monitoring-toggles.md
Userflow/Configuration/employee-override.md
Userflow/Configuration/retention-policy-setup.md
Userflow/Configuration/tenant-settings.md

## TASK 3 — Identity Verification (SKIPPED on first run; runs on second run)
current-focus/DEV4-identity-verification.md
modules/identity-verification/overview.md
modules/workforce-presence/overview.md              ← for VerificationCompleted side effect
security/data-classification.md                     ← verification photos are RESTRICTED
Userflow/Workforce-Intelligence/identity-verification-setup.md
Userflow/Workforce-Intelligence/identity-verification-review.md
frontend/design-system/patterns/data-visualization.md ← trend chart

## TASK 4 — Workforce Presence Biometric
current-focus/DEV4-workforce-presence-biometric.md
modules/workforce-presence/overview.md              ← already loaded, re-reads for biometric section
modules/identity-verification/overview.md           ← biometric_devices shared table
modules/agent-gateway/overview.md                   ← agent data integration
backend/notification-system.md
Userflow/Workforce-Presence/biometric-device-setup.md
Userflow/Workforce-Presence/attendance-correction.md
Userflow/Workforce-Presence/overtime-management.md
Userflow/Workforce-Presence/break-tracking.md
frontend/design-system/foundations/color-tokens.md  ← device status colors

## WMS BRIDGES (Dev 4)
current-focus/WMS-bridge-integration.md
docs/wms-integration-analysis.md
backend/bridge-api-contracts.md
backend/external-integrations.md
```

**Total unique files read: ~46**

---

## Known Issues Flagged During Read Flow Analysis

### ISSUE 1 — Identity Verification (Task 3) Will Always Be Skipped on First Run

**Severity: Critical for ADE correctness**

`DEV4-identity-verification.md` lists `DEV4-workforce-presence-biometric.md` as a dependency
because Identity Verification needs the `biometric_devices` table. But Biometric is **Task 4**,
which hasn't run yet when Task 3 runs.

**What happens on first run:**
- Task 1 (Shared Platform) → completes
- Task 2 (Configuration) → completes
- Task 3 (Identity Verification) → **SKIPPED** — biometric_devices missing
- Task 4 (Biometric) → completes, creates biometric_devices

**What happens on second run:**
- Task 3 (Identity Verification) → now unblocked, completes

**Fix options:**
- (A) **Swap Task 3 and Task 4** in `current-focus/README.md`. Biometric becomes Task 3,
  Identity Verification becomes Task 4. `biometric_devices` exists before Identity Verification
  needs it. This requires a one-time edit to the README and re-ordering the task files.
- (B) **Remove the biometric_devices dependency** from `DEV4-identity-verification.md` and note
  that `CheckBiometricDeviceHealthJob` is added in a follow-on pass after Task 4 completes.

**Recommended:** Option A. Swap Task 3 ↔ Task 4. No logic change required — just reorder.

---

## Notes for ADE Implementation

1. **Task 1 (Shared Platform + Agent Gateway) is the most critical delivery for the whole project.**
   Every other module that needs the workflow engine, notification scaffolding, or agent data
   pipeline depends on this task completing. DEV1 Leave, DEV2 Lifecycle, DEV3 Workforce Presence,
   and DEV3 Activity Monitoring are all blocked until Task 1 is done.

2. **The WorkPulse Agent (Windows .NET MAUI) is built in Task 1.** The agent code lives in a
   separate repo (`onevo-desktop-agent`). The ADE command must include `--agent ./onevo-desktop-agent`
   for Task 1 to complete fully. See `ade/README.md` for the `ade run` command flags.

3. **`biometric_devices` is a cross-module shared table** defined in the Identity Verification
   module namespace but physically used by Biometric Presence. The agent must place it under
   `ONEVO.Modules.IdentityVerification` namespace, not `WorkforcePresence`. Both modules
   reference it via direct FK — this is the only case where a presence-related table lives in
   an identity namespace.

4. **Two ADE runs are required to complete all Dev 4 tasks** unless the task order is swapped
   (see Issue 1 above). The orchestrator should document this expectation in its final report.

5. **Step 1 (Backend) always completes before Step 2 (Frontend).** Backend commit happens first.

6. **If a cross-dev dependency is missing, the orchestrator skips the task entirely** — no partial
   implementation. Checkboxes stay unchecked.
