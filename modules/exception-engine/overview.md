# Module: Exception Engine

**Feature Folder:** `Application/Features/ExceptionEngine`
**Phase:** 1 â€” Build
**Pillar:** 2 â€” Workforce Intelligence
**Owner:** Dev 2 (Week 4)
**Tables:** 6
**Task File:** [[current-focus/DEV2-exception-engine|DEV2: Exception Engine]]

---

## Purpose

Configurable anomaly detection engine that evaluates rules against activity and presence data, generates alerts when thresholds are breached, and routes notifications through escalation chains. Runs on a schedule during configured work hours only.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/activity-monitoring/overview\|Activity Monitoring]] | `IActivityMonitoringService` | Latest activity data for rule evaluation |
| **Depends on** | [[modules/workforce-presence/overview\|Workforce Presence]] | `IWorkforcePresenceService` | Presence/idle data for detection |
| **Depends on** | [[modules/core-hr/overview\|Core Hr]] | `IEmployeeService` | Employee/department context, position-derived reporting hierarchy |
| **Depends on** | [[modules/configuration/overview\|Configuration]] | `IConfigurationService` | Monitoring toggles |
| **Consumed by** | [[modules/notifications/overview\|Notifications]] | â€” (via `ExceptionAlertCreated` event) | Route alert action cards through Chat or Inbox |
| **Consumed by** | [[modules/productivity-analytics/overview\|Productivity Analytics]] | â€” (via direct query) | Exception counts for reports |
| **Publishes to** | [[modules/agent-gateway/overview\|Agent Gateway]] | `RemoteCaptureRequested` event | Triggers on-demand screenshot/photo capture via agent |

---

## Public Interface

```csharp
// ONEVO.Application.Features.ExceptionEngine/Public/IExceptionEngineService.cs
public interface IExceptionEngineService
{
    Task<Result<List<ExceptionAlertDto>>> GetActiveAlertsAsync(CancellationToken ct);
    Task<Result<List<ExceptionAlertDto>>> GetAlertsByEmployeeAsync(Guid employeeId, DateOnly from, DateOnly to, CancellationToken ct);
    Task<Result<int>> GetExceptionCountAsync(DateOnly date, CancellationToken ct);
    Task AcknowledgeAlertAsync(Guid alertId, Guid acknowledgedById, string comment, CancellationToken ct);
}
```

---

## Code Location (Clean Architecture)

Domain entities:
  ONEVO.Domain/Features/ExceptionEngine/Entities/
  ONEVO.Domain/Features/ExceptionEngine/Events/

Application (CQRS):
  ONEVO.Application/Features/ExceptionEngine/Commands/
  ONEVO.Application/Features/ExceptionEngine/Queries/
  ONEVO.Application/Features/ExceptionEngine/DTOs/Requests/
  ONEVO.Application/Features/ExceptionEngine/DTOs/Responses/
  ONEVO.Application/Features/ExceptionEngine/Validators/
  ONEVO.Application/Features/ExceptionEngine/EventHandlers/

Infrastructure:
  ONEVO.Infrastructure/Persistence/Configurations/ExceptionEngine/

API endpoints:
  ONEVO.Api/Controllers/ExceptionEngine/ExceptionEngineController.cs

---

## Database Tables (5)

### `exception_rules`

Configurable anomaly detection rules.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `rule_name` | `varchar(100)` | Human-readable name |
| `rule_type` | `varchar(30)` | `low_activity`, `excess_idle`, `unusual_pattern`, `excess_meeting`, `no_presence`, `break_exceeded`, `verification_failed`, `non_allowed_app`, `presence_without_activity`, `heartbeat_gap` |
| `threshold_json` | `jsonb` | Rule-specific thresholds (see below) |
| `severity` | `varchar(20)` | `info`, `warning`, `critical` |
| `is_active` | `boolean` | |
| `applies_to` | `varchar(20)` | `all`, `department`, `team`, `employee` |
| `applies_to_id` | `uuid` | Nullable â€” department/team/employee ID |
| `created_by_id` | `uuid` | FK â†’ users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Threshold JSON examples:**

