# Background Jobs — Testing

## Test Fixtures Required

- Platform account with `platform.health.manage`
- Platform account with `platform.health.read` only
- At least 3 background jobs registered: 1 scheduled (healthy), 1 failed (retryable), 1 failed (non-retryable)

---

### TC-BJ-001: Job list read requires health.read
**Setup:** Account with no permissions
**Action:** `GET /admin/v1/operations/background-jobs`
**Expected:** HTTP 403

### TC-BJ-002: Non-retryable job rejects retry attempt
**Setup:** Failed job with `is_retryable = false` (e.g., a one-time migration job that cannot safely run twice)
**Action:** `POST /admin/v1/operations/background-jobs/{jobId}/retry`
**Expected:** HTTP 422 — `code: "job_not_retryable"`. Non-retryable jobs cannot be triggered again via this endpoint.

### TC-BJ-003: Retryable job retry is audit-logged
**Setup:** Retryable failed job (e.g., `InvoiceGenerationJob` that failed due to transient DB error)
**Action:** `POST /admin/v1/operations/background-jobs/{jobId}/retry`
**Expected:**
- Job re-queued or re-triggered
- Audit log: `action = 'background_job.retry_triggered'`, job name, actor, reason

### TC-BJ-004: Schedule update requires reason
**Action:** `PATCH /admin/v1/operations/background-jobs/{jobId}` `{"schedule": "0 3 * * *"}` without `reason`
**Expected:** HTTP 422 — changing job schedule requires an audit reason

### TC-BJ-005: Error output is redacted — no raw stack traces with secrets
**Setup:** Job failed with an exception that included a database connection string in the stack trace
**Action:** `GET /admin/v1/operations/background-jobs/{jobId}`
**Expected:** `last_error` field contains a sanitized error message. Connection strings, passwords, JWT secrets, and internal file paths are `[REDACTED]`. The original exception detail is logged to the internal logging system, not returned via the API.

### TC-BJ-006: Job list filters work correctly
**Action:** `GET /admin/v1/operations/background-jobs?status=failed`
**Expected:** Only jobs with `last_run_status = 'failed'` returned. Healthy and running jobs excluded.

### TC-BJ-007: Manage permission required for retry and schedule update
**Setup:** Account with `platform.health.read` only
**Action 1:** `POST /admin/v1/operations/background-jobs/{jobId}/retry`
**Expected:** HTTP 403

**Action 2:** `PATCH /admin/v1/operations/background-jobs/{jobId}` to update schedule
**Expected:** HTTP 403
