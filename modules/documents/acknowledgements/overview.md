# Document Acknowledgements

**Module:** Documents  
**Feature:** Acknowledgements

---

## Purpose

Tracks employee acknowledgement of documents that require it. Supports click and e-signature methods.

## Database Tables

### `document_acknowledgements`
Fields: `document_version_id`, `employee_id`, `acknowledged_by_id`, `method` (`click`, `e_signature`), `acknowledged_at`, `ip_address`.

## Related

- [[modules/documents/overview|Documents Module]]
- [[frontend/architecture/overview|Document Management]]
- [[frontend/architecture/overview|Access Control]]
- [[frontend/architecture/overview|Categories]]
- [[frontend/architecture/overview|Templates]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/data-classification|Data Classification]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]]
