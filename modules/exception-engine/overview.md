# Module: Exception Engine

**Namespace:** `ONEVO.Modules.ExceptionEngine`
**Phase:** 1 — Build
**Pillar:** 2 — Workforce Intelligence
**Owner:** Dev 2 (Week 4)
**Tables:** 5
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
| **Depends on** | [[modules/core-hr/overview\|Core Hr]] | `IEmployeeService` | Employee/department context, manager hierarchy |
| **Depends on** | [[modules/configuration/overview\|Configuration]] | `IConfigurationService` | Monitoring toggles |
| **Consumed by** | [[modules/notifications/overview\|Notifications]] | — (via `ExceptionAlertCreated` event) | Send alerts |
| **Consumed by** | [[modules/productivity-analytics/overview\|Productivity Analytics]] | — (via direct query) | Exception counts for reports |
| **Publishes to** | [[modules/agent-gateway/overview\|Agent Gateway]] | `RemoteCaptureRequested` event | Triggers on-demand screenshot/photo capture via agent |

---

## Public Interface

```csharp
// ONEVO.Modules.ExceptionEngine/Public/IExceptionEngineService.cs
public interface IExceptionEngineService
{
    Task<Result<List<ExceptionAlertDto>>> GetActiveAlertsAsync(CancellationToken ct);
    Task<Result<List<ExceptionAlertDto>>> GetAlertsByEmployeeAsync(Guid employeeId, DateOnly from, DateOnly to, CancellationToken ct);
    Task<Result<int>> GetExceptionCountAsync(DateOnly date, CancellationToken ct);
    Task AcknowledgeAlertAsync(Guid alertId, Guid acknowledgedById, string comment, CancellationToken ct);
}
```

---

## Database Tables (5)

### `exception_rules`

Configurable anomaly detection rules.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `rule_name` | `varchar(100)` | Human-readable name |
| `rule_type` | `varchar(30)` | `low_activity`, `excess_idle`, `unusual_pattern`, `excess_meeting`, `no_presence`, `break_exceeded`, `verification_failed`, `non_allowed_app`, `presence_without_activity`, `heartbeat_gap` |
| `threshold_json` | `jsonb` | Rule-specific thresholds (see below) |
| `severity` | `varchar(20)` | `info`, `warning`, `critical` |
| `is_active` | `boolean` | |
| `applies_to` | `varchar(20)` | `all`, `department`, `team`, `employee` |
| `applies_to_id` | `uuid` | Nullable — department/team/employee ID |
| `created_by_id` | `uuid` | FK → users |
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

// non_allowed_app — triggers when employee uses app not on their allowlist
{"max_minutes_per_day": 15, "max_consecutive_minutes": 5, "alert_severity": "medium"}

// presence_without_activity — biometric says present but no laptop activity
{"gap_minutes_threshold": 30, "source": "biometric_vs_activity"}

