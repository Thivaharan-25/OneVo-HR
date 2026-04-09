# File Management — End-to-End Logic

**Module:** Infrastructure
**Feature:** File Management

---

## Upload File

### Flow

```
POST /api/v1/files/upload
  -> FileController.Upload(IFormFile file)
    -> [Authenticated]
    -> FileService.UploadFileAsync(stream, fileName, contentType, ct)
      -> 1. Validate file size (max 50MB)
      -> 2. Validate content type (whitelist: pdf, docx, xlsx, png, jpg)
      -> 3. Generate unique storage path: {tenant_id}/{year}/{month}/{uuid}.{ext}
      -> 4. Upload to blob storage (Railway/S3)
      -> 5. INSERT into file_records
         -> file_name, content_type, size_bytes, storage_path
      -> Return Result.Success(fileRecordDto)
```

## Download File

### Flow

```
GET /api/v1/files/{id}
  -> FileController.Download(id)
    -> [Authenticated]
    -> FileService.DownloadFileAsync(fileId, ct)
      -> 1. Load file_records by id
      -> 2. Verify tenant_id matches caller's tenant
      -> 3. Generate signed URL or stream from blob storage
      -> Return file stream
```

### Key Rules

- **Files stored in blob storage, not database.** Only metadata in `file_records`.
- **Tenant isolation:** Files are partitioned by tenant_id in storage path.

## Related

- [[modules/infrastructure/file-management/overview|Overview]]
- [[modules/infrastructure/tenant-management/overview|Tenant Management]]
- [[modules/infrastructure/user-management/overview|User Management]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
