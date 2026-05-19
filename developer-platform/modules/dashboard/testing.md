# Dashboard — Testing

## Test Fixtures Required

- At least 3 tenants seeded: one `active`, one `suspended`, one `provisioning`, one `cancelled`
- At least 2 `platform_alerts` rows: one `severity = 'critical'` unresolved, one `severity = 'warning'` unresolved
- Platform account with `platform.dashboard.view` permission
- Platform account with NO permissions (for permission rejection tests)

---

## KPI Cards

### TC-D-001: Total Tenants count excludes cancelled
**Setup:** 5 active, 2 suspended, 1 provisioning, 1 cancelled tenant in DB
**Action:** `GET /admin/v1/dashboard/summary`
**Expected:** `total_tenants = 8` (all except cancelled), `active_tenants = 5`, `suspended_tenants = 2`

### TC-D-002: Active Users counts only users in active tenants
**Setup:** Active tenant has 50 users with events in window; suspended tenant has 20 users with events
**Action:** `GET /admin/v1/dashboard/summary?from=...&to=...`
**Expected:** `active_users` = 50; suspended tenant users not counted

### TC-D-003: Alerts KPI card shows Critical and Warning separately
**Setup:** 3 critical unresolved, 8 warning unresolved, 15 info alerts in `platform_alerts`
**Action:** `GET /admin/v1/dashboard/alerts`
**Expected:** `critical_count = 3`, `warning_count = 8`, `info_count = 15`; info count NOT added to total_alerts badge

### TC-D-004: Dashboard rejects tenant-scoped JWT
**Action:** `GET /admin/v1/dashboard/summary` with `iss: "onevo-tenant"` token
**Expected:** HTTP 401 — tenant JWT rejected at `/admin/v1/*` namespace

### TC-D-005: Dashboard rejects platform account without permission
**Setup:** Platform account with no permissions
**Action:** `GET /admin/v1/dashboard/summary`
**Expected:** HTTP 403

---

## Alert Detection — Pathway 1 (Domain Events)

### TC-D-006: Brute force alert created at threshold
**Action:** Publish 10 `LoginFailedEvent` events from same IP to same tenant within 5 minutes
**Expected:**
- `platform_alerts` row created: `alert_code = 'auth.brute_force_detected'`, `severity = 'critical'`, `tenant_id` set correctly
- `GET /admin/v1/dashboard/alerts` returns `critical_count` incremented by 1

### TC-D-007: Brute force below threshold creates only Warning
**Action:** Publish 6 `LoginFailedEvent` from same tenant in 1 hour (below brute-force threshold of 10 in 5 min)
**Expected:** `alert_code = 'auth.failed_login_spike'`, `severity = 'warning'` — NOT critical

### TC-D-008: Alert deduplication — no duplicate rows
**Setup:** One active `auth.brute_force_detected` alert exists for tenant T
**Action:** Trigger threshold again for same tenant
**Expected:**
- No new `platform_alerts` row inserted
- Existing alert's `detail` and `updated_at` updated
- `critical_count` does not increase again

### TC-D-009: Identity verification spike threshold is 3 failures in 1 hour
**Action:** 2 `IdentityVerificationFailedEvent` for different users in 1 hour
**Expected:** No alert created (below threshold)
**Action:** 3rd failure within same hour
**Expected:** `platform_alerts` row: `alert_code = 'identity.verification_failed_spike'`, `severity = 'critical'`

---

## Alert Detection — Pathway 2 (Background Jobs)

### TC-D-010: PlatformHealthCheckJob raises Critical after 2 consecutive failures
**Action:** Simulate health check returning `status = 'down'` for Auth Service on check 1 and check 2
**Expected:** After check 2: `platform_alerts` row `alert_code = 'infra.service_down'`, `severity = 'critical'`, `tenant_id = null`
**Verify single-failure does NOT raise Critical:** After only check 1 failure — no alert created yet

### TC-D-011: Warning alert auto-resolves when condition clears
**Setup:** Active `infra.service_degraded` warning for Reporting Engine
**Action:** Health check job detects Reporting Engine back to healthy
**Expected:** Alert updated: `auto_resolved = true`, `resolved_at` populated, `resolved_reason = 'condition_cleared'`; `warning_count` decreases

### TC-D-012: Critical alert is NOT auto-resolved
**Setup:** Active `auth.brute_force_detected` critical alert
**Action:** Login failures stop; health check job runs multiple cycles
**Expected:** Alert unchanged — `resolved_at = null`, `auto_resolved = false`; must be manually resolved

### TC-D-013: Info alert auto-dismissed after 48 hours
**Setup:** `tenant.new_device_registered` info alert with `created_at` = 49 hours ago, `auto_dismissed = false`
**Action:** `AlertDismissalJob` runs
**Expected:** `auto_dismissed = true`; alert no longer shown in active alerts count

---

## Widget Failure Isolation

### TC-D-014: One widget failure does not break others
**Setup:** Simulate `GET /admin/v1/dashboard/platform-health` returning HTTP 500
**Action:** Load full dashboard
**Expected:**
- KPI cards, Alerts widget, Device Status, Recent Events all load successfully
- Platform Health widget shows red error card with retry button
- Page is not in a full error state

### TC-D-015: Alerts widget failure is high-visibility
**Setup:** Simulate `GET /admin/v1/dashboard/alerts` returning 500
**Expected:** Alerts widget shows red error card — NOT the standard gray "Could not load" state used by other widgets

---

## Provisioning Tenant Visibility

### TC-D-016: Provisioning tenant counted in platform totals but not customer-facing
**Setup:** One provisioning tenant exists
**Action 1:** `GET /admin/v1/dashboard/summary`
**Expected:** Counted in `total_tenants`

**Action 2:** Any `GET /api/v1/*` tenant-facing query
**Expected:** Provisioning tenant does NOT appear

---

## Quick Actions Panel

### TC-D-017: Quick Action hidden when permission absent
**Setup:** Platform account without `platform.tenants.create`
**Action:** Load dashboard
**Expected:** "Create New Tenant" quick action row not rendered — not disabled, not present