// heartbeat_gap — agent stopped sending heartbeats (possible tamper or crash)
{"gap_minutes_threshold": 10, "exclude_known_offline": true}
```

**Always validate threshold JSON against a known schema before evaluating.**

### `exception_alerts`

Generated alerts when rules are triggered.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `rule_id` | `uuid` | FK → exception_rules |
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
| `tenant_id` | `uuid` | FK → tenants |
| `severity` | `varchar(20)` | Which severity triggers this chain |
| `step_order` | `int` | 1, 2, 3… |
| `notify_role` | `varchar(30)` | `reporting_manager`, `department_head`, `hr`, `ceo`, `custom` |
| `notify_user_id` | `uuid` | Nullable — for `custom` role |
| `delay_minutes` | `int` | Wait N minutes before escalating to next step |
| `created_at` | `timestamptz` | |

**Example chain for `critical` severity:**
1. `reporting_manager` — delay 0 min (immediate)
2. `hr` — delay 30 min (if not acknowledged)
3. `ceo` — delay 60 min (if still not acknowledged)

### `alert_acknowledgements`

Audit trail for alert actions.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `alert_id` | `uuid` | FK → exception_alerts |
| `acknowledged_by_id` | `uuid` | FK → users |
| `action` | `varchar(20)` | `acknowledged`, `dismissed`, `escalated`, `noted` |
| `comment` | `text` | Optional note |
| `acted_at` | `timestamptz` | |

### `exception_schedules`

When the engine runs checks.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants, UNIQUE |
| `check_interval_minutes` | `int` | Default 5 |
| `active_from_time` | `time` | e.g., 08:00 |
| `active_to_time` | `time` | e.g., 18:00 |
| `active_days_json` | `jsonb` | e.g., `[1,2,3,4,5]` (Mon–Fri) |
| `timezone` | `varchar(50)` | e.g., "Asia/Colombo" |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `ExceptionAlertCreated` | Rule threshold breached | [[modules/notifications/overview\|Notifications]] (send alert via escalation chain) |
| `AlertEscalated` | Unacknowledged alert escalated to next level | [[modules/notifications/overview\|Notifications]] (notify next in chain) |
| `AlertAcknowledged` | Manager acknowledges/dismisses alert | Audit trail |
| `RemoteCaptureRequested` | Manager clicks "Request Screenshot/Photo" on alert | [[modules/agent-gateway/overview\|Agent Gateway]] (dispatches capture command to agent) |

---

## Key Business Rules

1. **Engine only evaluates during configured work hours** (`exception_schedules`). Off-hours activity data is still collected by [[modules/activity-monitoring/overview|Activity Monitoring]] but does NOT trigger alerts.
2. **One alert per rule per employee per evaluation window.** Don't generate duplicate alerts for the same ongoing condition — check if an active (non-acknowledged) alert already exists.
3. **Escalation is time-based.** If alert is not acknowledged within `delay_minutes`, auto-escalate to next step in the chain. Implemented via Hangfire delayed jobs.
4. **Data snapshot is evidence.** When an alert fires, capture the relevant data (activity snapshots, presence data) into `data_snapshot_json` so the alert is self-contained for review.
5. **Threshold JSON must be validated** against the known schema for each `rule_type` before evaluation. Invalid JSON = skip rule + log warning.

---

## Evaluation Flow

```
ExceptionEngineEvaluationJob (Hangfire, every 5 min during work hours)
  │
  ├─ Check exception_schedules — is it within active hours?
  │   └─ No → skip evaluation
  │
  ├─ Load all active exception_rules for tenant
  │
  ├─ For each rule:
  │   ├─ Determine target employees (all / department / team / specific)
  │   ├─ For each employee:
  │   │   ├─ Check monitoring_feature_toggles + employee_monitoring_overrides
  │   │   │   └─ Monitoring disabled → skip
  │   │   ├─ Fetch relevant data from Activity Monitoring / Workforce Presence
  │   │   ├─ Evaluate threshold_json against data
  │   │   ├─ If breached:
  │   │   │   ├─ Check for existing active alert (dedup)
  │   │   │   ├─ Create exception_alert with data_snapshot_json
  │   │   │   └─ Publish ExceptionAlertCreated event
  │   │   └─ If not breached → continue
  │
  └─ Done

EscalationJob (Hangfire, every 5 min)
  ├─ Find alerts where status = 'new' AND triggered_at + delay_minutes < now
  ├─ Escalate to next step in escalation_chains
  └─ Publish AlertEscalated event
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

### `non_allowed_app` — App Allowlist Violation

```
Evaluation:
  → Fetch resolved app allowlist for employee via IConfigurationService.GetResolvedAppAllowlistAsync()
  → Query application_usage for today where app NOT in allowlist
  → Sum non-allowed minutes
  → If exceeds max_minutes_per_day OR any single app exceeds max_consecutive_minutes → fire alert
  → Evidence: { app_name, total_minutes, category, allowlist_mode }
```

### `presence_without_activity` — Biometric ↔ Activity Cross-Validation

```
Evaluation:
  → Fetch attendance_records (biometric clock-in/out) for employee today
  → Fetch activity_daily_summary (agent data) for employee today  
  → Compare: if biometric says "present since 09:00" but first activity_snapshot is at 09:45
    → gap = 45 minutes > gap_minutes_threshold (30) → fire alert
  → Also detects: "clocked out at 17:00 but no activity since 15:30"
  → Evidence: { biometric_in, first_activity, gap_minutes, biometric_out, last_activity }
```

### `heartbeat_gap` — Agent Tamper / Crash Detection

