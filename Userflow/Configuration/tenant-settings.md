# Tenant Settings

**Area:** Configuration  
**Required Permission(s):** `settings:admin`  
**Related Permissions:** `settings:read` (view only)

---

## Preconditions

- Tenant provisioned → [[tenant-provisioning]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Settings
- **UI:** Sidebar → Settings → General
- **API:** `GET /api/v1/configuration/tenant`

### Step 2: Configure General Settings
- **UI:** Edit:
  - Company name, logo
  - Default timezone
  - Date format (DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD)
  - Currency (primary + secondary)
  - Fiscal year start month
  - Work week days (e.g., Mon-Fri or Sun-Thu)
  - Default language (English, others)
- **Backend:** TenantSettingsService.UpdateAsync() → [[tenant-settings]]
- **DB:** `tenant_settings`

### Step 3: Save
- **API:** `PUT /api/v1/configuration/tenant`
- **Result:** Changes apply to all users in tenant → affects date display, currency formatting, payroll periods, schedule generation

## Variations

### With `settings:read` only
- Can view all settings but cannot edit

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Invalid timezone | Validation fails | "Invalid timezone selected" |
| Changing fiscal year mid-year | Warning | "Changing fiscal year will affect leave entitlements and payroll" |

## Events Triggered

- `TenantSettingsUpdated` → [[event-catalog]]

## Related Flows

- [[tenant-provisioning]]
- [[tenant-branding]]
- [[monitoring-toggles]]

## Module References

- [[tenant-settings]]
- [[configuration]]
