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

- [[documents|Documents Module]]
- [[documents/document-management/overview|Document Management]]
- [[documents/acknowledgements/overview|Acknowledgements]]
- [[documents/categories/overview|Categories]]
- [[documents/templates/overview|Templates]]
- [[auth-architecture]]
- [[data-classification]]
- [[multi-tenancy]]
- [[event-catalog]]
- [[WEEK4-supporting-bridges]]
