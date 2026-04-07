# Employee Monitoring Overrides

**Module:** Configuration  
**Feature:** Employee Overrides

---

## Purpose

Per-employee feature overrides. Override wins over tenant toggle. Null means inherit from tenant.

## Database Tables

### `employee_monitoring_overrides`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `activity_monitoring` | `boolean` | Nullable — null means inherit |
| `application_tracking` | `boolean` | Nullable |
| `screenshot_capture` | `boolean` | Nullable |
| `meeting_detection` | `boolean` | Nullable |
| `device_tracking` | `boolean` | Nullable |
| `identity_verification` | `boolean` | Nullable |
| `biometric` | `boolean` | Nullable |
| `override_reason` | `varchar(255)` | |
| `set_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

## Merge Logic

```csharp
effectivePolicy.ActivityMonitoring = employeeOverride?.ActivityMonitoring ?? tenantToggles.ActivityMonitoring;
```

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/settings/monitoring/overrides` | `monitoring:view-settings` | List overrides |
| POST | `/api/v1/settings/monitoring/overrides` | `monitoring:configure` | Set override |
| POST | `/api/v1/settings/monitoring/overrides/bulk` | `monitoring:configure` | Bulk set by dept/team |
| DELETE | `/api/v1/settings/monitoring/overrides/{employeeId}` | `monitoring:configure` | Remove override |

## Related

- [[configuration|Configuration Module]]
- [[configuration/monitoring-toggles/overview|Monitoring Toggles]]
- [[configuration/tenant-settings/overview|Tenant Settings]]
- [[configuration/integrations/overview|Integrations]]
- [[configuration/retention-policies/overview|Retention Policies]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[data-classification]]
- [[compliance]]
- [[WEEK1-shared-platform]]
