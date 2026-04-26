# File Storage

**Provider:** Railway S3-compatible blob storage (production), local disk (development)

---

## Purpose

Provides file upload, download, and deletion for tenant-scoped files. Used by the DataImport module for uploaded CSV/Excel files, and any other module requiring blob storage.

## Interface

```csharp
public interface IImportFileStorage
{
    Task<UploadUrlResult> GenerateUploadUrlAsync(string tenantId, string filename, CancellationToken ct = default);
    Task<Stream> DownloadFileAsync(string fileKey, CancellationToken ct = default);
    Task DeleteFileAsync(string fileKey, CancellationToken ct = default);
    Task<bool> FileExistsAsync(string fileKey, CancellationToken ct = default);
}
```

## Configuration

| Environment | Provider | Notes |
|:------------|:---------|:------|
| Development | Local disk (`/tmp/onevo-uploads/`) | Configured via `FileStorageOptions.UseLocalDisk = true` |
| Production | Railway S3-compatible (MinIO-compatible API) | Credentials via environment variables |

Environment variables (production):
- `STORAGE_ENDPOINT` — S3-compatible endpoint URL
- `STORAGE_BUCKET` — Bucket name
- `STORAGE_ACCESS_KEY` — Access key
- `STORAGE_SECRET_KEY` — Secret key

## File Key Convention

`{tenantId}/{module}/{yyyy-MM}/{uuid}.{ext}`

Example: `a1b2c3/data-import/2026-04/f7e8d9-employees.csv`

## Related

- [[modules/data-import/overview|DataImport]] — primary consumer (CSV/Excel import files)
- [[infrastructure/environment-parity|Environment Parity]] — local vs production configuration
- [[infrastructure/multi-tenancy|Multi Tenancy]] — files are tenant-scoped by prefix
