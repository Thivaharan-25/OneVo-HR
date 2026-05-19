# Module Catalog Manager — Testing

## Test Fixtures Required

- Platform account with `platform.module_catalog.manage`
- Platform account with `platform.module_catalog.read` only
- `module_catalog` seeded with all Phase 1 modules
- `permissions` table seeded with permission codes per module
- 2 active tenants with different entitlements
- At least 1 active subscription plan referencing `core_hr`

---

## Module Catalog CRUD

### TC-MC-001: Module key is immutable after creation
**Setup:** Module `new_module` created
**Action:** `PATCH /admin/v1/modules/catalog/new_module` with body attempting to change `module_key`
**Expected:** `module_key` field is ignored or HTTP 422 — key is permanent

### TC-MC-002: Deactivated module excluded from new plan creation
**Setup:** Module `leave` deactivated (`is_active = false`)
**Action:** `POST /admin/v1/subscription-plans` with `included_module_keys: ["core_hr", "leave"]`
**Expected:** HTTP 422 — `leave` is inactive and cannot be included in new plans. Existing tenant entitlements using `leave` are preserved and not removed.

### TC-MC-003: Phase 2 module cannot be included in Phase 1 plans
**Setup:** Module `payroll` has `phase = 2`
**Action:** `POST /admin/v1/subscription-plans` with `included_module_keys: ["core_hr", "payroll"]`
**Expected:** HTTP 422 — Phase 2 modules cannot be sold in Phase 1 plans

---

## Pricing

### TC-MC-004: Updating module price creates price history entry
**Setup:** `core_hr` module has unit price `8.00` for `51-200` size range
**Action:** `PATCH /admin/v1/modules/catalog/core_hr/pricing` — change to `9.50` for `51-200`
**Expected:**
- `module_catalog` price bracket updated to `9.50`
- `module_catalog_price_history` row inserted: `previous_unit_price = 8.00`, `new_unit_price = 9.50`, `changed_by_id`, `changed_at`

### TC-MC-005: Price update does NOT rewrite existing tenant subscription snapshots
**Setup:** Tenant T has `tenant_subscriptions.calculated_price = 4200.00` based on old `core_hr` price of `8.00`
**Action:** Update `core_hr` price to `9.50`
**Expected:**
- Tenant T's `tenant_subscriptions.calculated_price` remains `4200.00` unchanged
- `GET /admin/v1/modules/catalog/core_hr/tenant-impact` shows tenant T as having a "stale price" warning — not automatically repriced

### TC-MC-006: Tenant impact preview is accurate before pricing change
**Setup:** 5 tenants entitled to `core_hr`. 3 have active subscriptions, 2 are provisioning.
**Action:** `GET /admin/v1/modules/catalog/core_hr/tenant-impact`
**Expected:** Response shows exactly 5 affected tenants. Count matches actual `tenant_module_entitlements` rows for `core_hr`.

---

## Permission Ownership

### TC-MC-007: Permission cannot be owned by two modules simultaneously
**Setup:** `leave:approve` owned by module `leave`
**Action:** `PUT /admin/v1/modules/catalog/core_hr/permissions` including `leave:approve`
**Expected:** HTTP 422 — `leave:approve` already owned by `leave`; must be removed from `leave` first

### TC-MC-008: Removing permission ownership updates tenant permission catalog
**Setup:** `leave:approve` owned by `leave`. Tenant T entitled to `leave`. `GET /admin/v1/tenants/{id}/permissions/catalog` includes `leave:approve`.
**Action:** Remove `leave:approve` from leave module via `PUT /admin/v1/modules/catalog/leave/permissions` (omit `leave:approve`)
**Expected:** `GET /admin/v1/tenants/{id}/permissions/catalog` no longer includes `leave:approve`

---

## Integration Catalog — Create

### TC-MC-009: Create integration entry — happy path
**Action:** `POST /admin/v1/integrations/catalog`
```json
{
  "integration_key": "my_calendar_tool",
  "display_name": "My Calendar Tool",
  "category": "customer_oauth",
  "auth_type": "oauth2",
  "oauth_app_provider": "google",
  "required_module_condition": "any",
  "required_module_keys": ["calendar"],
  "is_active": true
}
```
**Expected:**
- HTTP 201
- `integration_catalog` row created
- Audit log: `action = 'integration_catalog.created'`

### TC-MC-010: Integration key is permanent after tenant connects
**Setup:** Integration `github` exists. Tenant has `tenant_integration_credentials` row for `github`.
**Action:** `PATCH /admin/v1/integrations/catalog/github` attempting to change `integration_key`
**Expected:** `integration_key` field immutable — cannot change after connections exist

### TC-MC-011: Integration condition change disconnects tenants that no longer qualify
**Setup:**
- Integration `slack` requires ANY of `["chat", "chat_ai", "integrations"]`
- Tenant T entitled to `chat` only — qualifies
- Tenant T has `slack` connected (`status = 'connected'`)
**Action:** `PATCH /admin/v1/integrations/catalog/slack` — change required to ALL of `["chat_ai", "integrations"]`
**Expected:**
- Tenant T no longer qualifies (doesn't have `chat_ai` or `integrations`)
- `tenant_integration_credentials` for tenant T + `slack`: `status = 'disconnected'`
- Warning alert raised: `integration.access_revoked` for tenant T

---

## Module-Integration Linking

### TC-MC-012: Link integration to module — appears in module detail
**Action:** `POST /admin/v1/modules/catalog/work_management/integrations` `{"integration_key": "github", "link_type": "required"}`
**Expected:**
- `module_integration_links` row: `(work_management, github, required)`
- `GET /admin/v1/modules/catalog/work_management/integrations` includes `github`

### TC-MC-013: Unlink integration shows impact count
**Setup:** 5 tenants entitled to `work_management` with `github` connected. No other module links `github`.
**Action:** `DELETE /admin/v1/modules/catalog/work_management/integrations/github`
**Expected:** Response includes `integrations_affected: 5` warning before confirming. After confirmation: all 5 tenants have `github` disconnected.

### TC-MC-014: Read-only account cannot manage integration catalog
**Setup:** Account with `platform.module_catalog.read` only
**Action:** `POST /admin/v1/integrations/catalog`
**Expected:** HTTP 403

---

## Logo Upload

### TC-MC-015: Integration logo upload returns logo_url
**Action:** `POST /admin/v1/uploads/integration-logo` with valid PNG file (< 500KB)
**Expected:**
- HTTP 200
- Response: `{"logo_url": "https://storage.onevo.io/integration-logos/..."}`
- File accessible at the returned URL

### TC-MC-016: Oversized logo upload rejected
**Action:** `POST /admin/v1/uploads/integration-logo` with 600KB PNG
**Expected:** HTTP 422 — file exceeds 500KB limit
