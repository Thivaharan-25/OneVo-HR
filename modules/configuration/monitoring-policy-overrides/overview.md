# Monitoring Policy Overrides

**Module:** Configuration
**Feature:** Monitoring Policy Overrides

---

## Purpose

Monitoring policy overrides define group-level monitoring rules between tenant defaults and per-employee exceptions.

Use this feature when a tenant wants different monitoring behavior for a role, department, team, or job family. For example:

- Developers: application tracking, document tracking, communication tracking, and IDE/tool usage allowed.
- Finance: document tracking and communication tracking enabled, development tools not expected.
- Factory staff: desktop monitoring disabled, biometric/presence tracking enabled.
- Remote support team: work-location verification and meeting detection enabled.

This table should not replace tenant defaults or employee exceptions. It is the middle layer of the policy hierarchy.

---

## Policy Hierarchy

Effective monitoring policy is resolved in this order:

1. Tenant default: `monitoring_feature_toggles`.
2. Scope override: `monitoring_policy_overrides`.
3. Employee override: `employee_monitoring_overrides`.
4. Consent/disclosure gate.
5. Workforce Presence lifecycle gate.
6. App allowlist resolution.
7. Privacy/transparency mode.

Most specific non-null value wins. Null means inherit.

Scope override precedence when multiple scopes apply:

1. `role`
2. `job_family`
3. `department`
4. `team`

The later scope can override earlier scopes only for fields it explicitly sets. This lets a broad role policy define the baseline while a team can refine one or two features.

---

## Database Table

### `monitoring_policy_overrides`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `scope_type` | `varchar(30)` | `role`, `department`, `team`, `job_family` |
| `scope_id` | `uuid` | ID of the matching role/department/team/job family |
| `activity_monitoring` | `boolean` | Nullable |
| `application_tracking` | `boolean` | Nullable |
| `document_tracking` | `boolean` | Nullable |
| `communication_tracking` | `boolean` | Nullable |
| `screenshot_capture` | `boolean` | Nullable; command eligibility only |
| `meeting_detection` | `boolean` | Nullable |
| `device_tracking` | `boolean` | Nullable |
| `work_location_verification` | `boolean` | Nullable |
| `identity_verification` | `boolean` | Nullable |
| `biometric` | `boolean` | Nullable |
| `override_reason` | `varchar(255)` | Required for auditability |
| `set_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Unique constraint:** `(tenant_id, scope_type, scope_id)`

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/settings/monitoring/policy/{scopeType}/{scopeId}` | `monitoring:view-settings` | Read one scope override |
| PUT | `/api/v1/settings/monitoring/policy/{scopeType}/{scopeId}` | `monitoring:configure` | Create or update one scope override |
| DELETE | `/api/v1/settings/monitoring/policy/{scopeType}/{scopeId}` | `monitoring:configure` | Remove scope override |
| GET | `/api/v1/settings/monitoring/resolved/{employeeId}` | `monitoring:view-settings` | Preview final employee policy |

Valid `scopeType` values: `role`, `department`, `team`, `job-family`.

---

## Consent And Visibility

Admin policy does not replace employee disclosure/consent. If a required WorkPulse notice or consent is missing, the affected desktop collection category is disabled.

Employees should be able to see the policy assigned to them according to tenant `privacy_mode`:

- `full_transparency`: show enabled collector list and status.
- `partial`: show monitoring active/paused and required verification prompts.
- `covert`: hides self-service detail, but the desktop agent is still visible in the tray and Task Manager.

Screenshots and photos are special:

- Screenshots are never scheduled in Phase 1.
- Screenshots require explicit manager/admin command and employee notification before capture.
- Photo verification requires interaction through the TrayApp.

---

## Policy Refresh

Any change to tenant toggles, scope overrides, employee overrides, app allowlist, consent state, or employee role/team/department/job family assignment must trigger `RefreshPolicy` for affected agents through Agent Gateway.

If SignalR is unavailable, the agent receives the updated policy during heartbeat fallback.

---

## Related

- [[modules/configuration/overview|Configuration Module]]
- [[modules/configuration/monitoring-toggles/overview|Monitoring Toggles]]
- [[modules/configuration/employee-overrides/overview|Employee Overrides]]
- [[modules/configuration/app-allowlist/overview|App Allowlist]]
- [[modules/agent-gateway/overview|Agent Gateway]]
- [[security/compliance|Compliance]]
