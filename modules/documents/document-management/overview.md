# Document Management

**Module:** Documents  
**Feature:** Document Management

---

## Purpose

Document metadata, versioning, and storage. Files stored in blob storage via `IFileService`, only metadata in PostgreSQL.

## Database Tables

### `documents`
Key columns: `category_id`, `employee_id` (nullable for company-wide), `title`, `requires_acknowledgement`, `is_active`.

### `document_versions`
Version history: `version_number` (auto-incremented), `blob_storage_url`, `file_name`, `effective_date`, `expiry_date`, `is_current`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/documents` | `documents:read` | List documents |
| POST | `/api/v1/documents` | `documents:write` | Upload document |
| GET | `/api/v1/documents/{id}` | `documents:read` | Download document |
| GET | `/api/v1/documents/{id}/versions` | `documents:read` | Version history |
| POST | `/api/v1/documents/{id}/versions` | `documents:write` | Upload new version |

## Related

- [[modules/documents/overview|Documents Module]]
- [[frontend/architecture/overview|Categories]]
- [[frontend/architecture/overview|Access Control]]
- [[frontend/architecture/overview|Acknowledgements]]
- [[frontend/architecture/overview|Templates]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/data-classification|Data Classification]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]]
