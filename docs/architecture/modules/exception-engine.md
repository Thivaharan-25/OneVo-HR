# Module: Exception Engine

**Namespace:** `ONEVO.Modules.ExceptionEngine`
**Pillar:** 2 — Workforce Intelligence
**Owner:** Dev 2 (Week 4)
**Tables:** 5
**Task File:** [[WEEK4-exception-engine]]

---

## Purpose

Configurable anomaly detection engine that evaluates rules against activity and presence data, generates alerts when thresholds are breached, and routes notifications through escalation chains. Runs on a schedule during configured work hours only.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[activity-monitoring]] | `IActivityMonitoringService` | Latest activity data for rule evaluation |
| **Depends on** | [[workforce-presence]] | `IWorkforcePresenceService` | Presence/idle data for detection |
| **Depends on** | [[core-hr]] | `IEmployeeService` | Employee/department context, manager hierarchy |
| **Depends on** | [[configuration]] | `IConfigurationService` | Monitoring toggles |
| **Consumed by** | [[notifications]] | — (via `ExceptionAlertCreated` event) | Send alerts |
| **Consumed by** | [[productivity-analytics]] | — (via direct query) | Exception counts for reports |

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
| `rule_type` | `varchar(30)` | `low_activity`, `excess_idle`, `unusual_pattern`, `excess_meeting`, `no_presence`, `break_exceeded`, `verification_failed` |
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
| `ExceptionAlertCreated` | Rule threshold breached | [[notifications]] (send alert via escalation chain) |
| `AlertEscalated` | Unacknowledged alert escalated to next level | [[notifications]] (notify next in chain) |
| `AlertAcknowledged` | Manager acknowledges/dismisses alert | Audit trail |

---

## Key Business Rules

1. **Engine only evaluates during configured work hours** (`exception_schedules`). Off-hours activity data is still collected by [[activity-monitoring]] but does NOT trigger alerts.
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

## Important Notes

- **This module does NOT collect data.** It only evaluates data collected by [[activity-monitoring]] and [[workforce-presence]].
- **Off-hours activity does NOT trigger alerts.** Always check `exception_schedules` first.
- **Escalation chains are per-severity, not per-rule.** All `critical` alerts follow the same escalation chain.

See also: [[module-catalog]], [[activity-monitoring]], [[workforce-presence]], [[notifications]]
