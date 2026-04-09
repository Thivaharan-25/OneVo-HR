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
| GET | `/api/v1/activity/screenshots/{id}/view` | `workforce:view` | View screenshot (redirect to blob URL) |

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
