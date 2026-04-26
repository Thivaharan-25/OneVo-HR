# Task: HR Import Onboarding — Bulk Employee Import Wizard

**Assignee:** Dev 1
**Module:** DataImport
**Priority:** High
**Dependencies:** [[current-focus/DEV1-core-hr-profile|DEV1 Core HR Profile]], [[current-focus/DEV2-auth-security|DEV2 Auth & Security]] (RBAC + `employees:write` permission must exist), [[current-focus/DEV3-org-structure|DEV3 Org Structure]] (departments + job families needed for ETL field resolution)

---

## Overview

Build a guided 7-step import wizard allowing new tenants to bulk-import employees + org structure from CSV/Excel files or PeopleHR API — replacing manual one-by-one employee creation.

**Plan:** [[docs/superpowers/plans/2026-04-24-hr-import-onboarding|Implementation Plan (2026-04-24)]]
**Module docs:** [[modules/data-import/overview|DataImport Module Overview]]

> ⚠️ The design spec references BullMQ (Node.js) and Cloudflare R2 — ignore both. Use **Hangfire** for background jobs and **Railway S3-compatible blob storage** (`IImportFileStorage`) instead.

---

## Step 1: Backend (Phase A — Tasks 1–7)

### Acceptance Criteria

**Task 1 — Database Migration**
- [ ] EF Core migration creates `migration_runs` table (see [[modules/data-import/overview|schema]])
- [ ] `MigrationRun` domain entity with `Create`, `UpdateProgress`, `Complete` methods
- [ ] `DataImportDbContext` wires up the `MigrationRuns` DbSet

**Task 2 — File Storage**
- [ ] `IImportFileStorage` interface implemented by `S3ImportFileStorage`
- [ ] `GenerateUploadUrlAsync` returns a 1-hour pre-signed URL + `FileKey`
- [ ] `DownloadFileAsync`, `DeleteFileAsync`, `FileExistsAsync` all functional
- [ ] Registered in DI; `S3Options` read from config (Railway endpoint, bucket, credentials)