```
Evaluation:
  → Fetch agent_health_logs for employee's registered agent
  → Check last_heartbeat_at against now
  → If gap > gap_minutes_threshold AND agent status = 'active' → fire alert
  → Exclude agents with status 'inactive' or 'revoked' (known offline)
  → Evidence: { agent_id, last_heartbeat, gap_minutes, tamper_detected }
```

### Remote Capture Action Flow

```
Manager views alert detail → clicks "Request Screenshot" or "Request Photo"
  → POST /api/v1/exceptions/alerts/{id}/request-screenshot
  → ExceptionEngineService.RequestRemoteCaptureAsync(alertId, captureType, requestedByUserId)
    → Validate: alert exists, employee has active agent, rate limit not exceeded
    → Publish RemoteCaptureRequested event
    → agent-gateway handles event → sends command to agent via SignalR
    → Agent shows notification to employee → captures → uploads
    → AgentCommandCompleted event fires → result attached to alert
  → Manager sees capture result in alert detail view
```

**Rate limit:** Max 10 capture requests per agent per hour. Prevents harassment.

---

## Important Notes

- **This module does NOT collect data.** It only evaluates data collected by [[modules/activity-monitoring/overview|Activity Monitoring]] and [[modules/workforce-presence/overview|Workforce Presence]].
- **Off-hours activity does NOT trigger alerts.** Always check `exception_schedules` first.
- **Escalation chains are per-severity, not per-rule.** All `critical` alerts follow the same escalation chain.
- **Remote capture requires `agent:command` permission.** Only reporting managers and above can trigger captures.
- **Capture results are attached to the originating alert** via `data_snapshot_json` update.

## Features

- [[modules/exception-engine/exception-rules/overview|Exception Rules]] — Configurable anomaly detection rules with threshold JSON
- [[modules/exception-engine/evaluation-engine/overview|Evaluation Engine]] — Hangfire-driven rule evaluation against activity and presence data
- [[modules/exception-engine/alert-generation/overview|Alert Generation]] — Alert creation, deduplication, evidence snapshots — frontend: [[modules/exception-engine/alert-generation/frontend|Frontend]]
- [[modules/exception-engine/escalation-chains/overview|Escalation Chains]] — Time-based escalation routing by severity
- Remote Capture Actions — Manager-triggered screenshot/photo capture from alert detail view
- Biometric Cross Validation — Presence-without-activity detection (biometric ↔ agent data)
- App Violation Rules — Non-allowed app usage detection (integrated with [[modules/configuration/app-allowlist/overview|App Allowlist]])

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] — All rules, alerts, and schedules are tenant-scoped
- [[backend/messaging/event-catalog|Event Catalog]] — `ExceptionAlertCreated`, `AlertEscalated`, `AlertAcknowledged`
- [[backend/messaging/error-handling|Error Handling]] — Invalid threshold JSON skips rule with warning log
- [[security/compliance|Compliance]] — Alert acknowledgement audit trail
- [[current-focus/DEV2-exception-engine|DEV2: Exception Engine]] — Implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/activity-monitoring/overview|Activity Monitoring]], [[modules/workforce-presence/overview|Workforce Presence]], [[modules/notifications/overview|Notifications]]

---

## Phase 2 Features (Do NOT Build)

> [!WARNING]
> The following features are deferred to Phase 2. Do not implement them. Specs are preserved here for future reference.

### AI-Powered Anomaly Detection
Phase 1 uses configurable threshold-based rules (e.g., "idle > 30 min = alert"). Phase 2 will add ML-based anomaly detection that learns per-employee baselines and flags statistical outliers. For example: "Employee X is typically 85% active but today is 40%" would trigger even if the absolute threshold isn't breached. Requires training data collection during Phase 1 operation.

### Predictive Alerts
Phase 2 may add predictive alerting: detecting downward trends before thresholds are breached (e.g., "Employee Y's activity has been declining 5% each day for the past week"). This requires time-series analysis on `activity_daily_summary` data.

### Auto-Remediation Actions
Phase 1 alerts require manual manager action. Phase 2 may add configurable auto-remediation: e.g., auto-send a "check-in" notification to the employee when idle exceeds a threshold, or auto-schedule a 1-on-1 when exception count exceeds N in a week.
