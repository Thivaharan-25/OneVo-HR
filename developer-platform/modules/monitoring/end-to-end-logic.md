# Activity Monitoring — End-to-End Logic

**Module key:** `monitoring`  
**Pillar:** Workforce Intelligence (Package 1)  
**Pricing unit:** Per employee  
**Entitlement guard:** All endpoints call `IsModuleEnabledAsync(tenantId, "monitoring")` → 403 `module_not_entitled` if not entitled  
**Dependency:** See [[developer-platform/module-dependency-matrix|Module Dependency Matrix]]

---

## What This Module Does

Activity Monitoring tracks employee computer usage during work hours via the WorkPulse desktop agent. It collects app usage, active window time, idle periods, website visits, and periodic screenshots. Data is aggregated into daily summaries and surfaced as timelines, productivity scores, and dashboard alerts.

It is the **data source** for the Exception Engine. Without `monitoring`, the exception engine has no data to evaluate.

---

## Data Collection Pipeline

### Agent Collection (WorkPulse)

The WorkPulse Windows service collects activity data **only between clock-in and clock-out** events. The agent checks the tenant's monitoring policy before capturing anything.

| Event type | What is collected | Privacy rule |
|:---|:---|:---|
| Active window change | App name, window title (SHA-256 hashed) | Title never stored in plain text |
| Keyboard/mouse activity | Count of events per minute (not keystrokes) | Content never captured |
| Idle detection | Consecutive minutes with zero keyboard/mouse events | — |
| Screenshot | Compressed screenshot image → file storage | Frequency configurable per tenant; default: every 10 min during active period |
| Website visit (browser extension) | Domain only, not full URL | — |

Collection stops immediately when:
- Employee clocks out
- Employee manually pauses monitoring (if tenant allows it)
- Monitoring is disabled for that employee via `employee_monitoring_overrides`

### Raw Buffer → Daily Summary

1. Agent sends batched events to `POST /agent/v1/activity/batch` every 60 seconds
2. Events are written to `activity_raw_buffer` (append-only, never UPDATE)
3. A Hangfire background job aggregates raw buffer rows into `activity_daily_summary` — runs every 15 minutes for the current day, once at midnight to finalise the previous day
4. Raw buffer rows older than 30 days are archived (configurable retention)

---

## Key Features

### Activity Timeline

A per-employee chronological view of the work session. Available at the employee detail page in the management app.

| Component | Data source | Notes |
|:---|:---|:---|
| Clock-in / clock-out markers | `verification_records` (type `clock_in`, `clock_out`) | Shows even without `verification` module — uses agent clock-in event if no photo verification |
| App usage segments | `activity_daily_summary.app_usage_json` | Colour-coded by app category |
| Idle segments | `activity_daily_summary.idle_minutes_json` | Grey blocks |
| Screenshot thumbnails | `screenshots` joined to `file_records` | Click to expand full image |
| Website usage (if browser ext.) | `activity_daily_summary.website_usage_json` | Domain-level only |

### Screenshot Gallery

- Grid view of screenshots for a selected employee and date range
- Requires permission `monitoring.screenshots.view`
- Screenshots stored in tenant storage pool as compressed JPEG (counted toward `tenant_storage_limit_gb`)
- Deleted with employee if employee is offboarded and data purged per retention policy

### Productivity Summary

Daily and weekly cards per employee showing:
- Active time (minutes with keyboard/mouse activity)
- Idle time (minutes with zero input)
- Top 5 apps by time
- Productivity score = active_minutes / (active_minutes + idle_minutes) × 100

### Idle-Time Alert

Dashboard alert `monitoring.high_idle_time`:
- Condition: > 50% of a tenant's currently active employees show idle state for > 2 consecutive hours during configured work hours
- Trigger: Health check Hangfire job (runs every 30 min)
- Auto-resolve: Idle percentage drops below 30%
- Alert visible in Developer Platform Dashboard for ONEVO operators

---

## Per-Employee Monitoring Overrides

Tenants can disable or restrict monitoring for specific employees. Overrides are stored in `employee_monitoring_overrides` (owned by the **Configuration** module, but readable by Monitoring).

| Override value | Effect |
|:---|:---|
| `full` (default) | All monitoring active — screenshots, idle, app usage |
| `no_screenshots` | Activity tracked; screenshots disabled for this employee |
| `activity_only` | App + idle tracking only; screenshots and website visits disabled |
| `disabled` | All monitoring off for this employee. **Removes from Package 1 billable count.** |

