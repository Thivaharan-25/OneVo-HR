# Employee Monitoring Overrides

**Module:** Configuration  
**Feature:** Employee Overrides

---

## Purpose

Per-employee feature overrides. Employee override is the most specific monitoring policy layer and wins over tenant defaults and role/department/team/job-family scope overrides. Null means inherit from the resolved tenant/scope policy.

## Database Tables

### `employee_monitoring_overrides`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `activity_monitoring` | `boolean` | Nullable — null means inherit |
| `application_tracking` | `boolean` | Nullable |
| `document_tracking` | `boolean` | Nullable |
| `communication_tracking` | `boolean` | Nullable |
| `screenshot_capture` | `boolean` | Nullable |
| `meeting_detection` | `boolean` | Nullable |
| `device_tracking` | `boolean` | Nullable |
| `work_location_verification` | `boolean` | Nullable |
| `identity_verification` | `boolean` | Nullable |
| `biometric` | `boolean` | Nullable |
| `override_reason` | `varchar(255)` | |
| `set_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

## Merge Logic

```csharp
effectivePolicy.ActivityMonitoring =
    employeeOverride?.ActivityMonitoring
    ?? scopePolicy.ActivityMonitoring
    ?? tenantToggles.ActivityMonitoring;
```

Resolution order for every monitoring feature:

1. Tenant default from `monitoring_feature_toggles`.
2. Scope override from `monitoring_policy_overrides` (`role`, `job_family`, `department`, `team`).
3. Employee override from `employee_monitoring_overrides`.
4. Consent/disclosure gate. Missing consent disables desktop collection.
5. Workforce Presence lifecycle gate. No collection during breaks or after clock-out.

Employee overrides should be used for specific exceptions, not as the normal way to configure an entire role or department. Use `monitoring_policy_overrides` for lasting group-level policy.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/settings/monitoring/overrides` | `monitoring:view-settings` | List overrides |
| POST | `/api/v1/settings/monitoring/overrides` | `monitoring:configure` | Set override |
| POST | `/api/v1/settings/monitoring/overrides/bulk` | `monitoring:configure` | Bulk set by dept/team |
| DELETE | `/api/v1/settings/monitoring/overrides/{employeeId}` | `monitoring:configure` | Remove override |

## Related

- [[modules/configuration/overview|Configuration Module]]
- [[frontend/architecture/overview|Monitoring Toggles]]
- [[frontend/architecture/overview|Tenant Settings]]
- [[frontend/architecture/overview|Integrations]]
- [[frontend/architecture/overview|Retention Policies]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/data-classification|Data Classification]]
- [[security/compliance|Compliance]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]]
