# App Catalog Manager — Testing

## Test Fixtures Required

- Platform account with `platform.app_catalog.manage`
- Platform account with `platform.app_catalog.read` only
- At least 5 observed app candidates in `observed_applications`
- At least 1 existing catalog entry

---

### TC-APP-001: Process name must be unique in catalog
**Setup:** Catalog entry for `Microsoft Edge` already exists
**Action:** `POST /admin/v1/app-catalog` with `process_name: "msedge.exe"` (same as existing)
**Expected:** HTTP 409 — process name already in catalog

### TC-APP-002: Create/update requires platform.app_catalog.manage
**Setup:** Account with `platform.app_catalog.read` only
**Action:** `POST /admin/v1/app-catalog`
**Expected:** HTTP 403

### TC-APP-003: Bulk approve creates entries and links observations transactionally
**Setup:** 3 uncatalogued observed apps selected for bulk approve
**Action:** `POST /admin/v1/app-catalog/bulk-approve` with array of candidate IDs
**Expected:**
- 3 new `app_catalog` rows created
- 3 `observed_applications` rows updated: `status = 'catalogued'`
- All 3 insertions and updates happen atomically — if one fails, none are committed
- Audit log: single `action = 'app_catalog.bulk_approved'` entry with count

### TC-APP-004: Dismissed candidates do not reappear in uncatalogued list
**Setup:** Candidate dismissed via `PATCH /admin/v1/app-catalog/uncatalogued/{id}` `{"status": "dismissed"}`
**Action:** `GET /admin/v1/app-catalog/uncatalogued`
**Expected:** Dismissed candidate absent from results — filter applied correctly

### TC-APP-005: Analytics are aggregate counts only — no employee-level data
**Action:** `GET /admin/v1/analytics/modules` (module adoption includes app usage data)
**Expected:** Usage counts are per-app totals across all tenants. No individual employee names, specific app session details, or per-user breakdowns.

### TC-APP-006: Catalog writes are audit-logged
**Action:** `POST /admin/v1/app-catalog` creating new entry
**Expected:** Audit log: `action = 'app_catalog.created'`, actor, app name, process name

### TC-APP-007: `is_public` toggle affects tenant-facing app visibility
**Setup:** Catalog entry `is_public = false`
**Action:** `PATCH /admin/v1/app-catalog/{id}` `{"is_public": true}`
**Expected:** Entry now visible to tenant-facing app allowlist configurations. Audit log entry for toggle change.