```json
// low_activity
{"idle_percent_max": 40, "window_minutes": 60, "consecutive_snapshots": 3}

// excess_idle
{"idle_minutes_threshold": 30, "exclude_breaks": true}

// excess_meeting
{"meeting_percent_max": 70, "window_hours": 8}

// no_presence
{"minutes_after_shift_start": 30}

// break_exceeded
{"max_break_minutes": 60, "break_type": "any"}

// non_allowed_app â€” triggers when employee uses app not on their allowlist
{"max_minutes_per_day": 15, "max_consecutive_minutes": 5, "alert_severity": "medium"}

// presence_without_activity â€” biometric says present but no laptop activity
{"gap_minutes_threshold": 30, "source": "biometric_vs_activity"}

// heartbeat_gap â€” agent stopped sending heartbeats (possible tamper or crash)
{"gap_minutes_threshold": 10, "exclude_known_offline": true}
```

**Always validate threshold JSON against a known schema before evaluating.**

### `exception_alerts`

Generated alerts when rules are triggered.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `employee_id` | `uuid` | FK â†’ employees |
| `rule_id` | `uuid` | FK â†’ exception_rules |
| `triggered_at` | `timestamptz` | When the rule fired |
| `severity` | `varchar(20)` | Copied from rule at trigger time |
| `summary` | `varchar(500)` | Human-readable description |
| `data_snapshot_json` | `jsonb` | Evidence data at trigger time |
| `status` | `varchar(20)` | `new`, `acknowledged`, `dismissed`, `escalated` |
| `created_at` | `timestamptz` | |

**Indexes:** `(tenant_id, status)`, `(tenant_id, employee_id, triggered_at)`, `(tenant_id, severity)`

### `escalation_chains`

Notification routing by severity.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `severity` | `varchar(20)` | Which severity triggers this chain |
| `step_order` | `int` | 1, 2, 3â€¦ |
| `resolver_type` | `varchar(50)` | `reporting_chain_first_eligible`, `reporting_manager`, `team_lead`, `department_owner`, `permission`, `legal_entity`, `department`, `team`, `position`, `position_branch`, `specific_employee`, `configured_escalation_resolver`, `previous_approver`, `case_participants` |
| `resolver_config` | `jsonb` | Resolver-specific configuration such as permission key, legal entity/department/team/position/position branch id, optional job level id, or selected employee id |
| `delay_minutes` | `int` | Wait N minutes before escalating to next step |
| `created_at` | `timestamptz` | |

**Example chain for `critical` severity:**
1. Employee's reporting manager â€” delay 0 min (immediate)
2. Users with permission `exceptions:manage` â€” delay 30 min (if not acknowledged)
3. Configured escalation resolver â€” delay 60 min (if still not acknowledged)

> Database note: resolver-based routing is the canonical Phase 1 shape. Do not reintroduce fixed HR/CEO role columns for exception escalation.

### `alert_acknowledgements`

Audit trail for alert actions.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `alert_id` | `uuid` | FK â†’ exception_alerts |
| `acknowledged_by_id` | `uuid` | FK â†’ users |
| `action` | `varchar(20)` | `acknowledged`, `dismissed`, `escalated`, `noted` |
| `comment` | `text` | Optional note |
| `acted_at` | `timestamptz` | |

### `exception_schedules`

When the engine runs checks.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants, UNIQUE |
| `check_interval_minutes` | `int` | Default 5 |
| `active_from_time` | `time` | e.g., 08:00 |
| `active_to_time` | `time` | e.g., 18:00 |
| `active_days_json` | `jsonb` | e.g., `[1,2,3,4,5]` (Monâ€“Fri) |
| `timezone` | `varchar(50)` | e.g., "Asia/Colombo" |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

---

## Domain Events (intra-module â€” MediatR)

> These events are published and consumed within this module only. They never leave the module.

| Event | Published When | Handler |
|:------|:---------------|:--------|
| _(none)_ | â€” | â€” |

