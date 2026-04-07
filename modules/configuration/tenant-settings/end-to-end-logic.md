# Tenant Settings — End-to-End Logic

**Module:** Configuration
**Feature:** Tenant Settings

---

## Get Tenant Settings

### Flow

```
GET /api/v1/settings
  -> SettingsController.Get()
    -> [RequirePermission("settings:read")]
    -> ConfigurationService.GetTenantSettingsAsync(ct)
      -> 1. Get tenant_id from ITenantContext
      -> 2. Query tenant_settings WHERE tenant_id = @id
      -> 3. Map to TenantSettingsDto
      -> Return Result.Success(settingsDto)
```

## Update Tenant Settings

### Flow

```
PUT /api/v1/settings
  -> SettingsController.Update(UpdateSettingsCommand)
    -> [RequirePermission("settings:admin")]
    -> Validation: timezone valid, date_format valid, work_week_days non-empty
    -> ConfigurationService.UpdateTenantSettingsAsync(command, ct)
      -> 1. Load existing settings
      -> 2. Apply changes (partial update — only provided fields)
      -> 3. UPDATE tenant_settings
      -> 4. Invalidate settings cache (Redis, tenant-scoped)
      -> 5. Log to audit_logs
      -> Return Result.Success(updatedDto)
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Invalid timezone | Return 422 |
| Settings not found (new tenant) | Auto-create with defaults |
| Unauthorized | Return 403 |

## Related

- [[configuration/tenant-settings/overview|Tenant Settings Overview]]
- [[configuration/monitoring-toggles/overview|Monitoring Toggles]]
- [[configuration/retention-policies/overview|Retention Policies]]
- [[event-catalog]]
- [[error-handling]]