> **Billing rule:** Employees with override = `disabled` are excluded from the Package 1 billable seat count at the monthly billing snapshot.

---

## Configuration Dependencies

| Setting | Location | Effect on monitoring |
|:---|:---|:---|
| Screenshot interval | Tenant config (Configuration module, Step 4 provisioning) | Minutes between screenshots; default 10; min 5, max 60 |
| Enable Camera Photo Verification | Tenant config (Step 4 provisioning) | When On, WorkPulse agent may capture a photo for identity spot-checks — requires `verification` module entitlement |
| Work hours | Tenant config (Core HR) | Idle-time thresholds only count during configured work hours |
| Per-employee overrides | `employee_monitoring_overrides` | See table above |

---

## Behavior Without Other Intelligence Modules

| Missing module | Effect on `monitoring` |
|:---|:---|
| No `exceptions` | Activity data fully collected and stored. No rule-based alert evaluation. Dashboard `monitoring.data_exfiltration_pattern` alert will never fire (that alert requires the exception engine). `monitoring.high_idle_time` still fires — it is generated by a monitoring-owned health-check job, not the exception engine. |
| No `verification` | Activity timeline does not show clock-in/out photo thumbnails. Clock-in markers are based on agent clock events only. Otherwise unaffected. |
| No `workforce` | Workforce productivity reports are not available. Raw monitoring data is still collected and accessible via the Monitoring module UI. |
| No `analytics` | Cross-module analytics dashboard does not show monitoring-derived charts. Monitoring module's own UI is unaffected. |

---

## Entitlement Guard Behavior

```http
GET /tenant/v1/monitoring/employees/{id}/summary

# Tenant not entitled to monitoring:
HTTP 403 Forbidden
{ "error": "module_not_entitled", "module": "monitoring" }

# Tenant entitled:
HTTP 200 OK
{ ... daily summary ... }
```

The management app hides the "Monitoring" sidebar section entirely for non-entitled tenants based on the entitlement list in the JWT claims.

---

## Key Database Tables

| Table | Module | Purpose |
|:---|:---|:---|
| `activity_raw_buffer` | monitoring | Append-only raw events from agent (30-day rolling retention) |
| `activity_daily_summary` | monitoring | Aggregated per-employee per-day stats (permanent) |
| `screenshots` | monitoring | Screenshot metadata; image stored in file storage |
| `employee_monitoring_overrides` | configuration | Per-employee monitoring policy overrides |

---

## Permissions

| Permission code | Description |
|:---|:---|
| `monitoring.view` | View activity summaries and timelines |
| `monitoring.screenshots.view` | View screenshot gallery |
| `monitoring.overrides.manage` | Set or update per-employee monitoring overrides |
| `monitoring.export` | Export activity data to CSV |

---

## API Endpoints

| Method | Route | Description | Permission |
|:---|:---|:---|:---|
| GET | `/tenant/v1/monitoring/employees/{id}/summary` | Daily productivity summary for an employee | `monitoring.view` |
| GET | `/tenant/v1/monitoring/employees/{id}/timeline` | Activity timeline for a date | `monitoring.view` |
| GET | `/tenant/v1/monitoring/employees/{id}/screenshots` | Screenshot gallery (paginated) | `monitoring.screenshots.view` |
| GET | `/tenant/v1/monitoring/summary` | Aggregate monitoring summary for all employees | `monitoring.view` |
| PATCH | `/tenant/v1/monitoring/employees/{id}/overrides` | Update monitoring override for an employee | `monitoring.overrides.manage` |
| GET | `/tenant/v1/monitoring/employees/{id}/app-usage` | App usage breakdown for a date range | `monitoring.view` |

All endpoints require `IsModuleEnabledAsync(tenantId, "monitoring")` check before execution.

---

## Dashboard Alerts Generated by This Module

| Alert code | Trigger | Auto-resolves |
|:---|:---|:---|
| `monitoring.high_idle_time` | >50% of active employees idle >2 consecutive hours during work hours | Idle % drops below 30% |
| `monitoring.data_exfiltration_pattern` | **Generated by Exception Engine** when bulk-download rule fires — attributed to monitoring as the data source | Exception engine clears the rule threshold |

---

## Related

- [[developer-platform/module-dependency-matrix|Module Dependency Matrix]]
- [[developer-platform/modules/exceptions/end-to-end-logic|Exception Engine — End-to-End Logic]]
- [[developer-platform/modules/verification/end-to-end-logic|Identity Verification — End-to-End Logic]]
- [[developer-platform/modules/workforce/end-to-end-logic|Workforce Analytics — End-to-End Logic]]