## Cross-Module Events (cross-module â€” MediatR INotification)

### Publishes

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `ExceptionAlertCreated` | Rule threshold breached | [[modules/notifications/overview\|Notifications]] (send alert via escalation chain), [[modules/productivity-analytics/overview\|Productivity Analytics]] |
| `AlertEscalated` | Unacknowledged alert escalated to next level | [[modules/notifications/overview\|Notifications]] (notify next in chain) |
| `AlertAcknowledged` | Manager acknowledges/dismisses alert | Audit trail |

### Consumes

| Event | Source Module | Action Taken |
|:------|:-------------|:-------------|
| `ActivitySnapshotReceived` | [[modules/activity-monitoring/overview\|Activity Monitoring]] | Evaluate active exception rules against latest snapshot |
| `BreakExceeded` | [[modules/workforce-presence/overview\|Workforce Presence]] | Fire break-exceeded alert if over allowed duration |
| `AgentHeartbeatLost` | [[modules/agent-gateway/overview\|Agent Gateway]] | Fire heartbeat-gap alert for the affected employee |

---

## Key Business Rules

1. **Engine only evaluates during configured work hours** (`exception_schedules`). Off-hours activity data is still collected by [[modules/activity-monitoring/overview|Activity Monitoring]] but does NOT trigger alerts.
2. **One alert per rule per employee per evaluation window.** Don't generate duplicate alerts for the same ongoing condition â€” check if an active (non-acknowledged) alert already exists.
3. **Escalation is time-based and resolver-based.** If alert is not acknowledged within `delay_minutes`, auto-escalate to the next resolver in the chain. Implemented via Hangfire delayed jobs.
4. **Data snapshot is evidence.** When an alert fires, capture the relevant data (activity snapshots, presence data) into `data_snapshot_json` so the alert is self-contained for review.
5. **Threshold JSON must be validated** against the known schema for each `rule_type` before evaluation. Invalid JSON = skip rule + log warning.

---

## Evaluation Flow

