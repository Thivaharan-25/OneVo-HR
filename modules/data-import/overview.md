# Module: DataImport

**Namespace:** `ONEVO.Modules.DataImport`  
**Phase:** 1 - Build  
**Pillar:** HR Management  
**Owner:** Dev 1  
**Tables:** `migration_runs` plus PeopleHR staging/audit tables  
**Task File:** [[current-focus/DEV1-hr-import-onboarding|DEV1: HR Import Onboarding]]

---

## Purpose

Bulk employee, org-structure, and HR history migration for new tenants. Instead of creating employees one-by-one, HR admins upload a CSV or Excel file, or connect a PeopleHR account, and the module guides them through source selection, file upload or API connection, field mapping, job grouping, ETL validation, confirmation, and reconciliation before commit.

CSV and Excel imports focus on employee/profile rows. PeopleHR imports use the full migration pipeline in [[modules/data-import/peoplehr-full-migration|PeopleHR Full Migration]]: raw API records are staged first, API permissions are preflighted, source fields are mapped to canonical ONEVO modules, and unmapped records are retained as raw archive instead of being silently dropped.

A background Hangfire job handles the heavy lifting: it downloads uploaded files from Railway S3-compatible blob storage or reads staged PeopleHR records, runs ETL transformations, validates rows, and bulk-writes approved records into canonical module tables owned by CoreHR, OrgStructure, Leave, Payroll, Documents, Skills, Performance, WorkforcePresence, and related modules.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/core-hr/overview|CoreHR]] | `employees` and profile tables | Bulk-writes imported employee records. |
| **Depends on** | [[modules/org-structure/overview|OrgStructure]] | `IDepartmentResolver` and org resolvers | Resolves department, job-family, legal entity, location, and manager references. |
| **Depends on** | [[modules/auth/overview|Auth]] | `employees:write` permission | Permission gate on all import endpoints. |
| **Depends on** | [[infrastructure/file-storage|Infrastructure / FileStorage]] | `IImportFileStorage` | Railway S3-compatible blob storage for uploaded files. |
| **Depends on** | [[modules/leave/overview|Leave]] | Leave entitlement/request tables | Imports PeopleHR leave, holiday, absence, sickness, maternity, and paternity records. |
| **Depends on** | [[modules/payroll/overview|Payroll]] | Compensation/payroll tables | Imports salary, pay history, payroll identifiers, and benefits where mapped. |
| **Depends on** | [[modules/documents/overview|Documents]] | Documents and versions | Imports PeopleHR document metadata and retryable file downloads. |
| **Depends on** | [[modules/skills/overview|Skills]] | Skills/qualifications tables | Imports training, CPD, qualifications, and certifications. |
| **Depends on** | [[modules/performance/overview|Performance]] | Review/appraisal tables | Imports appraisal and review data where templates can be mapped. |

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

## Database Tables

### `migration_runs`

Tracks CSV/Excel imports and high-level import progress.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | Tenant-scoped |
| `initiated_by_user_id` | `uuid` | FK -> users |
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

### PeopleHR staging and audit tables

