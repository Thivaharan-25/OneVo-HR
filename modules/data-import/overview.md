# Module: DataImport

**Namespace:** `ONEVO.Modules.DataImport`
**Phase:** 1 — Build
**Pillar:** HR Management
**Owner:** Dev 1
**Tables:** 1
**Task File:** [[current-focus/DEV1-hr-import-onboarding|DEV1: HR Import Onboarding]]

---

## Purpose

Bulk employee and org-structure import for new tenants. Instead of creating employees one-by-one, HR admins upload a CSV or Excel file — or connect a PeopleHR account — and the module guides them through a 7-step wizard: source selection, file upload or API connection, field mapping, job grouping, ETL validation, confirmation, and a reconciliation spot-check on completion.

A background Hangfire job handles the heavy lifting: it downloads the uploaded file from Railway S3-compatible blob storage, runs ETL transformations (date normalisation, E.164 phone, decimal salary), validates rows, and bulk-writes employees into the `employees` table owned by [[modules/core-hr/overview|CoreHR]].

---

## Dependencies

| Direction      | Module                                                        | Interface                    | Purpose                                                       |
| :------------- | :------------------------------------------------------------ | :--------------------------- | :------------------------------------------------------------ |
| **Depends on** | [[modules/core-hr/overview\|CoreHR]]                          | `employees` table            | Bulk-writes imported employee records                         |
| **Depends on** | [[modules/org-structure/overview\|OrgStructure]]              | `IDepartmentResolver`        | Resolves department and job-family names during ETL transform |
| **Depends on** | [[modules/auth/overview\|Auth]]                               | `employees:write` permission | Permission gate on all import endpoints                       |
| **Depends on** | [[infrastructure/file-storage\|Infrastructure / FileStorage]] | `IImportFileStorage`         | Railway S3-compatible blob storage for uploaded files         |

---

## Public Interface

```csharp
public interface IImportFileStorage
{
    Task<UploadUrlResult> GenerateUploadUrlAsync(string tenantId, string filename, CancellationToken ct = default);
    Task<Stream> DownloadFileAsync(string fileKey, CancellationToken ct = default);
    Task DeleteFileAsync(string fileKey, CancellationToken ct = default);
    Task<bool> FileExistsAsync(string fileKey, CancellationToken ct = default);
}

public record UploadUrlResult(string UploadUrl, string FileKey, DateTime ExpiresAt);
```

---

## Database Tables (1)

### `migration_runs`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | Tenant-scoped |
| `initiated_by_user_id` | `uuid` | FK → users |
| `source` | `varchar(20)` | `CSV`, `Excel`, `PeopleHR` |
| `file_key` | `varchar(500)` | S3 object key; null for PeopleHR runs |
| `status` | `varchar(20)` | `Pending`, `Processing`, `Completed`, `Failed` |
| `total_rows` | `int` | Set after file parse |
| `processed_rows` | `int` | Updated by background job |
| `success_rows` | `int` | |
| `failed_rows` | `int` | |
| `skipped_rows` | `int` | User-skipped validation errors |
| `created_at` | `timestamptz` | |
| `completed_at` | `timestamptz` | Null until terminal state |

Factory: `MigrationRun.Create(tenantId, userId, source, fileKey)`
Methods: `UpdateProgress(processed, success, failed, skipped)`, `Complete()`

---

## Key Business Rules

1. **Source branching** — CSV and Excel follow the upload path (Step 2a). PeopleHR skips Step 2a and goes to Step 2b (API key entry). The wizard Zustand store manages this via `method` state.
2. **Pre-signed upload** — files are PUT directly from the browser to Railway S3 using a 1-hour pre-signed URL. The server never proxies file bytes.
3. **ETL normalisation** — `EtlTransformService` normalises all dates to ISO-8601, phone numbers to E.164, and salary to decimal. Rows with unresolvable errors are marked `failed`; rows with warnings may be skipped in Step 5.
4. **Fuzzy field mapping** — `FieldMappingService` auto-suggests canonical HR field mappings using alias matching (e.g. `"DOB"` → `birth_date`, `"First Name"` → `first_name`). Users can override in the Step 3 table.
5. **Background isolation** — import processing runs entirely in a Hangfire background job. The API returns `migrationRunId` immediately; the frontend polls `GET /api/v1/migration/runs/{id}/progress` every 1.5 s until `Completed` or `Failed`.
6. **Reconciliation spot-check** — on completion, `ReconciliationService` randomly samples 10–15 imported records for human verification in Step 7. Display-only — not a rollback mechanism.
7. **File retention** — `ImportFileCleanupJob` (Hangfire recurring) deletes S3 files for `Completed` or `Failed` runs older than 7 days.

