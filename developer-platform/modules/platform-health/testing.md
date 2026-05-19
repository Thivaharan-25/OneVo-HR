# Platform Health - Testing

## Test Fixtures Required

- Platform account with `platform.health.read`
- Platform account with no permissions
- Mock health check endpoint that can return degraded/down states
- Registry fixture with at least one critical service, one medium service, one dependency, and one timed-out reader
- Registry fixture with one planned reader that has no implementation yet
- Redaction fixture containing fake connection strings, JWTs, cookies, API keys, internal IPs, and PII-like values
- Contract fixture and fake reader outputs from [[developer-platform/modules/platform-health/contract-validation|Platform Health Contract Validation]]

---

## Pre-Implementation Contract Tests

Run these before real health readers are implemented. They validate the registry shape, redaction guard, status mapper, and overall health calculator without requiring the full API endpoint.

| Test Area | Required Coverage |
|---|---|
| Registry validation | Duplicate service keys, unknown dependency keys, invalid criticality, empty check lists, missing status rules |
| Planned readers | `planned_reader:` checks are valid registry entries but always return `unknown` until implemented |
| Stale evidence | Evidence older than `freshness_sla_seconds` maps to `unknown`, not `healthy` |
| Timeout handling | Reader timeout maps to `unknown` and does not block the full response |
| Redaction guard | Unsafe reader output is discarded and maps to `unknown` |
| Status mapping | Healthy, degraded, down, and unknown check states map deterministically to service status |
| Overall scoring | Weighted health percentage includes unknown services in the denominator |
| Critical overrides | Critical `down` forces overall `down`; critical `unknown` prevents overall `healthy` |

### TC-PH-001: Platform health endpoint requires health.read permission
**Setup:** Account with no permissions
**Action:** `GET /admin/v1/operations/platform-health`
**Expected:** HTTP 403

### TC-PH-002: Tenant JWT rejected
**Action:** `GET /admin/v1/operations/platform-health` with tenant JWT
**Expected:** HTTP 401

### TC-PH-003: No secrets or internal credentials in health response
**Action:** `GET /admin/v1/operations/platform-health`
**Expected:** Response contains: service names, status badges, uptime %, latency metrics. Does NOT contain: database connection strings, API keys, environment variables, internal IPs, or credential values.

### TC-PH-004: Single failing service shown as degraded without failing whole response
**Setup:** Simulate `reporting_engine` service returning 500 on health check
**Action:** `GET /admin/v1/operations/platform-health`
**Expected:**
- HTTP 200 for the platform health endpoint
- `reporting_engine` service: `status = "down"` or `status = "degraded"`
- Other services: still show their correct healthy state
- `overall_health_pct` reduced but response not a 500

### TC-PH-005: Health check reader timeout does not block page
**Setup:** Simulate health check for one service timing out after 5 seconds
**Action:** `GET /admin/v1/operations/platform-health`
**Expected:** Response returns within reasonable time (< 10s) with timed-out service showing `status = "unknown"` rather than the whole request hanging

### TC-PH-006: Dashboard platform health widget shows same data as full health endpoint
**Action:** `GET /admin/v1/dashboard/platform-health` vs `GET /admin/v1/operations/platform-health`
**Expected:** Dashboard endpoint returns same per-service status data - same source, different response shape (dashboard is a summary, operations endpoint is the full detail)

### TC-PH-007: Missing evidence is unknown, not healthy
**Setup:** Registry includes `auth_service.token_validation`, but the token validation reader returns no fresh evidence
**Action:** `GET /admin/v1/operations/platform-health`
**Expected:** `auth_service.checks[token_validation].status = "unknown"` and the check counts against `overall_health_pct`

### TC-PH-008: Database health includes migration and table evidence
**Action:** `GET /admin/v1/operations/platform-health`
**Expected:** Database evidence includes safe values for live connection result, latest `__EFMigrationsHistory` migration id or empty-state marker, pending migration count, required table sample result, and read/write probe result. Response does not include connection strings.

### TC-PH-009: Registry drives service criticality and dependencies
**Setup:** Registry marks `auth_service` as `critical` with dependency `postgresql`
**Action:** `GET /admin/v1/operations/platform-health`
**Expected:** Response shows `criticality = "critical"` and includes `postgresql` in the service dependency list. UI does not invent dependencies absent from the registry.

### TC-PH-010: Runtime-only evidence cannot be inferred from docs
**Setup:** Logs/metrics/queue readers are unavailable
**Action:** `GET /admin/v1/operations/platform-health`
**Expected:** Observability, queue depth, worker heartbeat, and failed job checks return `unknown`, not `healthy`

### TC-PH-011: Invalid registry dependency fails validation
**Setup:** Registry includes `auth_service.expected_dependencies = ["postgresql", "missing_dependency"]`, but only `postgresql` exists in the dependency registry
**Action:** Start API or load Platform Health registry
**Expected:** Startup or registry validation fails with a safe configuration error. The API must not silently drop `missing_dependency` or report `auth_service` as healthy.

### TC-PH-012: Unknown checks reduce overall health percentage
**Setup:** Registry has two equal-weight services. One is `healthy`; one has only stale evidence and maps to `unknown`.
**Action:** `GET /admin/v1/operations/platform-health`
**Expected:** `overall_health_pct = 50`, `unknown_check_count > 0`, and the unknown service remains visible in the response.

### TC-PH-013: Critical unknown prevents green overall status
**Setup:** `auth_service` is `critical`; its signing-key validation reader is unavailable.
**Action:** `GET /admin/v1/operations/platform-health`
**Expected:** `auth_service.status = "unknown"` or a check under it is `unknown`; `overall_status` is not `"healthy"`.

### TC-PH-014: Critical down forces overall down
**Setup:** `data_service` is `critical`; live DB connection reader returns a safe down result.
**Action:** `GET /admin/v1/operations/platform-health`
**Expected:** `data_service.status = "down"` and `overall_status = "down"` even if non-critical services are healthy.

### TC-PH-015: Reader output must be redacted before response
**Setup:** A fake reader returns evidence containing a connection string, JWT, cookie, API key, internal IP, stack trace, and user email
**Action:** `GET /admin/v1/operations/platform-health`
**Expected:** Unsafe fields are absent from the response. The check returns safe summarized evidence or `unknown` if redaction cannot be applied.

### TC-PH-016: Planned reader is visible as unknown
**Setup:** Registry includes planned `frontend_console.session_refresh_check` with no implemented evidence source
**Action:** `GET /admin/v1/operations/platform-health`
**Expected:** The check appears with `status = "unknown"` and a stable `reader_error_code` such as `reader_not_implemented`.

### TC-PH-017: Services Monitor uses the same registry keys
**Action:** Compare `GET /admin/v1/operations/platform-health` services with `GET /admin/v1/operations/services`
**Expected:** Services Monitor uses the same `service_key`, dependency keys, criticality, and approved action keys. It does not introduce services or actions absent from the Platform Health registry.
