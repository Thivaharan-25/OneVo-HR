# Employee Monitoring Overrides

**Module:** Configuration  
**Feature:** Employee Overrides

---

## Purpose


## Database Tables

### `employee_monitoring_overrides`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `activity_monitoring` | `boolean` | Nullable - null means inherit |
| `application_tracking` | `boolean` | Nullable |
| `document_tracking` | `boolean` | Nullable |
| `communication_tracking` | `boolean` | Nullable |
| `screenshot_capture` | `boolean` | Nullable; allows authorized on-demand screenshot capture |
| `auto_screenshot_capture` | `boolean` | Nullable; allows automatic screenshot capture when monitoring detects a deviation |
| `meeting_detection` | `boolean` | Nullable |
| `device_tracking` | `boolean` | Nullable |
| `work_location_verification` | `boolean` | Nullable |
| `identity_verification` | `boolean` | Nullable |
| `biometric` | `boolean` | Nullable |
| `override_reason` | `varchar(255)` | |
| `set_by_id` | `uuid` | FK -> users |
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
3. Employee override from `employee_monitoring_overrides`.
4. Consent/disclosure gate. Missing required WorkPulse notice or consent disables only the affected desktop collection category.
5. Time & Attendance lifecycle gate. No collection during breaks or after clock-out.

Employee overrides should be used for specific exceptions, not as the normal way to configure an entire position or department. Use `monitoring_policy_overrides` for lasting group-level policy.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/settings/monitoring/overrides` | `monitoring:view-settings` | List overrides |
| POST | `/api/v1/settings/monitoring/overrides` | `monitoring:configure` | Set override |
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