---

## Backend Components

| Component | Responsibility |
|:----------|:--------------|
| `MigrationRun` entity | Domain aggregate tracking run lifecycle and row counts |
| `DataImportDbContext` | EF Core context owning `migration_runs` |
| `IImportFileStorage` / `S3ImportFileStorage` | Pre-signed URL generation, file download, deletion — backed by Railway S3 |
| `EtlTransformService` | `RawImportRow` → `TransformedRow`; date/phone/salary normalisation + duplicate detection |
| `FieldMappingService` | Auto-maps source column headers to canonical HR fields; returns `ColumnMappingResult` list |
| `IHrSystemAdapter` / `PeopleHrAdapter` | Fetches employees from PeopleHR REST API → `IReadOnlyList<RawImportRow>` |
| `ImportController` | Four REST endpoints; permission-gated with `employees:write` |
| `ImportBackgroundJob` | Hangfire job: download → ETL → validate → bulk write → update run |
| `ReconciliationService` | Samples 10–15 records post-import for spot-check display |
| `ImportFileCleanupJob` | Hangfire recurring job; deletes stale S3 files after 7 days |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| `POST` | `/api/v1/migration/upload-url` | `employees:write` | Generate pre-signed S3 upload URL (1-hour expiry) |
| `POST` | `/api/v1/migration/analyse` | `employees:write` | Parse file headers + first row; return column mapping suggestions |
| `POST` | `/api/v1/migration/bulk-import` | `employees:write` | Create `MigrationRun`, enqueue Hangfire job, return `migrationRunId` |
| `GET` | `/api/v1/migration/runs/{id}/progress` | `employees:write` | Poll run status + row counts |

---

## Wizard Steps

| Step | Name | Frontend Component | Description |
|:-----|:-----|:------------------|:------------|
| 1 | Choose Method | `Step1ChooseMethod` | Select CSV, Excel, or PeopleHR |
| 2a | Upload File | `Step2aUploadFile` | Drag-drop upload; PUT directly to pre-signed S3 URL |
| 2b | Connect PeopleHR | `Step2bConnectPeopleHR` | API key entry with masked display |
| 3 | Map Fields | `Step3FieldMapping` / `FieldMappingTable` | Editable dropdowns; source columns → canonical HR fields |
| 4 | Job Grouping | `Step4JobGrouping` | Assign department and job family to row groups |
| 5 | Validate | `Step5Validation` | Review ETL errors/warnings; skip or fix rows |
| 6 | Confirm | `Step6ConfirmImport` | Summary counts; triggers `POST /api/v1/migration/bulk-import` |
| 7 | Done | `Step7Done` | Reconciliation spot-check list + success summary |

---

## Frontend Components

| Component / Hook | Path | Responsibility |
|:-----------------|:-----|:--------------|
| `useImportWizard` | `hr/import/_hooks/useImportWizard.ts` | Zustand state machine: `currentStep`, `method`, `fileKey`, `columnMappings`, `migrationRunId` |
| `ImportWizard` | `hr/import/_components/ImportWizard.tsx` | Wizard shell with 7-step progress bar |
| `Step1–7` components | `hr/import/_components/steps/` | One component per wizard step |
| `FieldMappingTable` | `hr/import/_components/FieldMappingTable.tsx` | Editable source → canonical field mapping table with sample values |
| `fieldTypeDetector.ts` | `hr/import/_lib/fieldTypeDetector.ts` | Detects field type from sample value (date, email, phone, salary, text) |
| `useImportProgress` | `hr/import/_hooks/useImportProgress.ts` | Polls `/api/v1/migration/runs/{id}/progress` every 1.5 s |
| `IntegrationCard` | `settings/integrations/_components/IntegrationCard.tsx` | Status badge, masked API key, last import date/count |
| Integrations page | `settings/integrations/page.tsx` | Grid of `IntegrationCard` components (PeopleHR + future integrations) |

---

## Related

- [[modules/core-hr/overview|CoreHR]] — `employees` table target for bulk writes
- [[modules/org-structure/overview|OrgStructure]] — department and job-family resolution during ETL
- [[modules/auth/overview|Auth]] — `employees:write` permission
- [[backend/module-catalog|Module Catalog]]
- [[current-focus/DEV1-hr-import-onboarding|DEV1: HR Import Onboarding]] — task file with acceptance criteria
- [[docs/superpowers/plans/2026-04-24-hr-import-onboarding|Implementation Plan]] — phased build plan (Phase A backend + Phase B frontend)
