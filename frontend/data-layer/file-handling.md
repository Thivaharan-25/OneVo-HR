# File Handling

## File Operations in ONEVO

| Feature | Operation | Files |
|:--------|:----------|:------|
| Employee Documents | Upload, download, preview | PDF, DOCX, images |
| Profile Photos | Upload, crop | JPEG, PNG, WebP |
| Payroll Reports | Download, export | PDF, XLSX, CSV |
| Identity Verification | Upload | JPEG, PNG, PDF |
| Expense Receipts | Upload, preview | JPEG, PNG, PDF |
| Data Import | Upload | CSV, XLSX |
| Data Export | Download | CSV, XLSX, PDF |

## Upload Architecture

### Flow

```
User selects file(s)
    │
    ├── Client-side validation (size, type, dimensions)
    │
    ├── Request presigned upload URL from API
    │   POST /api/v1/files/upload-url
    │   Body: { fileName, contentType, category }
    │   Response: { uploadUrl, fileId, expiresAt }
    │
    ├── Upload directly to blob storage (Azure Blob / S3)
    │   PUT {uploadUrl}
    │   Body: file binary
    │   Headers: Content-Type, x-ms-blob-type
    │
    ├── Confirm upload with API
    │   POST /api/v1/files/{fileId}/confirm
    │   Triggers: virus scan, metadata extraction
    │
    └── Poll for processing status (or receive SignalR push)
        GET /api/v1/files/{fileId}/status
        Response: { status: 'scanning' | 'ready' | 'rejected', reason? }
```

### Upload Component

```tsx
function FileUpload({ category, accept, maxSize, onComplete }: FileUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const requestUploadUrl = useRequestUploadUrl();
  const confirmUpload = useConfirmUpload();

  async function handleFiles(files: FileList) {
    const file = files[0];

    // Client-side validation
    if (file.size > maxSize) {
      toast.error(`File too large. Max ${formatBytes(maxSize)}.`);
      return;
    }

    setUploading(true);
    try {
      // 1. Get presigned URL
      const { uploadUrl, fileId } = await requestUploadUrl.mutateAsync({
        fileName: file.name,
        contentType: file.type,
        category,
      });

      // 2. Upload to storage with progress tracking
      await uploadWithProgress(uploadUrl, file, setProgress);

      // 3. Confirm with API
      await confirmUpload.mutateAsync(fileId);

      onComplete({ fileId, fileName: file.name });
    } catch (error) {
      toast.error('Upload failed');
    } finally {
      setUploading(false);
      setProgress(0);
    }
  }

  return (
    <div
      className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer hover:border-primary/50 transition-colors"
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => { e.preventDefault(); handleFiles(e.dataTransfer.files); }}
      onClick={() => inputRef.current?.click()}
    >
      {uploading ? (
        <div className="space-y-2">
          <Loader2 className="h-8 w-8 mx-auto animate-spin text-muted-foreground" />
          <Progress value={progress} className="w-48 mx-auto" />
          <p className="text-sm text-muted-foreground">{progress}%</p>
        </div>
      ) : (
        <>
          <Upload className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
          <p className="text-sm">Drop file here or click to browse</p>
          <p className="text-xs text-muted-foreground mt-1">
            {accept} — Max {formatBytes(maxSize)}
          </p>
        </>
      )}
      <input ref={inputRef} type="file" accept={accept} hidden onChange={(e) => handleFiles(e.target.files!)} />
    </div>
  );
}
```

## Download Architecture

### Secure Download

Files are accessed via time-limited signed URLs:

```tsx
function useFileDownload() {
  return useMutation({
    mutationFn: async (fileId: string) => {
      // Get signed download URL
      const { downloadUrl, fileName } = await api.files.getDownloadUrl(fileId);

      // Trigger browser download
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = fileName;
      link.click();
    },
  });
}
```

### Report Export

For server-generated reports (PDF, Excel):

```tsx
function useExportReport() {
  return useMutation({
    mutationFn: async ({ reportType, filters, format }: ExportParams) => {
      // Request report generation
      const { jobId } = await api.reports.requestExport({ reportType, filters, format });

      // Poll for completion (or use SignalR)
      const result = await pollUntilReady(`/api/v1/reports/exports/${jobId}`);

      // Download
      window.open(result.downloadUrl, '_blank');
    },
  });
}
```

## File Preview

### In-App Preview

| Type | Preview Method |
|:-----|:---------------|
| Images (JPEG, PNG, WebP) | `<img>` with signed URL |
| PDF | Embedded `<iframe>` or `react-pdf` |
| DOCX | Server-side PDF conversion → `<iframe>` |
| CSV/XLSX | Parse client-side → render in DataTable |

```tsx
function FilePreviewDialog({ file }: { file: FileMetadata }) {
  const { data: previewUrl } = useFilePreviewUrl(file.id);

  return (
    <Dialog>
      <DialogContent className="max-w-4xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle>{file.name}</DialogTitle>
        </DialogHeader>
        {file.contentType.startsWith('image/') && (
          <img src={previewUrl} alt={file.name} className="max-h-[60vh] object-contain mx-auto" />
        )}
        {file.contentType === 'application/pdf' && (
          <iframe src={previewUrl} className="w-full h-[60vh]" />
        )}
      </DialogContent>
    </Dialog>
  );
}
```

## Validation Rules

| Category | Max Size | Allowed Types | Max Files |
|:---------|:---------|:--------------|:----------|
| Profile photo | 5MB | JPEG, PNG, WebP | 1 |
| Employee document | 25MB | PDF, DOCX, XLSX, images | 10 per upload |
| Identity verification | 10MB | JPEG, PNG, PDF | 3 |
| Expense receipt | 10MB | JPEG, PNG, PDF | 5 |
| Data import | 50MB | CSV, XLSX | 1 |

## Security

- All uploads go through presigned URLs — the frontend never holds storage credentials
- Files are virus-scanned before being marked as `ready`
- Download URLs are time-limited (15 min) and scoped to the tenant
- Sensitive documents (salary, medical) require additional permission check for download

## Related

- [[frontend/data-layer/api-integration|Api Integration]] — API client patterns
- [[frontend/design-system/patterns/form-patterns|Form Patterns]] — file upload in forms
- [[frontend/cross-cutting/security|Security]] — file upload security
