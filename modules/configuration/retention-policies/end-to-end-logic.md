# Retention Policies — End-to-End Logic

**Module:** Configuration
**Feature:** Data Retention Policies

---

## Update Retention Policy

### Flow

```
PUT /api/v1/settings/retention
  -> RetentionController.Update(UpdateRetentionCommand)
    -> [RequirePermission("settings:admin")]
    -> RetentionService.UpdateAsync(command, ct)
      -> 1. Validate data_type: screenshots, verification_photos, activity_snapshots, audit_logs
      -> 2. Validate retention_days >= minimum (audit_logs minimum: 365 days, compliance)
      -> 3. UPSERT into retention_policies
      -> 4. Hangfire purge jobs will use these values on next run
      -> Return Result.Success(policyDto)
```

### Key Rules

- **Audit logs have a minimum retention** of 365 days (compliance requirement).
- **Screenshots default:** 30 days. Verification photos default: 30 days.
- **Activity snapshots default:** 90 days. Daily summaries: 2 years.
- **Purge jobs run nightly** and reference these policies for what to delete.

## Related

- [[configuration/retention-policies/overview|Retention Policies Overview]]
- [[configuration/tenant-settings/overview|Tenant Settings]]
- [[event-catalog]]
- [[error-handling]]
