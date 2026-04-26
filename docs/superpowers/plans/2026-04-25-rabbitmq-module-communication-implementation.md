# RabbitMQ Module Communication — Documentation Plan

> **What this plan does:** Updates the markdown documentation files in this repo to reflect the RabbitMQ architecture decisions already captured in ADR-001 and exchange-topology.md. No C# code. Only doc file changes.

**Goal:** Every file that describes module events, database tables, or messaging must consistently say "Phase 1 = RabbitMQ via MassTransit for cross-module events, MediatR for intra-module only" — no file should still say MediatR is Phase 1 cross-module transport.

---

## Pre-work Already Completed ✅

Do NOT redo these:

| Done | File |
|:-----|:-----|
| ✅ | `docs/decisions/ADR-001-per-module-database-and-event-bus.md` — written |
| ✅ | `backend/README.md` — Architecture Decisions section added |
| ✅ | `backend/module-boundaries.md` — Per-Module Database Contexts section added |
| ✅ | `backend/messaging/exchange-topology.md` — rewritten; RabbitMQ is Phase 1 |
| ✅ | `AI_CONTEXT/tech-stack.md` — RabbitMQ moved from "NOT Using" to Infrastructure |

---

## What Needs Changing (4 tasks)

---

## Task 1: Fix `backend/messaging/event-catalog.md`

**Why:** The opening line still says *"Phase 1 uses in-process MediatR INotification"* — that is now wrong. The event format block only shows `DomainEvent`; it needs to also show `IntegrationEvent`.

**File:** `backend/messaging/event-catalog.md`

- [ ] **Step 1: Replace the opening paragraph**

Change:
```
All domain events published and consumed across modules. Phase 1 uses in-process MediatR `INotification` (see [[backend/messaging/exchange-topology|Exchange Topology]]); future phases migrate to RabbitMQ for scale.
```

To:
```
All events published and consumed across modules. Phase 1 uses **RabbitMQ via MassTransit** for cross-module integration events and **MediatR `INotification`** for intra-module domain events only (see [[backend/messaging/exchange-topology|Exchange Topology]]). See [[backend/messaging/error-handling|Error Handling]] for retry and idempotency patterns.
```

- [ ] **Step 2: Replace the Event Format block**

Replace the single `DomainEvent` block with two blocks:

```markdown
## Event Types

### Domain Event (intra-module — MediatR only)

Published and handled within the same module. Never crosses a module boundary.

\```csharp
public abstract record DomainEvent
{
    public Guid EventId { get; init; } = Guid.NewGuid();
    public DateTimeOffset OccurredAt { get; init; } = DateTimeOffset.UtcNow;
    public Guid TenantId { get; init; }
}
\```

### Integration Event (cross-module — RabbitMQ via IEventBus)

Published via `IEventBus.PublishAsync()` → written to module outbox → delivered by RabbitMQ. Consumers use `IConsumer<T>` with inbox-state idempotency.

\```csharp
public abstract record IntegrationEvent
{
    public Guid EventId { get; init; } = Guid.NewGuid();
    public DateTimeOffset OccurredAt { get; init; } = DateTimeOffset.UtcNow;
    public abstract Guid TenantId { get; init; }
    public string EventType => GetType().Name;
}
\```
```

- [ ] **Step 3: Add a "Routing Key" column to each event table**

For each event section table, add a `Routing Key` column showing the RabbitMQ routing key pattern, e.g.:

| Event | Routing Key | Publisher | Payload | Consumers |
|:------|:-----------|:---------|:--------|:----------|
| `LeaveApproved` | `leave.request.approved` | Leave | … | Payroll, Calendar, WorkforcePresence, Notifications |

Use the routing key patterns already defined in `backend/messaging/exchange-topology.md`:
- Infrastructure events → `infrastructure.*`
- Auth events → `auth.*`
- Core HR events → `core-hr.employee.*`
- Workforce Presence events → `workforce.presence.*`
- Agent Gateway events → `agent.gateway.*`
- Activity Monitoring events → `activity.*`
- Identity Verification events → `identity.*`
- Exception Engine events → `exception.*`
- Productivity Analytics events → `analytics.*`
- Leave events → `leave.request.*`
- Payroll events → `payroll.run.*`
- Performance events → `performance.review.*`
- Skills events → `skills.*`
- Documents events → `documents.*`
- Grievance events → `grievance.*`
- Expense events → `expense.*`
- Shared Platform events → `platform.*`

---

## Task 2: Update `modules/{name}/overview.md` for all 23 modules

**Why:** Every module overview currently has a single "Domain Events" section that lists cross-module events incorrectly as domain events. This must be split into two sections: intra-module domain events (MediatR) and cross-module integration events (RabbitMQ).

**Pattern to apply to each module's `overview.md`:**

