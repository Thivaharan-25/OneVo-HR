# Exception Engine — End-to-End Logic

**Module key:** `exceptions`  
**Pillar:** Monitoring
**Phase:** 2 - full Exception Engine deferred  
**Pricing unit:** Per employee  
**Entitlement guard:** All endpoints call `IsModuleEnabledAsync(tenantId, "exceptions")` ? 403 `module_not_entitled` if not entitled  
**Dependency:** See [[developer-platform/module-dependency-matrix|Module Dependency Matrix]]

---

## What This Module Does

The Exception Engine is a Phase 2 rule-based alerting layer that runs on top of activity monitoring data. Tenant admins define exception rules (thresholds, conditions, target groups, severity levels). A Hangfire background job evaluates each active rule against `activity_daily_summary` rows and creates `exception_alerts` when a threshold is breached. Alerts are reviewed, acknowledged, and optionally escalated via the Workflow Engine.

Phase 1 Developer Platform may expose module catalog, provisioning warnings, and platform dashboard visibility for lightweight monitoring alerts, but it must not require full Exception Engine rules or Workflow Engine escalation.

> **Critical:** The Exception Engine reads data produced by the `monitoring` module. Without `monitoring`, rules can be created and the engine runs, but it finds no activity data — zero alerts are ever generated. This is documented behavior, not an error. See the [Without Monitoring section](#behavior-without-monitoring-module).

---

## Rule Lifecycle

### Creating a Rule

1. Admin navigates to **Exceptions ? Rules ? + New Rule**
2. Fills in the rule definition form:

| Field | Type | Description |
|:---|:---|:---|
| Rule name | Text | Internal label |
| Condition | Dropdown | `idle_percent_exceeds`, `active_time_below`, `app_usage_exceeds`, `bulk_download_detected`, `out_of_hours_activity` |
| Threshold value | Number | Condition-specific: percentage for idle/active, MB for bulk download, hours for out-of-hours |
| Evaluation window | Dropdown | `daily`, `rolling_4h`, `rolling_1h` |
| Target group | Multi-select | All employees, specific departments, specific employees |
| Severity | Dropdown | `info`, `warning`, `critical` |
| Notify on trigger | User multi-select | Users to notify via notification module on alert creation |
| Escalation after (hours) | Number | Hours before unacknowledged alert escalates via workflow engine (0 = no escalation) |
| Enabled | Toggle | Default: On |

3. `POST /tenant/v1/exceptions/rules` ? creates `exception_rules` row
4. Rule becomes active at the next evaluation job run

### Enabling / Disabling a Rule

- `PATCH /tenant/v1/exceptions/rules/{id}` with `{ "is_enabled": false }`
- Disabled rules are skipped by the evaluation job
- Existing open alerts from a disabled rule remain open until acknowledged

### Deleting a Rule

- `DELETE /tenant/v1/exceptions/rules/{id}`
- Existing alerts linked to the deleted rule are preserved (rule_id becomes orphaned FK — alerts still accessible but rule name shown as "Deleted rule")
- Requires `exceptions.rules.manage` permission

---

## Evaluation Engine

### Background Job

A Hangfire recurring job `ExceptionRuleEvaluationJob` runs every **15 minutes**.

For each tenant with `exceptions` entitled:
1. Load all `exception_rules` where `is_enabled = true`
2. For each rule, resolve the target employee set
3. Query `activity_daily_summary` for the relevant time window
4. **If no rows found:** log "no monitoring data for tenant {id}" at Debug level, skip to next rule. **No error thrown. No alert created.**
5. If threshold is breached for any employee: create `exception_alerts` row
6. Publish `ExceptionAlertCreatedEvent` ? notification handler sends notifications to `notify_on_trigger` users

### Conditions and Data Source

| Condition | Data source column | Threshold comparison |
|:---|:---|:---|
| `idle_percent_exceeds` | `activity_daily_summary.idle_minutes / total_tracked_minutes` | idle% > threshold |
| `active_time_below` | `activity_daily_summary.active_minutes` | active_minutes < threshold |
| `app_usage_exceeds` | `activity_daily_summary.app_usage_json` — sum of flagged app categories | minutes > threshold |
| `bulk_download_detected` | `activity_daily_summary.file_transfer_mb` | mb > threshold in window |
| `out_of_hours_activity` | `activity_daily_summary.out_of_hours_active_minutes` | minutes > threshold |

### Deduplication

An alert is not created if an **open** alert already exists for the same `(rule_id, employee_id)` pair. The evaluation job skips creation and instead updates `exception_alerts.last_evaluated_at`. This prevents alert flooding on the same condition.

---

## Alert Lifecycle

```
created ? open ? acknowledged ? closed
                ? escalated (if unacknowledged past deadline)
```

| State | Meaning |
|:---|:---|
| `open` | Alert created, not yet reviewed |
| `escalated` | Alert was not acknowledged within `escalation_after_hours` — escalated via Workflow Engine |
| `acknowledged` | Reviewer acknowledged the alert with a note |
| `closed` | System auto-closed (condition no longer met at next evaluation) OR manually closed after acknowledgement |

### Acknowledgement Flow

1. Admin opens the Alerts list, clicks an open alert
2. Fills acknowledgement note (required)
3. `POST /tenant/v1/exceptions/alerts/{id}/acknowledge` with `{ "note": "Spoke with employee — resolved" }`
4. Creates `alert_acknowledgements` row
5. Alert status ? `acknowledged`
6. If the triggering condition is no longer met at the next job run ? status ? `closed`

### Escalation via Workflow Engine

If `escalation_after_hours > 0` and the alert remains `open` after that many hours:
1. Phase 2 Workflow Engine fires an escalation task when the tenant has the required workflow capability enabled
2. Escalation task notified to designated manager or HR role
3. Alert status ? `escalated`
4. Alert remains visible and acknowledgeable — escalation is informational

---

## Dashboard Alert — `monitoring.data_exfiltration_pattern`

When a `bulk_download_detected` rule fires, the platform Dashboard alert `monitoring.data_exfiltration_pattern` is created for ONEVO operators (not tenant admins). This alert code is prefixed `monitoring.*` because the data source is activity monitoring, even though the exception engine generates it.

| Property | Value |
|:---|:---|
| Alert code | `monitoring.data_exfiltration_pattern` |
| Source | Exception Engine (fires via `bulk_download_detected` rule) |
| Trigger | Bulk file access or download above tenant-configured exception rule threshold |
| Auto-resolve | Phase 1 lightweight alert detection evaluates condition no longer met; full Exception Engine auto-resolution is Phase 2 |
| Visible in | Developer Platform Dashboard |

---

## Behavior Without `monitoring` Module

This is the most important behavioral contract for the Exception Engine.

| State | Behavior |
|:---|:---|
| `exceptions` entitled, `monitoring` **not** entitled | Rules can be created and saved. The evaluation job runs on schedule, queries `activity_daily_summary` for the tenant, finds zero rows, logs at Debug level, and moves on. **Zero alerts are generated. No error is thrown.** |
| UI — Alerts screen | Shows "Waiting for Activity Monitoring data. Enable the Activity Monitoring module to start receiving exception alerts." empty state. Rule list is fully accessible. |
| UI — Rule creation form | Works normally. A banner at the top reads: "Activity Monitoring is not enabled for this tenant. Rules will be evaluated once monitoring is active." |
| Dashboard alert | `monitoring.data_exfiltration_pattern` will never fire (no bulk download data). |
| Provisioning warning | If an operator selects `exceptions` without `monitoring` in the subscription plan, the provisioning wizard Step 3 shows a warning: "Exception Engine works best with Activity Monitoring. Add Activity Monitoring for rule-based alerts to function." This is a **warning only** — the combination is allowed. |

---

## Entitlement Guard Behavior

```http
GET /tenant/v1/exceptions/rules

# Tenant not entitled to exceptions:
HTTP 403 Forbidden
{ "error": "module_not_entitled", "module": "exceptions" }

# Tenant entitled:
HTTP 200 OK
{ "rules": [...] }
```

Customer-app hides the Phase 2 "Exceptions" navigation section for non-entitled tenants.

---

## Key Database Tables

| Table | Purpose |
|:---|:---|
| `exception_rules` | Rule definitions: condition, threshold, target group, severity, escalation config |
| `exception_alerts` | Generated alerts: rule_id, employee_id, triggered_at, status |
| `alert_acknowledgements` | Acknowledgement records: alert_id, acknowledged_by_id, note, acknowledged_at |

Cross-module FKs:
- `exception_alerts.employee_id -> employees` (Core HR)
- `exception_rules.created_by_id -> users` (Infrastructure)
- `alert_acknowledgements.acknowledged_by_id -> users` (Infrastructure)

---

## Permissions

| Permission code | Description |
|:---|:---|
| `exceptions.rules.view` | View exception rules list and detail |
| `exceptions.rules.manage` | Create, edit, enable/disable, delete rules |
| `exceptions.alerts.view` | View exception alerts list and detail |
| `exceptions.alerts.acknowledge` | Acknowledge and close alerts |

---

## API Endpoints

| Method | Route | Description | Permission |
|:---|:---|:---|:---|
| GET | `/tenant/v1/exceptions/rules` | List all exception rules | `exceptions.rules.view` |
| POST | `/tenant/v1/exceptions/rules` | Create a new exception rule | `exceptions.rules.manage` |
| GET | `/tenant/v1/exceptions/rules/{id}` | Get rule detail | `exceptions.rules.view` |
| PATCH | `/tenant/v1/exceptions/rules/{id}` | Update rule (any field including `is_enabled`) | `exceptions.rules.manage` |
| DELETE | `/tenant/v1/exceptions/rules/{id}` | Delete a rule | `exceptions.rules.manage` |
| GET | `/tenant/v1/exceptions/alerts` | List alerts (filterable by status, severity, date) | `exceptions.alerts.view` |
| GET | `/tenant/v1/exceptions/alerts/{id}` | Get alert detail with employee context | `exceptions.alerts.view` |
| POST | `/tenant/v1/exceptions/alerts/{id}/acknowledge` | Acknowledge an alert with a note | `exceptions.alerts.acknowledge` |

All endpoints require `IsModuleEnabledAsync(tenantId, "exceptions")`.

---

## Error Responses

| Code | Error key | When |
|:---|:---|:---|
| 403 | `module_not_entitled` | `exceptions` not entitled |
| 422 | `rule_target_empty` | Target group resolves to zero employees |
| 422 | `invalid_threshold` | Threshold value out of range for the condition |
| 404 | `alert_not_found` | Alert ID does not exist or belongs to another tenant |
| 409 | `alert_already_acknowledged` | Attempting to acknowledge an already-acknowledged alert |

---

## Related

- [[developer-platform/module-dependency-matrix|Module Dependency Matrix]]
- [[developer-platform/modules/monitoring/end-to-end-logic|Activity Monitoring — End-to-End Logic]]
- [[developer-platform/modules/verification/end-to-end-logic|Identity Verification — End-to-End Logic]]
