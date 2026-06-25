# Monitoring Feature Toggles

**Module:** Configuration  
**Feature:** Monitoring Toggles

---

## Purpose

Global tenant-level ON/OFF switches per monitoring feature. Defaults set from `industry_profile` during operator provisioning. These are the first layer of the effective employee policy; scope and employee overrides may refine them.

## Database Tables

### `monitoring_feature_toggles`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants, UNIQUE |
| `activity_monitoring` | `boolean` | Keyboard/mouse event counting |
| `application_tracking` | `boolean` | App usage tracking |
| `document_tracking` | `boolean` | Document tool time tracking |
| `communication_tracking` | `boolean` | Communication tool active time and send counts |
| `screenshot_capture` | `boolean` | Allows authorized on-demand screenshot capture |
| `auto_screenshot_capture` | `boolean` | Allows automatic screenshot capture when monitoring detects a deviation |
| `meeting_detection` | `boolean` | Meeting time tracking |
| `device_tracking` | `boolean` | Device usage tracking |
| `work_location_verification` | `boolean` | Network-based work-location compliance |
| `identity_verification` | `boolean` | Photo verification |
| `biometric` | `boolean` | Biometric/attendance terminals |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

## Industry Profile Defaults

| Profile | activity | app_tracking | screenshot | meeting | device | identity | biometric |
|:--------|:---------|:-------------|:-----------|:--------|:-------|:---------|:----------|
| office_it | Yes | Yes | No | Yes | Yes | Yes | No |
| manufacturing | No | No | No | No | No | No | Yes |
| retail | No | No | No | No | No | No | Yes |
| healthcare | No | No | No | No | No | No | Yes |
| custom | No | No | No | No | No | No | No |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/settings/monitoring` | `monitoring:view-settings` | Get monitoring toggles |
| PUT | `/api/v1/settings/monitoring` | `monitoring:configure` | Update toggles |

## Effective Policy Resolution

Tenant toggles are not sent to the agent directly unless no more-specific policy exists. Configuration resolves:

1. Tenant defaults from `monitoring_feature_toggles`.
3. Employee overrides from `employee_monitoring_overrides`.
4. Consent/disclosure and Time & Attendance lifecycle gates.
5. App allowlist and transparency mode.

The agent receives only the resolved policy for the signed-in employee/device.

## Monitoring Alert Routing Policy

Tenant-level configuration controlling how monitoring alert recipients are resolved. Stored in `monitoring_alert_policy`.

| Setting | Type | Default | Description |
|:--------|:-----|:--------|:------------|
| `monitoring_alert_recipient_resolver` | `varchar(50)` | `management_coverage_availability_chain` | Resolution strategy: `management_coverage_availability_chain` or `reporting_manager` |
| `monitoring_alert_wait_for_scheduled_recipient_grace_minutes` | `int` | `15` | Minutes to wait for a scheduled responsible person before skipping to next |
| `monitoring_alert_fallback_to_management_coverage_chain` | `boolean` | `true` | When `reporting_manager` is selected, fall back to management coverage chain if reporting manager is unavailable |
| `monitoring_alert_unresolved_routing_action` | `varchar(30)` | `create_routing_issue` | Action when no eligible available person exists: `create_routing_issue` or `leave_unassigned` |

**Resolution uses:** management coverage assignments, employee schedule, clock-in/presence state, approved leave / unavailable state, permission checks (`monitoring:alerts:read`, `monitoring:alerts:resolve`, `verification:review`, or relevant alert-specific permission).

### API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/configuration/monitoring-alert-policy` | `monitoring:view-settings` | Get alert routing policy |
| PUT | `/api/v1/configuration/monitoring-alert-policy` | `monitoring:configure` | Update alert routing policy |

## Related

- [[modules/configuration/overview|Configuration Module]]
- [[frontend/architecture/overview|Employee Overrides]]
- [[frontend/architecture/overview|Tenant Settings]]
- [[frontend/architecture/overview|Integrations]]
- [[frontend/architecture/overview|Retention Policies]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/data-classification|Data Classification]]
- [[security/compliance|Compliance]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]]