Find the existing `## Domain Events` section and replace it with:

```markdown
## Domain Events (intra-module — MediatR)

> These events are published and consumed within this module only. They never leave the module.

| Event | Published When | Handler |
|:------|:---------------|:--------|
| (list only events that stay inside this module, e.g. balance recalculation triggers) |

## Integration Events (cross-module — RabbitMQ)

### Publishes

| Event | Routing Key | Published When | Consumers |
|:------|:-----------|:---------------|:----------|
| (list events this module sends to other modules) |

### Consumes

| Event | Routing Key | Source Module | Action Taken |
|:------|:-----------|:-------------|:-------------|
| (list events this module receives from other modules) |
```

**Per-module publish/consume mapping** (derived from `backend/messaging/event-catalog.md` and `exchange-topology.md`):

### activity-monitoring
- Publishes: `ExceptionDetected` (`activity.exception`), `DiscrepancyDetected` (`activity.discrepancy`), `ActivitySnapshotReceived` (`activity.snapshot`), `DailySummaryAggregated` (`activity.summary`)
- Consumes: `PresenceSessionStarted` (from WorkforcePresence)

### agent-gateway
- Publishes: `AgentRegistered` (`agent.gateway.registered`), `AgentHeartbeatLost` (`agent.gateway.heartbeat_lost`), `AgentRevoked` (`agent.gateway.revoked`)
- Consumes: `EmployeeOffboarded` (from CoreHR)

### auth
- Publishes: `UserLoggedIn` (`auth.login`), `UserLoggedOut` (`auth.logout`), `RoleAssigned` (`auth.role`), `PermissionChanged` (`auth.permission`)
- Consumes: `UserStatusChanged` (from Infrastructure)

### calendar
- Publishes: _(none — reacts to events, does not publish integration events)_
- Consumes: `LeaveApproved` (from Leave), `ReviewCycleStarted` (from Performance), `EmployeeHired` (from CoreHR)

### configuration
- Publishes: _(none)_
- Consumes: `TenantCreated` (from Infrastructure)

### core-hr
- Publishes: `EmployeeHired` (`core-hr.employee.hired`), `EmployeePromoted` (`core-hr.employee.promoted`), `EmployeeTransferred` (`core-hr.employee.transferred`), `SalaryChanged` (`core-hr.employee.salary_changed`), `EmployeeOffboarded` (`core-hr.employee.offboarded`), `OnboardingStepCompleted` (`core-hr.employee.onboarding`)
- Consumes: _(publishes only)_

### discrepancy-engine
- Publishes: `DiscrepancyCriticalDetected` (`discrepancy.critical`)
- Consumes: `DailySummaryAggregated` (from ActivityMonitoring)

### documents
- Publishes: `DocumentPublished` (`documents.published`), `AcknowledgementReceived` (`documents.acknowledged`)
- Consumes: `EmployeeHired` (from CoreHR), `EmployeeOffboarded` (from CoreHR)

### exception-engine
- Publishes: `ExceptionAlertCreated` (`exception.alert`), `AlertEscalated` (`exception.escalated`), `AlertAcknowledged` (`exception.acknowledged`)
- Consumes: `ActivitySnapshotReceived` (from ActivityMonitoring), `BreakExceeded` (from WorkforcePresence), `AgentHeartbeatLost` (from AgentGateway)

### expense
- Publishes: `ExpenseClaimSubmitted` (`expense.submitted`), `ExpenseClaimApproved` (`expense.approved`), `ExpenseClaimPaid` (`expense.paid`)
- Consumes: _(none)_

### grievance
- Publishes: `GrievanceFiled` (`grievance.filed`), `DisciplinaryActionIssued` (`grievance.disciplinary`), `GrievanceResolved` (`grievance.resolved`)
- Consumes: _(none)_

### identity-verification
- Publishes: `VerificationCompleted` (`identity.verified`), `VerificationFailed` (`identity.failed`), `BiometricDeviceOffline` (`identity.device_offline`)
- Consumes: `ActivitySnapshotReceived` (from ActivityMonitoring)

### infrastructure
- Publishes: `TenantCreated` (`infrastructure.tenant.created`), `TenantActivated` (`infrastructure.tenant.activated`), `TenantDeactivated` (`infrastructure.tenant.deactivated`), `UserCreated` (`infrastructure.user.created`), `UserStatusChanged` (`infrastructure.user.status`)
- Consumes: _(publishes only)_

### leave
- Publishes: `LeaveRequested` (`leave.request.requested`), `LeaveApproved` (`leave.request.approved`), `LeaveRejected` (`leave.request.rejected`), `LeaveCancelled` (`leave.request.cancelled`), `EntitlementAdjusted` (`leave.entitlement.adjusted`)
- Consumes: `EmployeeHired` (from CoreHR — to calculate initial entitlements)

