# Screenshots

**Module:** Activity Monitoring
**Feature:** Screenshots

---

## Purpose

Policy-controlled screenshot capture. **RESTRICTED data classification.** Screenshots are stored in blob storage, NOT in the database - only evidence metadata lives in `monitoring_evidence_assets`.

Screenshots are created only from live on-demand requests by authorized users or automatic deviation capture when the effective monitoring policy allows it. Random and interval screenshots are not supported.

## Database Tables

### `monitoring_evidence_assets`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `agent_device_id` | `uuid` | Nullable FK -> registered_agents |
| `activity_snapshot_id` | `uuid` | Nullable FK -> activity_snapshots |
| `captured_at` | `timestamptz` | |
| `file_record_id` | `uuid` | FK -> file_records (blob storage) |
| `evidence_type` | `varchar(40)` | `screenshot` |
| `source` | `varchar(30)` | `agent` or `system` |
| `trigger_type` | `varchar(20)` | `on_demand`, `auto_deviation` |
| `retention_policy_id` | `uuid` | Nullable FK -> retention_policies |
| `legal_hold_id` | `uuid` | Nullable FK -> legal_holds |
| `created_at` | `timestamptz` | |

**Retention:** Per tenant retention policy (default 30 days).

## Key Business Rules

1. Screenshots require feature toggle enabled via `IConfigurationService`.
2. Screenshots are captured only by authorized live on-demand request or by automatic deviation capture when `auto_screenshot_capture` is enabled. Do not build interval or random screenshot capture.
3. RESTRICTED data classification - encrypted at rest, access-logged.
4. **Screenshot URLs are time-limited signed URLs only** (15-minute expiry). The `/view` endpoint calls `IFileService.GetTemporaryUrlAsync(fileRecordId, expiry: TimeSpan.FromMinutes(15))` and returns the signed URL. It never redirects to or returns a permanent object URL. This ensures RBAC revocation is effective: a revoked `monitoring:view` permission stops access on the next request.

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `ScreenshotCaptured` | Screenshot stored | Audit trail |

## Hangfire Jobs

| Job | Schedule | Purpose |
|:----|:---------|:--------|
| `PurgeExpiredMonitoringEvidenceJob` | Daily 4:00 AM | Delete screenshot evidence past retention policy, unless held |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/activity/screenshots/{employeeId}` | `monitoring:view` | Screenshot list (metadata only) |
| GET | `/api/v1/activity/screenshots/{id}/view` | `monitoring:view` | Returns 15-minute SAS URL for screenshot blob (never a permanent URL) |

## Related

- [[modules/activity-monitoring/overview|Activity Monitoring Module]]
- [[modules/activity-monitoring/screenshots/end-to-end-logic|Screenshots - End-to-End Logic]]
- [[modules/activity-monitoring/screenshots/testing|Screenshots - Testing]]
- [[modules/agent-gateway/data-collection|Agent Data Collection]]
- [[security/data-classification|Data Classification]]
- [[modules/configuration/retention-policies/overview|Retention Policies]]
- [[code-standards/logging-standards|Logging Standards]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[current-focus/DEV3-activity-monitoring|DEV3: Activity Monitoring]]
