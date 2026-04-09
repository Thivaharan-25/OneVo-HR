# Compliance & Governance — End-to-End Logic

**Module:** Shared Platform
**Feature:** Compliance & Data Governance

---

## Place Legal Hold

### Flow

```
POST /api/v1/compliance/legal-holds
  -> ComplianceController.PlaceHold(PlaceHoldCommand)
    -> [RequirePermission("settings:admin")]
    -> ComplianceService.PlaceHoldAsync(command, ct)
      -> 1. INSERT into legal_holds
         -> resource_type, resource_id, reason
      -> 2. Prevents data deletion for held resources
         -> All purge jobs check legal_holds before deleting
      -> Return Result.Success(holdDto)
```

## GDPR Data Export

### Flow

```
POST /api/v1/compliance/exports
  -> ComplianceController.RequestExport(ExportCommand)
    -> [RequirePermission("settings:admin")]
    -> ComplianceService.RequestExportAsync(command, ct)
      -> 1. INSERT into compliance_exports (status = 'pending')
      -> 2. Queue Hangfire job: GdprExportJob
         -> Collects all data for target_user_id across modules
         -> Generates ZIP with JSON/CSV files
         -> Uploads via IFileService
         -> UPDATE status = 'completed', set file_url
      -> 3. Notify requestor when complete
      -> Return Result.Success(exportDto)

```

## Related

- [[modules/shared-platform/compliance-governance/overview|Overview]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
- [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]]
- [[modules/infrastructure/file-management/overview|File Management]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
