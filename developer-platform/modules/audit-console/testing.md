# Audit Console — Testing

## Test Fixtures Required

- Platform account with `platform.audit.export`
- Platform account with `platform.audit.read` only
- Platform account with no permissions
- `audit_log` seeded with: 50 rows across 3 tenants, various action categories, mixed success/failed results, some with IP addresses, some system-generated
- At least 1 entry with `action_category = 'security'` and a sensitive field in `new_state`

---

## Query Permissions and Bounds

### TC-AC-001: Audit query requires date range — unbounded queries blocked
**Action:** `GET /admin/v1/audit-logs` (no `from` or `to`)
**Expected:** HTTP 400, `code: "missing_date_range"` — unbounded queries are never allowed

### TC-AC-002: Date range over 90 days blocked
**Action:** `GET /admin/v1/audit-logs?from=2025-01-01T00:00:00Z&to=2026-05-17T00:00:00Z`
**Expected:** HTTP 400, `code: "date_range_too_large"` — use narrower window or export

### TC-AC-003: Audit read permission required
**Setup:** Account with no permissions
**Action:** `GET /admin/v1/audit-logs?from=...&to=...`
**Expected:** HTTP 403

### TC-AC-004: Export requires audit.export permission
**Setup:** Account with `platform.audit.read` only (no export)
**Action:** `POST /admin/v1/audit-logs/export`
**Expected:** HTTP 403

### TC-AC-005: Tenant JWT is rejected
**Action:** `GET /admin/v1/audit-logs` with `iss: "onevo-tenant"` token
**Expected:** HTTP 401

---

## Query Filters

### TC-AC-006: Tenant filter returns only that tenant's events
**Setup:** Audit log has events for tenant A and tenant B
**Action:** `GET /admin/v1/audit-logs?from=...&to=...&tenant_id={tenantA_id}`
**Expected:** All rows returned have `tenant_id = tenantA_id`. Tenant B events not present.

### TC-AC-007: Actor type filter works correctly
**Action:** `GET /admin/v1/audit-logs?from=...&to=...&actor_type=platform_admin`
**Expected:** Only entries with `actor_type = 'platform_admin'`. No tenant_user or system entries.

### TC-AC-008: Action category filter works correctly
**Action:** `GET /admin/v1/audit-logs?from=...&to=...&action_category=billing`
**Expected:** Only billing-category action codes (`invoice.generated`, `payment.failed`, etc.)

### TC-AC-009: Result filter returns only failed events
**Action:** `GET /admin/v1/audit-logs?from=...&to=...&result=failed`
**Expected:** Only entries with `result = 'failed'`. No success entries.

### TC-AC-010: Free-text search matches actor name and action description
**Setup:** Audit log has entry where `actor_name = "James Anderson"` and `action_description = "Tenant suspended"`
**Action:** `GET /admin/v1/audit-logs?from=...&to=...&search=James`
**Expected:** Entry appears in results

---

## Data Integrity — Sensitive Field Redaction

### TC-AC-011: API keys and secrets are redacted in previous_state and new_state
**Setup:** Audit log entry for `system_config.ai_key_updated` — action that stored an AI provider key. Actual key stored as `[REDACTED]` in the audit row's `new_state`.
**Action:** `GET /admin/v1/audit-logs/{id}` (single entry detail)
**Expected:**
- Response `new_state.api_key = "[REDACTED]"` — raw value never stored or returned
- `previous_state.api_key = "[REDACTED]"` if it existed
- All other non-sensitive fields returned normally

### TC-AC-012: Audit records cannot be modified through API
**Action:** Any `PATCH`, `PUT`, or `DELETE` against `/admin/v1/audit-logs/{id}`
**Expected:** HTTP 405 Method Not Allowed — audit records are append-only

### TC-AC-013: Audit records cannot be deleted through API
**Action:** `DELETE /admin/v1/audit-logs/{id}`
**Expected:** HTTP 405 — no deletion endpoint exists

---

## Every Query Is Itself Audit-Logged

### TC-AC-014: Audit Console access creates an audit entry
**Action:** `GET /admin/v1/audit-logs?from=...&to=...`
**Expected:**
- HTTP 200 with results
- NEW `audit_log` entry created: `action = 'audit_log.queried'`, `actor_id` = current platform account, `metadata` contains the filter params used
- This self-audit entry is itself queryable in subsequent audit queries

### TC-AC-015: Export request creates an audit entry
**Action:** `POST /admin/v1/audit-logs/export` with filters
**Expected:**
- `audit_log` entry: `action = 'audit_log.exported'`, actor, format, filter params, estimated row count

---

## Export Behaviour

### TC-AC-016: Synchronous CSV export for small result set
**Setup:** Filters match 500 rows
**Action:** `POST /admin/v1/audit-logs/export` `{"format": "csv", "filters": {...}}`
**Expected:**
- HTTP 200
- `Content-Type: text/csv`
- `Content-Disposition: attachment; filename="audit-export-....csv"`
- CSV contains correct columns: `timestamp`, `actor_type`, `actor_name`, `actor_email`, `action_code`, `action_description`, `resource_type`, `resource_name`, `tenant_name`, `result`, `ip_address`, `metadata`
- Exactly 500 data rows (plus header row)

### TC-AC-017: Async export for large result set
**Setup:** Filters match 15,000 rows
**Action:** `POST /admin/v1/audit-logs/export` `{"format": "json", "filters": {...}}`
**Expected:**
- HTTP 200
- Response: `{"export_job_id": "...", "status": "queued", "estimated_rows": 15000, "notification": "...email..."}`
- NOT an immediate file download

### TC-AC-018: Async export job status endpoint works
**Setup:** Async export job queued (TC-AC-017)
**Action:** `GET /admin/v1/audit-logs/export/{jobId}`
**Expected:** Response includes `status` (`queued` / `processing` / `completed`), `download_url` when completed, `expires_at` (24 hours from completion)

### TC-AC-019: Export blocked when too large
**Setup:** Filters match 150,000 rows
**Action:** `POST /admin/v1/audit-logs/export`
**Expected:** HTTP 422, `code: "export_too_large"` — must narrow filters below 100,000 rows

### TC-AC-020: JSON export includes previous_state and new_state (with redaction)
**Action:** `POST /admin/v1/audit-logs/export` `{"format": "json", "filters": {...}}`
**Expected:** JSON objects include `previous_state` and `new_state` fields (not in CSV). Sensitive fields still `[REDACTED]`.

---

## Tenant-Scoped Audit Access

### TC-AC-021: Tenant-scoped audit endpoint pre-filters to tenant
**Action:** `GET /admin/v1/tenants/{tenantId}/audit?from=...&to=...`
**Expected:** Identical to `GET /admin/v1/audit-logs?tenant_id={tenantId}&from=...&to=...` — same results, same columns, same filters available
