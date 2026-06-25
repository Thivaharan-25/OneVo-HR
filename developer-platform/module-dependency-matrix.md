# Module Dependency Matrix

This document defines the formal dependency relationships between ONEVO Phase 1 modules — what requires what, what blocks removal, and exactly how the system behaves when a tenant has a partial set of modules.

Read this alongside the individual module end-to-end specs.

---

## Dependency Types

| Type | Meaning |
|:---|:---|
| **Hard** | Module X cannot be removed while module Y is active. Backend enforces this at `PUT /admin/v1/tenants/{id}/modules` with 422 `dependency_conflict`. |
| **Functional** | Module Y's primary job produces no output or reduced output without module X. No backend removal block — but documented here for provisioning guidance and UI empty-state behavior. |
| **Implicit (Foundation)** | Foundation modules are always present and non-removable. Any dependency on Foundation is always satisfied automatically. |

---

## Hard Dependencies — Backend-Enforced Removal Blocks

When an operator attempts to disable a module, the backend checks the table below before allowing the change. If a blocker is found, the request fails with `422 dependency_conflict` listing every active dependent.

| Module to Disable | Blocked While These Are Active | Reason |
|:---|:---|:---|
| `core_hr` | `time_off`, `calendar`, `monitoring`, `verification`, `exceptions`, `monitoring`, `analytics` | All intelligent modules reference employee records via FK |
| `monitoring` | `exceptions`, `monitoring` | Both depend on activity data produced by monitoring |
| `org` | N/A — Foundation, non-removable | — |
| `auth` | N/A — Foundation, non-removable | — |
| All other Foundation | N/A — non-removable | — |

> **Note:** `verification` does not block removal of `monitoring`. Verification works standalone — clock-in photos and attendance/biometric devices do not require activity data.

---

## Functional Dependencies — Documented Soft Requirements

These are not enforced as removal blocks but define what "empty state" means and what guidance to show during provisioning.

| Module | Soft-Requires | Behavior When Absent |
|:---|:---|:---|
| `exceptions` | `monitoring` | Exception rules can be created and saved. Evaluation background job runs on schedule but finds zero `activity_daily_summary` rows for the tenant ? zero alerts generated. UI shows "Waiting for activity monitoring data" empty state on the Alerts screen. Operators are warned at provisioning time if `exceptions` is selected without `monitoring`. |
| `monitoring` | `monitoring` | Monitoring insights exist in two layers: (1) core-employee-derived metrics (headcount, turnover, Time Off trends) — these work with Core HR data only; (2) Activity-derived metrics (productivity scores, idle trends, work-pattern analysis) — these show empty state without `monitoring`. |
| `analytics` | `monitoring`, `time_off`, `core_hr` | Cross-module analytics renders only sections for modules the tenant has. Sections for absent modules show "Module not available on your plan" placeholder. Plans that include analytics should normally include enough source modules to avoid an empty analytics experience. |
| `chat_ai` | Phase 2 AI provider config in System Config | Phase 2 only. If `chat_ai` is entitled but no Agentic Chat AI provider is configured in System Config, Agentic Chat shows a "Configuration required" error on launch. |
| `verification` | _(none — works standalone)_ | Clock-in/out photo capture and attendance/biometric device verification function without activity monitoring or exception rules. |
| `monitoring` | _(none — works standalone)_ | Activity data is collected and stored independently. Exception alerts will not fire without the `exceptions` module but the data pipeline itself is unaffected. |

---

## Schema-Level (FK) Dependencies

These FK constraints cross module boundaries. They are satisfied at provisioning time because Foundation and Core HR are always present whenever these modules are activated.

| Module | FK Source Table.Column | Resolves To | Target Module |
|:---|:---|:---|:---|
| `monitoring` | `activity_daily_summary.employee_id` | `employees` | `core_hr` |
| `monitoring` | `activity_raw_buffer.agent_device_id` | `registered_agents` | Agent Gateway (infra) |
| `monitoring` | `monitoring_evidence_assets.employee_id` | `employees` | `core_hr` |
| `monitoring` | `monitoring_evidence_assets.file_record_id` | `file_records` | Infrastructure (shared) |
| `verification` | `biometric_devices.legal_entity_id` | `legal_entities` | `org` (Foundation) |
| `verification` | `biometric_enrollments.employee_id` | `employees` | `core_hr` |
| `verification` | `biometric_events.employee_id` | `employees` | `core_hr` |
| `verification` | `verification_records.employee_id` | `employees` | `core_hr` |
| `verification` | `verification_evidence_assets.file_record_id` | `file_records` | Infrastructure (shared) |
| `exceptions` | `exception_alerts.employee_id` | `employees` | `core_hr` |
| `exceptions` | `exception_rules.created_by_id` | `users` | Infrastructure (shared) |
| `exceptions` | `alert_acknowledgements.acknowledged_by_id` | `users` | Infrastructure (shared) |