```
ExceptionEngineEvaluationJob (Hangfire, every 5 min during work hours)
  â”‚
  â”œâ”€ Check exception_schedules â€” is it within active hours?
  â”‚   â””â”€ No â†’ skip evaluation
  â”‚
  â”œâ”€ Load all active exception_rules for tenant
  â”‚
  â”œâ”€ For each rule:
  â”‚   â”œâ”€ Determine target employees (all / department / team / specific)
  â”‚   â”œâ”€ For each employee:
  â”‚   â”‚   â”œâ”€ Check monitoring_feature_toggles + employee_monitoring_overrides
  â”‚   â”‚   â”‚   â””â”€ Monitoring disabled â†’ skip
  â”‚   â”‚   â”œâ”€ Fetch relevant data from Activity Monitoring / Workforce Presence
  â”‚   â”‚   â”œâ”€ Evaluate threshold_json against data
  â”‚   â”‚   â”œâ”€ If breached:
  â”‚   â”‚   â”‚   â”œâ”€ Check for existing active alert (dedup)
  â”‚   â”‚   â”‚   â”œâ”€ Create exception_alert with data_snapshot_json
  â”‚   â”‚   â”‚   â””â”€ Publish ExceptionAlertCreated event
  â”‚   â”‚   â””â”€ If not breached â†’ continue
  â”‚
  â””â”€ Done

EscalationJob (Hangfire, every 5 min)
  â”œâ”€ Find alerts where status = 'new' AND triggered_at + delay_minutes < now
  â”œâ”€ Escalate to next step in escalation_chains
  â””â”€ Publish AlertEscalated event
```

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/exceptions/alerts` | `exceptions:view` | List active alerts (filterable) |
| GET | `/api/v1/exceptions/alerts/{id}` | `exceptions:view` | Alert detail with evidence data |
| PUT | `/api/v1/exceptions/alerts/{id}/acknowledge` | `exceptions:acknowledge` | Acknowledge alert |
| PUT | `/api/v1/exceptions/alerts/{id}/dismiss` | `exceptions:acknowledge` | Dismiss alert |
| POST | `/api/v1/exceptions/alerts/{id}/request-screenshot` | `agent:command` | Request remote screenshot from employee's agent |
| POST | `/api/v1/exceptions/alerts/{id}/request-photo` | `agent:command` | Request remote photo verification from employee's agent |
| GET | `/api/v1/exceptions/rules` | `exceptions:manage` | List exception rules |
| POST | `/api/v1/exceptions/rules` | `exceptions:manage` | Create rule |
| PUT | `/api/v1/exceptions/rules/{id}` | `exceptions:manage` | Update rule |
| DELETE | `/api/v1/exceptions/rules/{id}` | `exceptions:manage` | Deactivate rule |
| GET | `/api/v1/exceptions/escalation-chains` | `exceptions:manage` | List escalation chains |
| POST | `/api/v1/exceptions/escalation-chains` | `exceptions:manage` | Create/update chain |
| GET | `/api/v1/exceptions/schedule` | `exceptions:manage` | Get evaluation schedule |
| PUT | `/api/v1/exceptions/schedule` | `exceptions:manage` | Update schedule |

---

## Hangfire Jobs

| Job | Schedule | Queue | Purpose |
|:----|:---------|:------|:--------|
| `ComputeActivityBaselinesJob` | Daily 9:45 PM | Default | Compute rolling 30-day avg+stddev per employee per metric |
| `ExceptionEngineEvaluationJob` | Every 5 min | High | Evaluate all active rules against latest data |
| `EscalationJob` | Every 5 min | High | Escalate unacknowledged alerts |

---

## SignalR Integration

New exception alerts are pushed to the frontend via SignalR channel `exception-alerts`:

```json
{
  "alertId": "uuid",
  "employeeId": "uuid",
  "employeeName": "John Doe",
  "severity": "critical",
  "summary": "Low activity detected: 15% active in last 60 minutes",
  "triggeredAt": "2026-04-05T10:30:00Z"
}
```

---

## New Rule Type Details

### `non_allowed_app` â€” App Allowlist Violation

```
Evaluation:
  â†’ Fetch resolved app allowlist for employee via IConfigurationService.GetResolvedAppAllowlistAsync()
  â†’ Query application_usage for today where app NOT in allowlist
  â†’ Sum non-allowed minutes
  â†’ If exceeds max_minutes_per_day OR any single app exceeds max_consecutive_minutes â†’ fire alert
  â†’ Evidence: { app_name, total_minutes, category, allowlist_mode }
```

### `presence_without_activity` â€” Biometric â†” Activity Cross-Validation

```
Evaluation:
  â†’ Fetch attendance_records (biometric clock-in/out) for employee today
  â†’ Fetch activity_daily_summary (agent data) for employee today  
  â†’ Compare: if biometric says "present since 09:00" but first activity_snapshot is at 09:45
    â†’ gap = 45 minutes > gap_minutes_threshold (30) â†’ fire alert
  â†’ Also detects: "clocked out at 17:00 but no activity since 15:30"
  â†’ Evidence: { biometric_in, first_activity, gap_minutes, biometric_out, last_activity }
```

### `heartbeat_gap` â€” Agent Tamper / Crash Detection

```
Evaluation:
  â†’ Fetch agent_health_logs for employee's registered agent
  â†’ Check last_heartbeat_at against now
  â†’ If gap > gap_minutes_threshold AND agent status = 'active' â†’ fire alert
  â†’ Exclude agents with status 'inactive' or 'revoked' (known offline)
  â†’ Evidence: { agent_id, last_heartbeat, gap_minutes, tamper_detected }