### notifications
- Publishes: _(none — subscriber only)_
- Consumes: All events that trigger notifications (see event catalog for full list — LeaveRequested, LeaveApproved, EmployeeHired, PayrollRunCompleted, ReviewCompleted, ExceptionAlertCreated, etc.)

### org-structure
- Publishes: `DepartmentChanged` (`org.department.changed`)
- Consumes: `TenantCreated` (from Infrastructure — to seed default department)

### payroll
- Publishes: `PayrollRunStarted` (`payroll.run.started`), `PayrollRunCompleted` (`payroll.run.completed`), `PayrollRunFailed` (`payroll.run.failed`)
- Consumes: `LeaveApproved` (from Leave), `SalaryChanged` (from CoreHR), `OvertimeApproved` (from WorkforcePresence), `ExpenseClaimApproved` (from Expense)

### performance
- Publishes: `ReviewCycleStarted` (`performance.review.started`), `ReviewCompleted` (`performance.review.completed`), `GoalCreated` (`performance.goal.created`), `RecognitionGiven` (`performance.recognition`)
- Consumes: `EmployeeHired` (from CoreHR)

### productivity-analytics
- Publishes: `DailyReportReady` (`analytics.daily`), `WeeklyReportReady` (`analytics.weekly`), `MonthlyReportReady` (`analytics.monthly`)
- Consumes: `ActivitySnapshotReceived` (from ActivityMonitoring), `ExceptionAlertCreated` (from ExceptionEngine)

### reporting-engine
- Publishes: _(none)_
- Consumes: _(none — reads directly via query service interfaces)_

### shared-platform
- Publishes: `WorkflowStepCompleted` (`platform.workflow.step`), `WorkflowCompleted` (`platform.workflow.completed`), `SubscriptionChanged` (`platform.subscription`), `FeatureFlagToggled` (`platform.flag`)
- Consumes: `UserLoggedIn` (from Auth), `TenantActivated` (from Infrastructure)

### skills
- Publishes: `SkillValidated` (`skills.validated`), `CourseCompleted` (`skills.course`), `CertificationEarned` (`skills.cert.earned`), `CertificationExpiring` (`skills.cert.expiring`)
- Consumes: `EmployeeHired` (from CoreHR), `ReviewCompleted` (from Performance)

### workforce-presence
- Publishes: `PresenceSessionStarted` (`workforce.presence.started`), `PresenceSessionEnded` (`workforce.presence.ended`), `BreakExceeded` (`workforce.presence.break`), `OvertimeRequested` (`workforce.presence.overtime_req`), `OvertimeApproved` (`workforce.presence.overtime_approved`), `AttendanceCorrected` (`workforce.presence.corrected`)
- Consumes: `EmployeeHired` (from CoreHR), `LeaveApproved` (from Leave — to mark presence as `on_leave`)

---

## Task 3: Add outbox tables to `database/schemas/{module}.md` for publishing modules

**Why:** The database schema files document each module's tables. Modules that publish integration events have an `{module}_outbox_events` table. Modules that consume have a `processed_integration_events` table. These are not documented anywhere in the `database/schemas/` files yet.

**Which modules get which tables:**

| Module | Needs `outbox_events` | Needs `processed_integration_events` |
|:-------|:---------------------|:-------------------------------------|
| activity-monitoring | ✅ | ✅ |
| agent-gateway | ✅ | ✅ |
| auth | ✅ | ✅ |
| calendar | ❌ | ✅ |
| configuration | ❌ | ✅ |
| core-hr | ✅ | ❌ |
| discrepancy-engine | ✅ | ✅ |
| documents | ✅ | ✅ |
| exception-engine | ✅ | ✅ |
| expense | ✅ | ❌ |
| grievance | ✅ | ❌ |
| identity-verification | ✅ | ✅ |
| infrastructure | ✅ | ❌ |
| leave | ✅ | ✅ |
| notifications | ❌ | ✅ |
| org-structure | ✅ | ✅ |
| payroll | ✅ | ✅ |
| performance | ✅ | ✅ |
| productivity-analytics | ✅ | ✅ |
| reporting-engine | ❌ | ❌ |
| shared-platform | ✅ | ✅ |
| skills | ✅ | ✅ |
| workforce-presence | ✅ | ✅ |

**Table definition to append to each applicable `database/schemas/{module}.md`:**