---

## Partial Intelligence Package Combinations

The five Intelligence modules (`monitoring`, `monitoring`, `verification`, `exceptions`, `analytics`) are sold independently. This table defines exact system behavior for every combination a tenant might purchase.

| `monitoring` | `verification` | `exceptions` | `monitoring` | `analytics` | System Behavior |
|:---:|:---:|:---:|:---:|:---:|:---|
| ? | | | | | Activity data collected, screenshots captured, idle-time tracking active, `monitoring.high_idle_time` dashboard alerts fire. No identity verification. No rule-based alerts. |
| ? | ? | | | | Activity monitoring + clock-in/out photo verification + attendance/biometric device scans. `identity.verification_failed_spike` alerts fire. No rule-based exception alerts. |
| ? | | ? | | | Activity monitoring + exception rule evaluation. Exception alerts fire when thresholds are breached. `monitoring.data_exfiltration_pattern` alert fires via exception engine. No identity verification. |
| ? | ? | ? | | | Activity + identity verification + exception rule engine. Recommended Intelligence baseline. All alert types fire. |
| ? | | | ? | | Activity data collected + monitoring insights fully populated (both core-employee-derived and activity-derived metrics). No rule-based alerts. No identity verification. |
| ? | ? | ? | ? | ? | Full Intelligence Package. All features and alerts available. |
| | ? | | | | Clock-in/out photo capture + attendance/biometric device verification only. No activity pipeline running. `identity.verification_failed_spike` alerts still fire. |
| | | ? | | | Exception rules created and saved. Evaluation job runs on schedule but produces zero alerts — no monitoring data exists. UI shows "Waiting for Activity Monitoring data" empty state. No error thrown. |
| | | | ? | | Monitoring insights show only core-employee-derived metrics (headcount, Time Off trends, turnover). Activity-derived metrics (productivity, idle) show empty state with "Activity Monitoring required" label. |
| | | | | ? | Analytics renders Core Employee sections (Time Off summary, headcount). All Intelligence sections show "Module not available on your plan" placeholder. |

---

## Provisioning Validation Rules

Enforced at `PUT /admin/v1/tenants/{id}/modules`:

```
1. Disabling `monitoring` while `exceptions` is active   ? 422 dependency_conflict
2. Disabling `monitoring` while `monitoring` is active    ? 422 dependency_conflict
3. Disabling `core_hr` while any of the following are active:
   time_off, calendar, monitoring, verification, exceptions, monitoring, analytics
                                                         ? 422 dependency_conflict
4. Disabling any Foundation module                       ? 422 foundation_module_immutable
```

Response body for `dependency_conflict`:

```json
{
  "error": "dependency_conflict",
  "module_to_disable": "monitoring",
  "blocked_by": ["exceptions", "monitoring"],
  "message": "Cannot disable 'monitoring' while 'exceptions', 'monitoring' are active. Disable those modules first."
}
```

---

## Entitlement Guard — API Behavior

Every feature API endpoint belonging to a sellable module calls `IModuleEntitlementService.IsModuleEnabledAsync(tenantId, moduleKey)` before executing. Foundation module endpoints skip this check.

**Response when not entitled:**

```http
HTTP 403 Forbidden
Content-Type: application/json

{
  "error": "module_not_entitled",
  "module": "monitoring",
  "message": "This tenant does not have the 'monitoring' module enabled."
}
```

The tenant-facing app hides navigation sidebar items for non-entitled modules using the entitlement list returned at login. The API guard is defense-in-depth, not the primary UX gate.

---

## Related

- [[developer-platform/modules/monitoring/end-to-end-logic|Activity Monitoring — End-to-End Logic]]
- [[developer-platform/modules/verification/end-to-end-logic|Identity Verification — End-to-End Logic]]
- [[developer-platform/modules/exceptions/end-to-end-logic|Exception Engine — End-to-End Logic]]
- [[developer-platform/modules/subscription-manager/end-to-end-logic|Subscription Plans — End-to-End Logic]]
