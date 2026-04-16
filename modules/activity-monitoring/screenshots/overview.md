# Screenshots

**Module:** Activity Monitoring
**Feature:** Screenshots

---

## Purpose

Optional periodic screenshot capture. **RESTRICTED data classification.** Screenshots are stored in blob storage, NOT in the database — only metadata lives here.

## Database Tables

### `screenshots`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `captured_at` | `timestamptz` | |
| `file_record_id` | `uuid` | FK → file_records (blob storage) |
| `trigger_type` | `varchar(20)` | `scheduled`, `random`, `manual` |
| `created_at` | `timestamptz` | |

**Retention:** Per tenant retention policy (default 30 days).

## Key Business Rules

1. Screenshots require feature toggle enabled via `IConfigurationService`.
2. RESTRICTED data classification — encrypted at rest, access-logged.
3. **Screenshot URLs are time-limited SAS tokens only** (Azure Blob Shared Access Signature, 15-minute expiry). The `/view` endpoint calls `IFileService.GetTemporaryUrlAsync(fileRecordId, expiry: TimeSpan.FromMinutes(15))` and returns the signed URL — it never redirects to or returns a permanent blob URL. This ensures RBAC revocation is effective: a revoked `workforce:view` permission stops access on the next request.

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `ScreenshotCaptured` | Screenshot stored | Audit trail |

## Hangfire Jobs

| Job | Schedule | Purpose |
|:----|:---------|:--------|
| `PurgeExpiredScreenshotsJob` | Daily 4:00 AM | Delete screenshots past retention policy |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/activity/screenshots/{employeeId}` | `workforce:view` | Screenshot list (metadata only) |
| GET | `/api/v1/activity/screenshots/{id}/view` | `workforce:view` | Returns 15-minute SAS URL for screenshot blob (never a permanent URL) |

## Related

- [[modules/activity-monitoring/overview|Activity Monitoring Module]]
- [[modules/activity-monitoring/screenshots/end-to-end-logic|Screenshots — End-to-End Logic]]
- [[modules/activity-monitoring/screenshots/testing|Screenshots — Testing]]
- [[frontend/architecture/overview|Raw Data Processing]]
- [[security/data-classification|Data Classification]]
- [[modules/configuration/retention-policies/overview|Retention Policies]]
- [[code-standards/logging-standards|Logging Standards]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[current-focus/DEV3-activity-monitoring|DEV3: Activity Monitoring]]
