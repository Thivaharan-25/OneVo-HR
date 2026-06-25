# Reports / Analytics - Testing

## Test Fixtures Required

- Platform account with `platform.reports.read`
- Platform account with no permissions
- At least 5 active tenants with varying entitlement states
- `tenant_module_entitlements` seeded with real adoption data

---

### TC-AN-001: Analytics endpoints require platform.reports.read
**Setup:** Account with no permissions
**Action:** `GET /admin/v1/reports/analytics`
**Expected:** HTTP 403

### TC-AN-002: Tenant JWT rejected
**Action:** `GET /admin/v1/analytics/tenants` with tenant JWT
**Expected:** HTTP 401

### TC-AN-003: Analytics responses do not expose employee-level activity
**Action:** `GET /admin/v1/reports/analytics?from=...&to=...`
**Expected:** Response contains aggregate counts (total active users, DAU, sessions). Does NOT contain: individual user names, individual user activity details, individual keystrokes or screenshots, employee-level breakdowns. All data is aggregated at tenant or platform level.

### TC-AN-004: Module adoption counts match entitlement source of truth
**Setup:** `tenant_module_entitlements` has 30 tenants with `activity_monitoring` in `active` status, 5 in `pending_payment`
**Action:** `GET /admin/v1/analytics/modules`
**Expected:**
- `activity_monitoring.active_tenants = 30`
- `activity_monitoring.pending_payment_tenants = 5`
- Counts match `tenant_module_entitlements` table - not subscription plan data alone

### TC-AN-005: Date filters are enforced - no data outside range returned
**Setup:** Events exist for May 2025 and May 2026
**Action:** `GET /admin/v1/reports/analytics?from=2026-05-01T00:00:00Z&to=2026-05-31T23:59:59Z`
**Expected:** Only May 2026 data returned. May 2025 events not included.

### TC-AN-006: Subscription analytics require subscriptions.read - not just analytics.read
**Action:** `GET /admin/v1/analytics/subscriptions` with account having only `platform.reports.read` (not `platform.subscriptions.read`)
**Expected:** HTTP 403 or subscription data filtered to non-commercial data - commercial analytics require `platform.subscriptions.read`

### TC-AN-007: Tenant filter scopes analytics to single tenant
**Action:** `GET /admin/v1/reports/analytics?tenant_id={tenantId}&from=...&to=...`
**Expected:** All returned metrics scoped to that single tenant. Cross-tenant aggregates not included.

