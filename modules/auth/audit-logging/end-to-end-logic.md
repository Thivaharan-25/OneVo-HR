# Audit Logging — End-to-End Logic

**Module:** Auth
**Feature:** Audit Logging

---

## Log Audit Event

### Flow

```
Domain event occurs (e.g., employee.created, leave.approved)
  -> AuditLogService.LogAsync(AuditLogCommand)
    -> 1. Build audit log entry:
       -> tenant_id from ITenantContext
       -> user_id from ICurrentUser (null for system actions)
       -> action = event type string
       -> resource_type + resource_id from event
       -> old_values_json / new_values_json (diff)
       -> ip_address from HttpContext
       -> correlation_id from request header
    -> 2. INSERT into audit_logs (partitioned by month via pg_partman)
    -> No events published (audit logs ARE the final destination)
```

## Query Audit Logs

### Flow

```
GET /api/v1/audit-logs?action=employee.created&from=2026-04-01&to=2026-04-05
  -> AuditLogController.Query(AuditLogQueryParams)
    -> [RequirePermission("settings:admin")]
    -> AuditLogService.QueryAsync(params, ct)
      -> 1. Build query with filters: action, resource_type, user_id, date range
      -> 2. Query audit_logs with pagination
         -> Partition pruning via date range (critical for performance)
      -> Return Result.Success(pagedResult)
```

### Key Rules

- **Audit logs are append-only** — never UPDATE or DELETE (compliance requirement).
- **Partitioned by month** via pg_partman for query performance.
- **Always include correlation_id** for request tracing across services.

## Related

- [[audit-logging|Overview]]
- [[authentication]]
- [[authorization]]
- [[gdpr-consent]]
- [[event-catalog]]
- [[error-handling]]
- [[logging-standards]]
