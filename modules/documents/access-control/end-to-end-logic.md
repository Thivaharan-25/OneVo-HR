# Document Access Control — End-to-End Logic

**Module:** Documents
**Feature:** Access Control & Audit Logging

---

## Access Control Check

### Flow

```
Any document access request:
  -> DocumentAccessService.CheckAccessAsync(documentId, employeeId, ct)
    -> 1. Load document with category
    -> 2. Check access rules:
       -> Company-wide doc (employee_id = null): any employee in tenant
       -> Department doc: employee must be in that department
       -> Employee doc: must be the employee or their manager or HR admin
    -> 3. If access granted: INSERT into document_access_logs
    -> 4. If access denied: Return 403
```

## View Access Logs

### Flow

```
GET /api/v1/documents/{id}/access-logs
  -> AccessLogController.GetLogs(id)
    -> [RequirePermission("documents:manage")]
    -> AccessLogService.GetLogsAsync(documentId, ct)
      -> Query document_access_logs for this document
      -> Return paginated list with: employee, action, accessed_at, ip_address

```

## Related

- [[frontend/architecture/overview|Access Control Overview]]
- [[frontend/architecture/overview|Document Management]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