Full PeopleHR migration also uses the staging and audit tables defined in [[modules/data-import/peoplehr-full-migration#staging-tables|PeopleHR Full Migration]]:

- `peoplehr_migration_runs`
- `peoplehr_raw_records`
- `peoplehr_mapping_profiles`
- `peoplehr_mapping_results`
- `peoplehr_external_id_links`
- `peoplehr_validation_errors`
- `peoplehr_reconciliation_items`

---

## Key Business Rules

1. **Source branching** - CSV and Excel follow the upload path. PeopleHR skips file upload, stores encrypted API credentials, and runs API permission preflight before fetch.
2. **Pre-signed upload** - CSV/Excel files are PUT directly from the browser to Railway S3 using a 1-hour pre-signed URL. The server never proxies file bytes.
3. **Raw-first PeopleHR import** - PeopleHR responses are written to `peoplehr_raw_records` before transformation. Unmapped or unsupported fields are archived raw and reported.
4. **ETL normalisation** - `EtlTransformService` normalises dates to ISO-8601, phone numbers to E.164, salary to decimal, and enums to canonical ONEVO values.
5. **Fuzzy field mapping** - `FieldMappingService` auto-suggests canonical HR mappings using alias matching, and users can override mappings in the wizard.
6. **Deterministic identity matching** - PeopleHR employee id/external id, work email, employee number, and admin-approved review candidates are used in that order.
7. **Dry-run before commit** - PeopleHR migrations must support dry-run, commit, rollback, and resume. Commit is blocked while blocking validation errors are open.
8. **No silent data loss** - every PeopleHR source record receives `Imported`, `NeedsReview`, `ArchivedRaw`, `SkippedByAdmin`, or `Failed`.
9. **Background isolation** - import processing runs in Hangfire. The API returns a migration run id immediately, and the frontend polls progress until a terminal state.
10. **Reconciliation** - PeopleHR dry-run reconciliation shows counts, missing API areas, duplicate candidates, unmapped fields, and spot-check samples before commit.
11. **File retention** - `ImportFileCleanupJob` deletes S3 files for completed or failed CSV/Excel runs older than 7 days.

---

## Backend Components

| Component | Responsibility |
|:----------|:---------------|
| `MigrationRun` entity | Domain aggregate tracking run lifecycle and row counts. |
| `DataImportDbContext` | EF Core context owning `migration_runs` and PeopleHR migration tables. |
| `IImportFileStorage` / `S3ImportFileStorage` | Pre-signed URL generation, file download, and deletion. |
| `EtlTransformService` | `RawImportRow` -> `TransformedRow`; date/phone/salary normalization and duplicate detection. |
| `FieldMappingService` | Auto-maps source fields to canonical HR fields and stores mapping results. |
| `IHrSystemAdapter` / `PeopleHrAdapter` | Coordinates PeopleHR API fetchers and writes raw staged records. |
| `PeopleHrPreflightService` | Tests API key access for selected PeopleHR areas before migration. |
| `PeopleHr*Fetcher` components | Fetch employees, org data, salary, leave, timesheets, documents, training, benefits, appraisals, and custom screens. |
| `ImportController` | REST endpoints permission-gated with `employees:write`. |
| `ImportBackgroundJob` | Hangfire job: fetch/download -> stage -> ETL -> validate -> reconcile -> commit. |
| `ReconciliationService` | Builds dry-run reconciliation counts, review items, and spot-check samples. |
| `ImportFileCleanupJob` | Hangfire recurring job; deletes stale S3 files after 7 days. |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| `POST` | `/api/v1/migration/upload-url` | `employees:write` | Generate pre-signed S3 upload URL. |
| `POST` | `/api/v1/migration/analyse` | `employees:write` | Parse file headers or staged PeopleHR samples; return mapping suggestions. |
| `POST` | `/api/v1/migration/bulk-import` | `employees:write` | Create migration run, enqueue Hangfire job, return run id. |
| `GET` | `/api/v1/migration/runs/{id}/progress` | `employees:write` | Poll run status and row counts. |
| `POST` | `/api/v1/migration/peoplehr/preflight` | `employees:write` | Check selected PeopleHR API areas before migration. |
| `POST` | `/api/v1/migration/peoplehr/{id}/commit` | `employees:write` | Commit approved dry-run mappings. |
| `POST` | `/api/v1/migration/peoplehr/{id}/rollback` | `employees:write` | Roll back records created by a committed run where safe. |
| `POST` | `/api/v1/migration/peoplehr/{id}/resume` | `employees:write` | Resume from the last completed migration stage. |

---

## Wizard Steps

| Step | Name             | Frontend Component                        | Description                                                              |
| :--- | :--------------- | :---------------------------------------- | :----------------------------------------------------------------------- |
| 1    | Choose Method    | `Step1ChooseMethod`                       | Select CSV, Excel, or PeopleHR.                                          |
| 2a   | Upload File      | `Step2aUploadFile`                        | Drag-drop upload; PUT directly to pre-signed S3 URL.                     |
| 2b   | Connect PeopleHR | `Step2bConnectPeopleHR`                   | API key entry with masked display and API permission preflight.          |
| 3    | Map Fields       | `Step3FieldMapping` / `FieldMappingTable` | Editable dropdowns; source fields/custom screens -> canonical HR fields. |
| 4    | Job Grouping     | `Step4JobGrouping`                        | Assign department, legal entity, job family, and location to row groups. |
| 5    | Validate         | `Step5Validation`                         | Review ETL errors/warnings; skip, fix, or accept raw archive.            |
| 6    | Confirm          | `Step6ConfirmImport`                      | Summary counts; triggers dry-run or import job.                          |
| 7    | Done             | `Step7Done`                               | Reconciliation spot-check list, final counts, and audit report.          |

PeopleHR full migration extends these steps with dry-run reconciliation, admin approval, commit, rollback, resume, and final audit report as defined in [[modules/data-import/peoplehr-full-migration|PeopleHR Full Migration]].

---

## Frontend Components

| Component / Hook | Path | Responsibility |
|:-----------------|:-----|:---------------|
| `useImportWizard` | `hr/import/_hooks/useImportWizard.ts` | Zustand state machine: current step, method, file key, mappings, and migration run id. |
| `ImportWizard` | `hr/import/_components/ImportWizard.tsx` | Wizard shell with progress bar. |
| `Step1-7` components | `hr/import/_components/steps/` | One component per wizard step. |
| `FieldMappingTable` | `hr/import/_components/FieldMappingTable.tsx` | Editable source -> canonical field mapping table with sample values. |
| `fieldTypeDetector.ts` | `hr/import/_lib/fieldTypeDetector.ts` | Detects field type from sample value. |
| `useImportProgress` | `hr/import/_hooks/useImportProgress.ts` | Polls progress every 1.5 seconds. |
| `PeopleHrPreflightPanel` | `hr/import/_components/PeopleHrPreflightPanel.tsx` | Shows available, denied, and unselected PeopleHR API areas. |
| `PeopleHrReconciliationDashboard` | `hr/import/_components/PeopleHrReconciliationDashboard.tsx` | Shows dry-run counts, review items, and commit readiness. |
| `IntegrationCard` | `settings/integrations/_components/IntegrationCard.tsx` | Status badge, masked API key, last import date/count. |
| Integrations page | `settings/integrations/page.tsx` | Grid of `IntegrationCard` components, including PeopleHR. |

---

## Related

- [[Userflow/Data-Import/data-import-wizard|Data Import Wizard]] - end-to-end HR admin import flow
- [[modules/data-import/peoplehr-full-migration|PeopleHR Full Migration]] - raw-first, auditable PeopleHR migration design
- [[modules/core-hr/overview|CoreHR]] - employee table target for bulk writes
- [[modules/org-structure/overview|OrgStructure]] - department and job-family resolution during ETL
- [[modules/auth/overview|Auth]] - `employees:write` permission
- [[backend/module-catalog|Module Catalog]]
- [[current-focus/DEV1-hr-import-onboarding|DEV1: HR Import Onboarding]]
- [[docs/superpowers/plans/2026-04-24-hr-import-onboarding|Implementation Plan]]
