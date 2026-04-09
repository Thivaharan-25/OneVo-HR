# Access Control & Audit

**Module:** Documents  
**Feature:** Access Control

---

## Purpose

Audit trail of who accessed which document versions.

## Database Tables

### `document_access_logs`
Fields: `document_version_id`, `employee_id`, `action` (`view`, `download`, `print`), `accessed_at`, `ip_address`.

## Related

- [[modules/documents/overview|Documents Module]]
- [[frontend/architecture/overview|Document Management]]
- [[frontend/architecture/overview|Acknowledgements]]
- [[frontend/architecture/overview|Categories]]
- [[frontend/architecture/overview|Templates]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/data-classification|Data Classification]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]]