**Task 3 — ETL Transform Service**
- [ ] `EtlTransformService` converts `RawImportRow` → `TransformedRow`
- [ ] Dates normalised to ISO-8601; phones to E.164; salary to `decimal`
- [ ] Duplicate detection within the batch (flag, don't drop)
- [ ] Rows with unresolvable errors carry a non-empty `ValidationErrors` list

**Task 4 — Field Mapping Service**
- [ ] `FieldMappingService.AutoMatch(headerName)` returns canonical field name or null
- [ ] Covers aliases: `"First Name"` → `first_name`, `"DOB"` → `birth_date`, `"Dept"` → `department`, etc.
- [ ] `GetDropdownOptions()` returns all 14 canonical fields for the mapping UI
- [ ] Returns `ColumnMappingResult(SourceColumn, SuggestedField, SampleValue, TypeCompatibility)`

**Task 5 — PeopleHR API Adapter**
- [ ] `IHrSystemAdapter` interface with `FetchEmployeesAsync(apiKey)`
- [ ] `PeopleHrAdapter` calls PeopleHR REST API, maps response to `RawImportRow`
- [ ] Throws `AdapterException` on API error (non-2xx or `isError: true`)

**Task 6 — Bulk Import Endpoint + Hangfire Job**
- [ ] `ImportController` with 4 endpoints (all gated with `[RequirePermission("employees:write")]`):
  - `POST /api/v1/migration/upload-url` — pre-signed S3 URL
  - `POST /api/v1/migration/analyse` — parse headers + row 1, return mapping suggestions
  - `POST /api/v1/migration/bulk-import` — create `MigrationRun`, enqueue job, return `{ migrationRunId }`
  - `GET /api/v1/migration/runs/{id}/progress` — return status + row counts
- [ ] `ImportBackgroundJob` orchestrates: download → ETL → validate → bulk-write to `employees` → `UpdateProgress` throughout
- [ ] `MigrationRun.status` transitions: `Pending → Processing → Completed | Failed`

**Task 7 — Reconciliation + Cleanup**
- [ ] `ReconciliationService.ReconcileAsync` returns a spot-check sample of 10–15 randomly selected imported records
- [ ] `ImportFileCleanupJob` (Hangfire recurring, daily) deletes S3 files for terminal runs older than 7 days

### Backend References

- [[modules/data-import/overview|DataImport Module Overview]] — architecture, data model, API endpoints
- [[modules/core-hr/overview|CoreHR]] — `employees` table target
- [[modules/org-structure/overview|OrgStructure]] — department + job-family resolution
- [[backend/shared-kernel|Shared Kernel]] — `BaseEntity`, `IEncryptionService`, tenant scoping
- [[infrastructure/multi-tenancy|Multi-Tenancy]] — tenant-scoped `migration_runs`
- [[backend/module-catalog|Module Catalog]] — dependency map
- [[code-standards/backend-standards|Backend Standards]] — conventions, error handling, FluentValidation

---

## Step 2: Frontend (Phase B — Tasks 8–12)

### Pages to Build

```
app/(dashboard)/hr/import/
├── page.tsx                            # Wizard entry point
├── _components/
│   ├── ImportWizard.tsx                # Shell with 7-step progress bar
│   ├── FieldMappingTable.tsx           # Editable mapping dropdowns
│   └── steps/
│       ├── Step1ChooseMethod.tsx       # Cards: CSV / Excel / PeopleHR
│       ├── Step2aUploadFile.tsx        # Drag-drop → PUT to pre-signed S3 URL
│       ├── Step2bConnectPeopleHR.tsx   # API key input + masked display
│       ├── Step3FieldMapping.tsx       # Field mapping table step wrapper
│       ├── Step4JobGrouping.tsx        # Assign department / job family
│       ├── Step5Validation.tsx         # ETL errors/warnings table; skip or fix
│       ├── Step6ConfirmImport.tsx      # Summary counts + confirm button
│       └── Step7Done.tsx              # Spot-check list + success summary
├── _hooks/
│   ├── useImportWizard.ts             # Zustand state machine
│   └── useImportProgress.ts           # REST polling hook (1.5 s interval)
└── _lib/
    ├── import-types.ts                # Shared types + Zod schemas
    └── fieldTypeDetector.ts           # Sample-value → field type inference

app/(dashboard)/settings/integrations/
├── page.tsx                           # Grid of IntegrationCard components
└── _components/
    └── IntegrationCard.tsx            # Status badge, masked key, last import info
```

### Acceptance Criteria

**Task 8 — Wizard State Machine**
- [ ] `useImportWizard` Zustand store manages: `currentStep` (1–7), `method` (csv|excel|peopleHR), `fileKey`, `columnMappings`, `migrationRunId`
- [ ] `advance()` / `back()` step transitions
- [ ] PeopleHR path: `method === 'peopleHR'` skips Step 2a and jumps to Step 2b

**Task 9 — Wizard Shell + Steps 1 & 2**
- [ ] `ImportWizard` renders a progress bar showing current step label; completed steps shown with strikethrough
- [ ] `Step1ChooseMethod` renders three clickable cards; selecting one calls `chooseMethod()` and advances
- [ ] `Step2aUploadFile` uploads via PUT to the pre-signed URL from `POST /api/v1/migration/upload-url`; on success stores `fileKey` in wizard store
- [ ] `Step2bConnectPeopleHR` validates the API key input (non-empty); stores in wizard store

**Task 10 — Step 3: Field Mapping**
- [ ] `FieldMappingTable` shows one row per source column with: source header, sample value, editable dropdown of canonical fields
- [ ] Auto-populated suggestions come from `POST /api/v1/migration/analyse`
- [ ] `fieldTypeDetector.ts` infers type from sample value: `date`, `email`, `phone`, `salary`, `text`
- [ ] User can change any mapping; "required" fields (first_name, last_name, email) are visually flagged

**Task 11 — Steps 4–7 + Progress**
- [ ] `Step4JobGrouping` allows assigning department + job family to all rows or by group
- [ ] `Step5Validation` renders a table of ETL errors with row number, field, error message; rows can be skipped
- [ ] `Step6ConfirmImport` shows total/success/failed/skipped counts; confirm button calls `POST /api/v1/migration/bulk-import`; button disabled while loading
- [ ] `Step7Done` displays the reconciliation spot-check list (10–15 sampled records) and success message
- [ ] `useImportProgress` polls every 1.5 s; clears interval on `Completed` or `Failed`; advances wizard to Step 7 on `Completed`

**Task 12 — Integrations Screen + Employee List Button**
- [ ] `IntegrationCard` shows: integration name, status badge (green "Connected" / grey "Not connected"), masked API key (last 4 chars), last import date + employee count
- [ ] Integrations page at `/settings/integrations` renders at minimum the PeopleHR card
- [ ] "Import Employees" button added to `/hr/employees` page linking to `/hr/import`

### Frontend References

- [[frontend/architecture/app-structure|App Structure]] — Next.js app directory layout
- [[frontend/data-layer/state-management|State Management]] — TanStack Query + Zustand patterns
- [[frontend/data-layer/api-integration|API Integration]] — API client, error handling, pagination
- [[frontend/design-system/README|Design System]] — shadcn/ui components, design tokens
- [[frontend/coding-standards|Frontend Coding Standards]] — conventions
- [[modules/data-import/overview|DataImport Module Overview]] — API endpoint contracts
