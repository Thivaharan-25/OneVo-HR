# Report Manager — Testing

## Test Fixtures Required

- Platform account with `platform.reports.read` + `platform.reports.export` (if export separate)
- Platform account with `platform.reports.read` only
- Platform account with no permissions
- At least 2 report definitions in the report catalog
- 1 completed export job, 1 export job with expired download link

---

### TC-RM-001: Report list requires platform.reports.read
**Setup:** Account with no permissions
**Action:** `GET /admin/v1/reports`
**Expected:** HTTP 403

### TC-RM-002: Export access is permission-gated
**Setup:** Account with `platform.reports.read` but no explicit export permission
**Action:** `POST /admin/v1/reports/export`
**Expected:** HTTP 403 if export is a separate permission, or HTTP 200 if included with reports.read — confirm which design is implemented and assert accordingly

### TC-RM-003: Expired export download link cannot be accessed
**Setup:** Completed export with `download_expires_at` in the past
**Action:** `GET /admin/v1/reports/exports/{id}` — attempt to use the expired download URL
**Expected:** Download URL marked expired. HTTP 410 or link returns 403/404 from storage provider.

### TC-RM-004: Export job records filters and requester
**Action:** `POST /admin/v1/reports/export` with specific date filters and tenant filter
**Expected:**
- Export job record created with: `requested_by_id` (platform account), `filters_snapshot` (JSON of applied filters), `requested_at`
- Audit log: `action = 'report.export_requested'`, actor, report type, filters

### TC-RM-005: Failed report job returns readable error — no raw stack traces
**Setup:** Report job that failed due to a query timeout
**Action:** `GET /admin/v1/reports/exports/{id}` for a failed job
**Expected:** `error_message` is human-readable (e.g., "Report generation timed out. Try a narrower date range."). No raw SQL errors, no stack traces, no internal server paths in the response.

### TC-RM-006: Export status polling works for async jobs
**Action:** `POST /admin/v1/reports/export` → get `export_job_id`. Poll `GET /admin/v1/reports/exports/{id}` repeatedly.
**Expected:**
- Status transitions: `queued` → `processing` → `completed`
- When `completed`: `download_url` present, `expires_at` set (24 hours from completion)
- When `queued`: `download_url` absent

### TC-RM-007: Tenant JWT rejected
**Action:** `GET /admin/v1/reports` with tenant JWT
**Expected:** HTTP 401
