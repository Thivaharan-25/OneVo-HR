# Monitoring Feature Toggles

**Module:** Configuration  
**Feature:** Monitoring Toggles

---

## Purpose

Global tenant-level ON/OFF switches per monitoring feature. Defaults set from `industry_profile` at tenant signup.

## Database Tables

### `monitoring_feature_toggles`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants, UNIQUE |
| `activity_monitoring` | `boolean` | Keyboard/mouse event counting |
| `application_tracking` | `boolean` | App usage tracking |
| `screenshot_capture` | `boolean` | Periodic screenshots |
| `meeting_detection` | `boolean` | Meeting time tracking |
| `device_tracking` | `boolean` | Device usage tracking |
| `identity_verification` | `boolean` | Photo verification |
| `biometric` | `boolean` | Fingerprint terminals |
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
