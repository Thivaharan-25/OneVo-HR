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

- [[documents|Documents Module]]
- [[documents/document-management/overview|Document Management]]
- [[documents/access-control/overview|Access Control]]
- [[documents/categories/overview|Categories]]
- [[documents/templates/overview|Templates]]
- [[auth-architecture]]
- [[data-classification]]
- [[multi-tenancy]]
- [[event-catalog]]
- [[WEEK4-supporting-bridges]]