```

### Remote Capture Action Flow

```
Manager views alert detail â†’ clicks "Request Screenshot" or "Request Photo"
  â†’ POST /api/v1/exceptions/alerts/{id}/request-screenshot
  â†’ ExceptionEngineService.RequestRemoteCaptureAsync(alertId, captureType, requestedByUserId)
    â†’ Validate: alert exists, employee has active agent, rate limit not exceeded
    â†’ Publish RemoteCaptureRequested event
    â†’ agent-gateway handles event â†’ sends command to agent via SignalR
    â†’ Agent shows notification to employee â†’ captures â†’ uploads
    â†’ AgentCommandCompleted event fires â†’ result attached to alert
  â†’ Manager sees capture result in alert detail view
```

**Rate limit:** Max 10 capture requests per agent per hour. Prevents harassment.

---

## Important Notes

- **This module does NOT collect data.** It only evaluates data collected by [[modules/activity-monitoring/overview|Activity Monitoring]] and [[modules/workforce-presence/overview|Workforce Presence]].
- **Off-hours activity does NOT trigger alerts.** Always check `exception_schedules` first.
- **Escalation chains are per-severity, not per-rule.** All `critical` alerts follow the same escalation chain unless an Automation Center rule overrides routing.
- **Remote capture requires `agent:command` permission.** Eligibility is permission-based and can also be constrained by workflow assignment.
- **Capture results are attached to the originating alert** via `data_snapshot_json` update.

## Features

- [[modules/exception-engine/exception-rules/overview|Exception Rules]] â€” Configurable anomaly detection rules with threshold JSON
- [[modules/exception-engine/evaluation-engine/overview|Evaluation Engine]] â€” Hangfire-driven rule evaluation against activity and presence data
- [[modules/exception-engine/alert-generation/overview|Alert Generation]] â€” Alert creation, deduplication, evidence snapshots â€” frontend: [[modules/exception-engine/alert-generation/frontend|Frontend]]
- [[modules/exception-engine/escalation-chains/overview|Escalation Chains]] â€” Time-based escalation routing by severity
- [[modules/exception-engine/activity-baselines/overview|Activity Baselines]] â€” Per-employee rolling baseline computation enabling sigma-relative rule thresholds
- Remote Capture Actions â€” Manager-triggered screenshot/photo capture from alert detail view
- Biometric Cross Validation â€” Presence-without-activity detection (biometric â†” agent data)
- App Violation Rules â€” Non-allowed app usage detection (integrated with [[modules/configuration/app-allowlist/overview|App Allowlist]])

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] â€” All rules, alerts, and schedules are tenant-scoped
- [[backend/messaging/event-catalog|Event Catalog]] â€” `ExceptionAlertCreated`, `AlertEscalated`, `AlertAcknowledged`
- [[backend/messaging/error-handling|Error Handling]] â€” Invalid threshold JSON skips rule with warning log
- [[security/compliance|Compliance]] â€” Alert acknowledgement audit trail
- [[current-focus/DEV2-exception-engine|DEV2: Exception Engine]] â€” Implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/activity-monitoring/overview|Activity Monitoring]], [[modules/workforce-presence/overview|Workforce Presence]], [[modules/notifications/overview|Notifications]]

---

## Phase 2 Features (Do NOT Build)

> [!WARNING]
> The following features are deferred to Phase 2. Do not implement them. Specs are preserved here for future reference.

### AI-Powered Anomaly Detection
Statistical baselines (rolling avg + stddev per employee per metric) are now shipped in Phase 1 via `ComputeActivityBaselinesJob` and `baseline_relative` rule conditions. See [[modules/exception-engine/activity-baselines/overview|Activity Baselines]]. Phase 2 may add ML-based anomaly detection that goes beyond fixed sigma multipliers to learn non-linear patterns.

### Predictive Alerts
Phase 2 may add predictive alerting: detecting downward trends before thresholds are breached (e.g., "Employee Y's activity has been declining 5% each day for the past week"). This requires time-series analysis on `activity_daily_summary` data.

### Auto-Remediation Actions
Phase 1 alerts require manual action by configured alert reviewers. Phase 2 may add configurable auto-remediation: e.g., auto-send a "check-in" notification to the employee when idle exceeds a threshold, or auto-schedule a follow-up when exception count exceeds N in a week.
