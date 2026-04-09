# Document Management — End-to-End Logic

**Module:** Documents
**Feature:** Document Management

---

## Upload Document

### Flow

```
POST /api/v1/documents
  -> DocumentController.Upload(UploadDocumentCommand, IFormFile file)
    -> [RequirePermission("documents:write")]
    -> DocumentService.UploadAsync(command, file, ct)
      -> 1. Validate category_id exists and is active
      -> 2. Upload file to blob storage via IFileService.UploadFileAsync()
         -> Returns file_record_id
      -> 3. INSERT into documents table
         -> category_id, employee_id (nullable for company-wide), title
      -> 4. INSERT into document_versions
         -> version_number = 1, is_current = true
         -> blob_storage_url, file_name, effective_date
      -> 5. If requires_acknowledgement = true:
         -> Schedule acknowledgement notifications
      -> Return Result.Success(documentDto) with 201 Created
```

## Download Document

### Flow

```
GET /api/v1/documents/{id}
  -> DocumentController.Download(id)
    -> [RequirePermission("documents:read")]
    -> DocumentService.DownloadAsync(id, ct)
      -> 1. Load document + current version (is_current = true)
      -> 2. Check access: company-wide OR employee's own OR admin
      -> 3. Log access: INSERT into document_access_logs (action = 'download')
      -> 4. Get file from blob storage via IFileService.DownloadFileAsync()
      -> Return file stream with content-type header
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| File upload failure | Return 500, rollback document insert |
| Document not found | Return 404 |
| Access denied (not owner/admin) | Return 403 |
| Category inactive | Return 422 "Category is not active" |

## Related

- [[frontend/architecture/overview|Document Management Overview]]
- [[frontend/architecture/overview|Categories]]
- [[frontend/architecture/overview|Access Control]]
- [[frontend/architecture/overview|Acknowledgements]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
