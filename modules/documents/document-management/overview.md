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

- [[documents|Documents Module]]
- [[documents/categories/overview|Categories]]
- [[documents/access-control/overview|Access Control]]
- [[documents/acknowledgements/overview|Acknowledgements]]
- [[documents/templates/overview|Templates]]
- [[auth-architecture]]
- [[data-classification]]
- [[multi-tenancy]]
- [[event-catalog]]
- [[WEEK4-supporting-bridges]]
