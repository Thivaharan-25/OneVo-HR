# Services Monitor — Testing

## Test Fixtures Required

- Platform account with `platform.health.manage`
- Platform account with `platform.health.read` only
- At least 2 monitored services registered in the system

---

### TC-SM-001: Read endpoint requires health.read
**Setup:** Account with no permissions
**Action:** `GET /admin/v1/operations/services`
**Expected:** HTTP 403

### TC-SM-002: Mutating action endpoint requires health.manage
**Setup:** Account with `platform.health.read` only
**Action:** `POST /admin/v1/operations/services/{serviceKey}/actions/restart`
**Expected:** HTTP 403

### TC-SM-003: Unknown service key returns 404
**Action:** `GET /admin/v1/operations/services/this_service_does_not_exist`
**Expected:** HTTP 404 — not a 500

### TC-SM-004: Error summaries do not contain secrets or PII
**Action:** `GET /admin/v1/operations/services/{serviceKey}` for a degraded service
**Expected:** Response includes: error rate, latency metrics, recent error messages. Does NOT include: raw stack traces with connection strings, employee PII, internal IP addresses, JWT secrets.

### TC-SM-005: Unsupported service action cannot be invoked by URL guessing
**Action:** `POST /admin/v1/operations/services/auth_service/actions/delete_all_data`
**Expected:** HTTP 400 or HTTP 404 — `delete_all_data` is not a registered approved action. Only explicitly approved actions are executable.

### TC-SM-006: Approved service action writes audit log
**Setup:** Account with `platform.health.manage`. `flush_cache` is an approved action for the `reporting_engine` service.
**Action:** `POST /admin/v1/operations/services/reporting_engine/actions/flush_cache`
**Expected:**
- Action executed
- Audit log: `action = 'service_action.executed'`, `service = 'reporting_engine'`, `action_name = 'flush_cache'`, actor, timestamp

### TC-SM-007: Tenant JWT rejected
**Action:** `GET /admin/v1/operations/services` with tenant JWT
**Expected:** HTTP 401
