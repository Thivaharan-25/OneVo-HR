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

- [[infrastructure|Infrastructure Module]]
- [[reference-data]]
- [[tenant-management]]
- [[user-management]]
- [[multi-tenancy]]
- [[authorization]]
- [[error-handling]]
- [[migration-patterns]]
- [[WEEK1-infrastructure-setup]]
