# File Storage

**Provider:** Cloudflare R2 object storage in production, local disk in development.

---

## Purpose

Provides upload, download, signed-access, and deletion for tenant-scoped files. ONEVO stores file metadata in PostgreSQL `file_records`; binary content lives in Cloudflare R2.

`file_records` is only the storage metadata source. Normal display assets and attachments link through `entity_assets`. Monitoring screenshots link through `monitoring_evidence_assets`; identity verification camera photos and clock-in/out evidence link through `verification_evidence_assets` so retention, legal hold, and view/download audit rules are enforced by the owning module.

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
| Production | Cloudflare R2 object storage | S3-compatible credentials managed through System Config / platform service keys |

Environment variables or encrypted service-key fields:
- `R2_ENDPOINT` - Cloudflare R2 S3-compatible endpoint URL
- `R2_BUCKET` - Bucket name
- `R2_ACCESS_KEY_ID` - Access key ID
- `R2_SECRET_ACCESS_KEY` - Secret access key

## File Key Convention

`{tenantId}/{module}/{yyyy-MM}/{uuid}.{ext}`

Example: `a1b2c3/data-import/2026-04/f7e8d9-employees.csv`

## Related

- [[modules/data-import/overview|DataImport]] - CSV/Excel import files
- [[modules/infrastructure/file-management/overview|File Management]] - canonical file metadata and R2 access
- [[infrastructure/environment-parity|Environment Parity]] - local vs production configuration
- [[infrastructure/multi-tenancy|Multi Tenancy]] - files are tenant-scoped by prefix
