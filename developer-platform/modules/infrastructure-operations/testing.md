# Infrastructure Operations — Testing

> Phase 2 only as a standalone module. In Phase 1, test only aggregate dependency status surfaced through Platform Health.

## Test Fixtures Required

- Platform account with `platform.health.read`
- Platform account with no permissions
- Mock infrastructure metrics available (CPU, memory, storage, dependency health)

---

### TC-IO-001: Infrastructure read requires health.read
**Setup:** Account with no permissions
**Action:** `GET /admin/v1/operations/infrastructure`
**Expected:** HTTP 403

### TC-IO-002: Tenant JWT rejected
**Action:** `GET /admin/v1/operations/infrastructure` with tenant JWT
**Expected:** HTTP 401

### TC-IO-003: Response does not contain secrets or internal credentials
**Action:** `GET /admin/v1/operations/infrastructure`
**Expected:** Response contains: capacity metrics (CPU %, memory %, storage %, region, instance count), dependency statuses. Does NOT contain: database connection strings, cloud provider API keys, internal hostnames used for auth, or any credential values.

### TC-IO-004: Degraded dependency state includes timestamp
**Setup:** Simulate external dependency (e.g., Cloudflare) as degraded
**Action:** `GET /admin/v1/operations/infrastructure/dependencies`
**Expected:** Degraded dependency entry includes: `status: "degraded"`, `detected_at` timestamp (when degradation was first observed), `last_checked_at`. Not just a current-state snapshot without timing context.

### TC-IO-005: Missing provider metric does not crash the response
**Setup:** Simulate one infrastructure provider metric endpoint timing out (e.g., Azure storage metrics unavailable)
**Action:** `GET /admin/v1/operations/infrastructure`
**Expected:**
- HTTP 200 (response still succeeds)
- Affected metric shows `status: "unknown"` or `value: null` with `error: "metric unavailable"`
- Other infrastructure metrics returned normally

### TC-IO-006: Infrastructure summary matches platform health widget data
**Action:** Compare `GET /admin/v1/operations/infrastructure` with `GET /admin/v1/dashboard/resource-utilization`
**Expected:** CPU, memory, storage percentages are consistent between the two endpoints — same underlying metric source, different response detail level