```markdown
## Messaging Tables (MassTransit Outbox + Idempotency)

> These tables are managed by MassTransit and must not be written to directly. They are part of each module's DbContext.

### `{module}_outbox_events` _(publisher modules only)_

Transactional outbox — written in the same DB transaction as the business write. A background processor reads and forwards to RabbitMQ.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `event_type` | `varchar(200)` | Fully-qualified event class name |
| `payload` | `jsonb` | Serialized IntegrationEvent |
| `created_at` | `timestamptz` | |
| `processed_at` | `timestamptz` | NULL = not yet delivered to RabbitMQ |
| `retry_count` | `integer` | Default 0; max 5 |
| `last_error` | `text` | Last failure message if any |

Index: `WHERE processed_at IS NULL` on `created_at` — the outbox processor queries this.

### `processed_integration_events` _(consumer modules only)_

Idempotency table — prevents double-processing if RabbitMQ redelivers a message.

| Column | Type | Notes |
|:-------|:-----|:------|
| `event_id` | `uuid` | PK — same as `IntegrationEvent.EventId` |
| `event_type` | `varchar(200)` | |
| `processed_at` | `timestamptz` | |
```

---

## Task 4: Create `backend/messaging/module-event-matrix.md`

**Why:** There is no single-glance reference showing all 23 modules and which events they publish/consume. This is a useful lookup table for developers.

**File to create:** `backend/messaging/module-event-matrix.md`

**Content:** A table with columns: Module | Publishes | Consumes — one row per module, derived from the per-module mapping in Task 2.

---

## Files Changed Summary

| File | Action |
|:-----|:-------|
| `backend/messaging/event-catalog.md` | Modify — fix preamble, add IntegrationEvent format, add routing key column |
| `backend/messaging/module-event-matrix.md` | **Create new** — 23-module publish/consume matrix |
| `modules/activity-monitoring/overview.md` | Modify — split Domain Events section |
| `modules/agent-gateway/overview.md` | Modify — split Domain Events section |
| `modules/auth/overview.md` | Modify — split Domain Events section |
| `modules/calendar/overview.md` | Modify — split Domain Events section |
| `modules/configuration/overview.md` | Modify — split Domain Events section |
| `modules/core-hr/overview.md` | Modify — split Domain Events section |
| `modules/discrepancy-engine/overview.md` | Modify — split Domain Events section |
| `modules/documents/overview.md` | Modify — split Domain Events section |
| `modules/exception-engine/overview.md` | Modify — split Domain Events section |
| `modules/expense/overview.md` | Modify — split Domain Events section |
| `modules/grievance/overview.md` | Modify — split Domain Events section |
| `modules/identity-verification/overview.md` | Modify — split Domain Events section |
| `modules/infrastructure/overview.md` | Modify — split Domain Events section |
| `modules/leave/overview.md` | Modify — split Domain Events section |
| `modules/notifications/overview.md` | Modify — split Domain Events section |
| `modules/org-structure/overview.md` | Modify — split Domain Events section |
| `modules/payroll/overview.md` | Modify — split Domain Events section |
| `modules/performance/overview.md` | Modify — split Domain Events section |
| `modules/productivity-analytics/overview.md` | Modify — split Domain Events section |
| `modules/reporting-engine/overview.md` | Modify — split Domain Events section |
| `modules/shared-platform/overview.md` | Modify — split Domain Events section |
| `modules/skills/overview.md` | Modify — split Domain Events section |
| `modules/workforce-presence/overview.md` | Modify — split Domain Events section |
| `database/schemas/activity-monitoring.md` | Modify — add outbox + idempotency tables |
| `database/schemas/agent-gateway.md` | Modify — add outbox + idempotency tables |
| `database/schemas/auth.md` | Modify — add outbox + idempotency tables |
| `database/schemas/calendar.md` | Modify — add idempotency table |
| `database/schemas/configuration.md` | Modify — add idempotency table |
| `database/schemas/core-hr.md` | Modify — add outbox table |
| `database/schemas/discrepancy-engine.md` | Modify — add outbox + idempotency tables |
| `database/schemas/documents.md` | Modify — add outbox + idempotency tables |
| `database/schemas/exception-engine.md` | Modify — add outbox + idempotency tables |
| `database/schemas/expense.md` | Modify — add outbox table |
| `database/schemas/grievance.md` | Modify — add outbox table |
| `database/schemas/identity-verification.md` | Modify — add outbox + idempotency tables |
| `database/schemas/infrastructure.md` | Modify — add outbox table |
| `database/schemas/leave.md` | Modify — add outbox + idempotency tables |
| `database/schemas/notifications.md` | Modify — add idempotency table |
| `database/schemas/org-structure.md` | Modify — add outbox + idempotency tables |
| `database/schemas/payroll.md` | Modify — add outbox + idempotency tables |
| `database/schemas/performance.md` | Modify — add outbox + idempotency tables |
| `database/schemas/productivity-analytics.md` | Modify — add outbox + idempotency tables |
| `database/schemas/shared-platform.md` | Modify — add outbox + idempotency tables |
| `database/schemas/skills.md` | Modify — add outbox + idempotency tables |
| `database/schemas/workforce-presence.md` | Modify — add outbox + idempotency tables |
