# Module: Configuration

**Namespace:** `ONEVO.Modules.Configuration`
**Pillar:** Shared Foundation
**Owner:** Dev 1 (Week 4)
**Tables:** 5

---

## Purpose

Tenant-level settings, external integration connections, and **monitoring configuration** (feature toggles + per-employee overrides). This module is the source of truth for "what monitoring features are enabled for which employees."

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[infrastructure]] | `ITenantContext` | Multi-tenancy |
| **Consumed by** | [[agent-gateway]] | `IConfigurationService` | Build agent monitoring policy |
| **Consumed by** | [[activity-monitoring]] | `IConfigurationService` | Check feature toggles before processing |
| **Consumed by** | [[exception-engine]] | `IConfigurationService` | Check if monitoring enabled for employee |
| **Consumed by** | [[identity-verification]] | `IConfigurationService` | Check verification policy |

---

## Public Interface

```csharp
public interface IConfigurationService
{
    Task<Result<TenantSettingsDto>> GetTenantSettingsAsync(CancellationToken ct);
    Task<Result<TenantSettingsDto>> UpdateTenantSettingsAsync(UpdateSettingsCommand command, CancellationToken ct);
    Task<Result<MonitoringTogglesDto>> GetMonitoringTogglesAsync(Guid tenantId, CancellationToken ct);
    Task<Result<MonitoringTogglesDto>> UpdateMonitoringTogglesAsync(UpdateTogglesCommand command, CancellationToken ct);
    Task<Result<EmployeeMonitoringOverrideDto>> GetEmployeeOverrideAsync(Guid employeeId, CancellationToken ct);
    Task<Result> SetEmployeeOverrideAsync(SetOverrideCommand command, CancellationToken ct);
    Task<Result> SetBulkOverrideAsync(SetBulkOverrideCommand command, CancellationToken ct); // By department/team/job family
}
```

---

## Database Tables (5)

### `tenant_settings`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants, UNIQUE |
| `timezone` | `varchar(50)` | Default timezone |
| `date_format` | `varchar(20)` | |
| `currency_code` | `varchar(3)` | |
| `work_week_days_json` | `jsonb` | e.g., `[1,2,3,4,5]` |
| `work_hours_start` | `time` | |
| `work_hours_end` | `time` | |
| `privacy_mode` | `varchar(20)` | `full_transparency`, `partial`, `covert` |
| `data_retention_days_json` | `jsonb` | Per-data-type retention settings |
| `settings_json` | `jsonb` | Extensible settings |
| `updated_at` | `timestamptz` | |

### `monitoring_feature_toggles`

**Global tenant-level ON/OFF per monitoring feature.** Defaults set from `industry_profile` at tenant signup.

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

**Industry profile defaults:**

| Profile | activity | app_tracking | screenshot | meeting | device | identity | biometric |
|:--------|:---------|:-------------|:-----------|:--------|:-------|:---------|:----------|
| office_it | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ |
| manufacturing | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| retail | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| healthcare | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| custom | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

### `employee_monitoring_overrides`

Per-employee feature overrides. **Override wins over tenant toggle.**

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `activity_monitoring` | `boolean` | Nullable — null means inherit from tenant |
| `application_tracking` | `boolean` | Nullable |
| `screenshot_capture` | `boolean` | Nullable |
| `meeting_detection` | `boolean` | Nullable |
| `device_tracking` | `boolean` | Nullable |
| `identity_verification` | `boolean` | Nullable |
| `biometric` | `boolean` | Nullable |
| `override_reason` | `varchar(255)` | Why this employee is different |
| `set_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Merge logic:** For each feature, if employee override is non-null, use it. Otherwise, use tenant toggle.

```csharp
// Effective policy computation
effectivePolicy.ActivityMonitoring = employeeOverride?.ActivityMonitoring ?? tenantToggles.ActivityMonitoring;
```

### `integration_connections`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `integration_type` | `varchar(50)` | `stripe`, `resend`, `google_calendar`, `slack`, `lms` |
| `config_json` | `jsonb` | |
| `credentials_encrypted` | `bytea` | Encrypted |
| `status` | `varchar(20)` | `active`, `inactive`, `error` |
| `last_sync_at` | `timestamptz` | |

### `retention_policies`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `data_type` | `varchar(50)` | `screenshots`, `verification_photos`, `activity_snapshots`, `audit_logs` |
| `retention_days` | `int` | |
| `created_at` | `timestamptz` | |

---

## Key Business Rules

1. **Industry profile sets defaults at signup** — admin can change any toggle at any time.
2. **Employee overrides allow per-person monitoring config** — a manufacturing company can turn on activity monitoring for just their 5 IT staff while keeping it off for 500 factory workers.
3. **Bulk overrides** — admin can set overrides by department, team, or job family. Individual overrides take precedence over bulk.
4. **Privacy mode** affects what employees can see about their own monitoring data (see [[known-issues]]).
5. **Always check monitoring toggles + overrides before processing any monitoring data.** Server must double-validate even though the agent checks on login.

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/settings` | `settings:read` | Get tenant settings |
| PUT | `/api/v1/settings` | `settings:admin` | Update settings |
| GET | `/api/v1/settings/monitoring` | `monitoring:view-settings` | Get monitoring toggles |
| PUT | `/api/v1/settings/monitoring` | `monitoring:configure` | Update toggles |
| GET | `/api/v1/settings/monitoring/overrides` | `monitoring:view-settings` | List employee overrides |
| POST | `/api/v1/settings/monitoring/overrides` | `monitoring:configure` | Set employee override |
| POST | `/api/v1/settings/monitoring/overrides/bulk` | `monitoring:configure` | Bulk set by dept/team |
| DELETE | `/api/v1/settings/monitoring/overrides/{employeeId}` | `monitoring:configure` | Remove override (inherit tenant) |
| GET | `/api/v1/settings/integrations` | `settings:admin` | List integrations |
| POST | `/api/v1/settings/integrations` | `settings:admin` | Add integration |
| GET | `/api/v1/settings/retention` | `settings:admin` | Retention policies |
| PUT | `/api/v1/settings/retention` | `settings:admin` | Update retention |

## Features

- [[tenant-settings]] — Timezone, currency, work hours, privacy mode — frontend: [[tenant-settings/frontend]]
- [[monitoring-toggles]] — Global per-feature ON/OFF with industry profile defaults
- [[employee-overrides]] — Per-employee monitoring overrides (null = inherit from tenant)
- [[integrations]] — External integration connections (Stripe, Resend, Google Calendar, Slack, LMS)
- [[retention-policies]] — Per-data-type retention settings

---

## Related

- [[multi-tenancy]] — One settings row per tenant; overrides scoped to tenant + employee
- [[compliance]] — Privacy mode controls employee self-visibility; retention policies for GDPR
- [[data-classification]] — Integration credentials encrypted at rest
- [[WEEK1-shared-platform]] — Implementation task file

See also: [[module-catalog]], [[agent-gateway]], [[activity-monitoring]], [[identity-verification]]
