# Module: Configuration

**Namespace:** `ONEVO.Modules.Configuration`
**Phase:** 1 — Build
**Pillar:** Shared Foundation
**Owner:** Dev 4
**Tables:** 7

---

## Purpose

Tenant-level settings, external integration connections, and **monitoring configuration** (feature toggles + per-employee overrides). This module is the source of truth for "what monitoring features are enabled for which employees."

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/infrastructure/overview\|Infrastructure]] | `ITenantContext` | Multi-tenancy |
| **Consumed by** | [[modules/agent-gateway/overview\|Agent Gateway]] | `IConfigurationService` | Build agent monitoring policy |
| **Consumed by** | [[modules/activity-monitoring/overview\|Activity Monitoring]] | `IConfigurationService` | Check feature toggles before processing |
| **Consumed by** | [[modules/exception-engine/overview\|Exception Engine]] | `IConfigurationService` | Check if monitoring enabled for employee |
| **Consumed by** | [[modules/identity-verification/overview\|Identity Verification]] | `IConfigurationService` | Check verification policy |

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
    
    // App Allowlist
    Task<Result<List<AppAllowlistEntryDto>>> GetResolvedAppAllowlistAsync(Guid employeeId, CancellationToken ct);
    Task<Result<List<AppAllowlistEntryDto>>> GetAppAllowlistByScopeAsync(string scopeType, Guid? scopeId, CancellationToken ct);
    Task<Result> SetAppAllowlistEntryAsync(SetAppAllowlistCommand command, CancellationToken ct);
    Task<Result> RemoveAppAllowlistEntryAsync(Guid entryId, CancellationToken ct);
}
```

---

## Database Tables (7)

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

### `app_allowlists`

**Three-tier app allowlist configuration** following the hybrid permission model: tenant default → role override → employee override. Controls which applications are considered "allowed" during work time. Non-allowed app usage triggers exception alerts.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `scope_type` | `varchar(20)` | `tenant`, `role`, `employee` |
| `scope_id` | `uuid` | Null for tenant, role_id for role, employee_id for employee |
| `application_name` | `varchar(100)` | e.g., "Microsoft Teams", "Visual Studio Code" |
| `category` | `varchar(50)` | `communication`, `development`, `browser`, `design`, `productivity`, `other` |
| `is_allowed` | `boolean` | True = allowed during work, False = not allowed |
| `set_by_id` | `uuid` | FK → users (who configured this) |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Indexes:** `(tenant_id, scope_type, scope_id, application_name)` UNIQUE, `(tenant_id, scope_type)`

**Three-tier resolution (most specific wins):**
1. Check `employee` scope for this employee → if found, use it
2. Check `role` scope for this employee's role → if found, use it
3. Check `tenant` scope → default
4. If app not in any list → treated as **not allowed** (allowlist model) OR **allowed** (blocklist model) depending on `allowlist_mode` in tenant settings

```csharp
// Resolve effective app allowlist for an employee
public async Task<List<AppAllowlistEntry>> ResolveAppAllowlistAsync(Guid employeeId, CancellationToken ct)
{
    var employee = await _employeeService.GetAsync(employeeId, ct);
    var tenantApps = await GetAllowlistByScopeAsync(tenantId, "tenant", null, ct);
    var roleApps = await GetAllowlistByScopeAsync(tenantId, "role", employee.RoleId, ct);
    var employeeApps = await GetAllowlistByScopeAsync(tenantId, "employee", employeeId, ct);
    
    // Merge: employee > role > tenant (most specific wins per app name)
    var merged = tenantApps.ToDictionary(a => a.ApplicationName);
    foreach (var app in roleApps) merged[app.ApplicationName] = app;
    foreach (var app in employeeApps) merged[app.ApplicationName] = app;
    
    return merged.Values.ToList();
}
```

### `app_allowlist_audit`

Tracks changes to app allowlists for compliance.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `allowlist_id` | `uuid` | FK → app_allowlists |
| `action` | `varchar(20)` | `created`, `updated`, `deleted` |
| `changed_by_id` | `uuid` | FK → users |
| `old_value_json` | `jsonb` | Previous state |
| `new_value_json` | `jsonb` | New state |
| `changed_at` | `timestamptz` | |

---

## Domain Events (intra-module — MediatR)

> These events are published and consumed within this module only. They never leave the module.

| Event | Published When | Handler |
|:------|:---------------|:--------|
| _(none)_ | — | — |

## Integration Events (cross-module — RabbitMQ)

### Publishes

| Event | Routing Key | Published When | Consumers |
|:------|:-----------|:---------------|:----------|
| _(none)_ | — | — | — |

### Consumes

| Event | Routing Key | Source Module | Action Taken |
|:------|:-----------|:-------------|:-------------|
| `TenantCreated` | `infrastructure.tenant.created` | [[modules/infrastructure/overview\|Infrastructure]] | Seed default monitoring toggles based on tenant's `industry_profile` |

---

## Key Business Rules

1. **Industry profile sets defaults at signup** — admin can change any toggle at any time.
2. **Employee overrides allow per-person monitoring config** — a manufacturing company can turn on activity monitoring for just their 5 IT staff while keeping it off for 500 factory workers.
3. **Bulk overrides** — admin can set overrides by department, team, or job family. Individual overrides take precedence over bulk.
4. **Privacy mode** affects what employees can see about their own monitoring data (see [[AI_CONTEXT/known-issues|Known Issues]]).
5. **Always check monitoring toggles + overrides before processing any monitoring data.** Server must double-validate even though the agent checks on login.
6. **App allowlist follows the hybrid permission model** — tenant sets default allowed apps, roles can add/remove apps, individual employees can have further overrides. Most specific scope wins per app name.
7. **Allowlist changes trigger `RefreshPolicy` command** to affected agents — when an admin updates an app allowlist, the agent-gateway sends a `RefreshPolicy` command via SignalR so the agent re-fetches its policy (including the updated allowlist).
8. **Allowlist mode** is configurable per tenant: `allowlist` (only listed apps allowed, everything else flagged) or `blocklist` (only listed apps blocked, everything else allowed). Default is `allowlist`.

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
| GET | `/api/v1/settings/app-allowlist` | `monitoring:view-settings` | Get tenant-level app allowlist |
| POST | `/api/v1/settings/app-allowlist` | `monitoring:configure` | Add app to tenant allowlist |
| PUT | `/api/v1/settings/app-allowlist/{id}` | `monitoring:configure` | Update app entry |
| DELETE | `/api/v1/settings/app-allowlist/{id}` | `monitoring:configure` | Remove app from list |
| GET | `/api/v1/settings/app-allowlist/role/{roleId}` | `monitoring:configure` | Get role-level overrides |
| POST | `/api/v1/settings/app-allowlist/role/{roleId}` | `monitoring:configure` | Add role-level app override |
| GET | `/api/v1/settings/app-allowlist/employee/{employeeId}` | `monitoring:configure` | Get employee-level overrides |
| POST | `/api/v1/settings/app-allowlist/employee/{employeeId}` | `monitoring:configure` | Add employee-level app override |
| GET | `/api/v1/settings/app-allowlist/resolved/{employeeId}` | `monitoring:view-settings` | Get resolved (merged) allowlist for an employee |

## Features

- [[Userflow/Configuration/tenant-settings|Tenant Settings]] — Timezone, currency, work hours, privacy mode — frontend: [[modules/configuration/tenant-settings/frontend|Frontend]]
- [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]] — Global per-feature ON/OFF with industry profile defaults
- [[modules/configuration/employee-overrides/overview|Employee Overrides]] — Per-employee monitoring overrides (null = inherit from tenant)
- [[modules/configuration/integrations/overview|Integrations]] — External integration connections (Stripe, Resend, Google Calendar, Slack, LMS)
- [[modules/configuration/retention-policies/overview|Retention Policies]] — Per-data-type retention settings
- [[modules/configuration/app-allowlist/overview|App Allowlist]] — Three-tier app allowlist (tenant → role → employee) following hybrid permission model

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] — One settings row per tenant; overrides scoped to tenant + employee
- [[security/compliance|Compliance]] — Privacy mode controls employee self-visibility; retention policies for GDPR
- [[security/data-classification|Data Classification]] — Integration credentials encrypted at rest
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]] — Implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/agent-gateway/overview|Agent Gateway]], [[modules/activity-monitoring/overview|Activity Monitoring]], [[modules/identity-verification/overview|Identity Verification]]
