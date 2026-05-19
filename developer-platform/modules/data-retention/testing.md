# Data Retention — Testing

## Test Fixtures Required

- Platform account with `platform.compliance.manage`
- Platform account with `platform.compliance.read` only
- Tenant with active legal hold in `legal_holds`
- Tenant without legal hold whose data is old enough to fall within retention
- Retention policy seeded: standard events = 2 years, security events = 5 years, billing = 7 years

---

### TC-DR-001: Policy update requires manage permission
**Setup:** Account with `platform.compliance.read` only
**Action:** `PATCH /admin/v1/retention-policies/{id}` reducing retention period
**Expected:** HTTP 403

### TC-DR-002: Impact preview required before shortening retention
**Setup:** Retention policy at 2 years. Attempting to reduce to 90 days.
**Action:** `PATCH /admin/v1/retention-policies/{id}` `{"retention_days": 90}` without first calling impact preview
**Expected:** HTTP 422 — impact preview must be acknowledged before destructive shortening; or: backend calls `GET /admin/v1/retention-policies/{id}/impact` and includes result in error response

### TC-DR-003: Legal hold protected records skipped by retention sweep
**Setup:**
- Tenant A: active legal hold covering all data
- Tenant B: no legal hold, has records older than retention period
**Action:** Retention sweep job runs
**Expected:**
- Tenant A: zero records deleted (legal hold protection)
- Tenant B: records beyond retention period deleted
- Audit log entries for each deletion batch

### TC-DR-004: Retention sweep is idempotent
**Action:** Retention sweep job runs twice in the same window
**Expected:** Second run deletes zero additional records — already-deleted records are not double-processed. No error thrown.

### TC-DR-005: Audit records for security category are retained 5 years (not 2)
**Setup:** Audit record with `action_category = 'security'` created 3 years ago. Standard retention is 2 years.
**Action:** Retention sweep runs
**Expected:** Record NOT deleted — 5-year retention for security events applies

### TC-DR-006: Policy update audit log includes old and new values with reason
**Action:** `PATCH /admin/v1/retention-policies/{id}` `{"retention_days": 730, "reason": "Aligning to GDPR Article 5 guidance"}`
**Expected:** Audit log: `previous_retention_days`, `new_retention_days`, actor, reason recorded

### TC-DR-007: Tenant JWT rejected
**Action:** `GET /admin/v1/retention-policies` with tenant JWT
**Expected:** HTTP 401
