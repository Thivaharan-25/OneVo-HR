# File Management

**Module:** Infrastructure  
**Feature:** File Management

---

## Purpose

File upload/download service. Metadata in PostgreSQL, files in blob storage (Railway/S3).

## Database Tables

### `file_records`
Key columns: `file_name`, `content_type` (MIME), `size_bytes`, `storage_path`, `uploaded_by_id`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/files/upload` | Authenticated | Upload file |
| GET | `/api/v1/files/{id}` | Authenticated | Download file |

## Related

- [[modules/infrastructure/overview|Infrastructure Module]]
- [[modules/infrastructure/reference-data/overview|Reference Data]]
- [[modules/infrastructure/tenant-management/overview|Tenant Management]]
- [[modules/infrastructure/user-management/overview|User Management]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[backend/messaging/error-handling|Error Handling]]
- [[database/migration-patterns|Migration Patterns]]
- [[current-focus/DEV1-infrastructure-setup|DEV1: Infrastructure]]
