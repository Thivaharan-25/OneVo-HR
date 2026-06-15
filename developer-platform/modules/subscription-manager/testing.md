# Subscription Plans - Testing

## Test Fixtures Required

- Platform user with `platform.subscriptions.manage`
- Platform user with `platform.subscriptions.read` only
- Active `module_catalog` rows for plan-selectable modules
- Inactive `module_catalog` row for negative tests
- Clean subscription plan table for creation tests

---

## Plan Creation

### TC-S-001: Create plan with base modules, optional add-ons, and resource add-ons

**Action:** `POST /admin/v1/subscription-plans`

**Input includes:**

- Plan name, tier, description, active status
- Monthly and annual billing cycles
- Company-size pricing bracket `51-200`
- Shared base storage allocation
- Shared base AI token allowance
- `core_hr` and `leave` as base modules
- `monitoring` as optional module add-on
- Extra Storage Pack as resource-only add-on
- Extra AI Token Pack as resource-only add-on

**Expected:**

- HTTP 201
- `subscription_plans` row created
- `subscription_plan_modules` rows created with correct `package_type`
- `subscription_plan_price_brackets` row created
- `subscription_plan_resource_addons` rows created
- Resource-only add-ons do not create module entitlement rows

### TC-S-002: Module cannot be both base and optional add-on in same plan

**Action:** `POST /admin/v1/subscription-plans` with `monitoring` as both base and optional add-on.

**Expected:** HTTP 422, `code: "duplicate_plan_module_package_type"`

### TC-S-003: Inactive catalog module cannot be selected

**Action:** `POST /admin/v1/subscription-plans` with inactive module `payroll`.

**Expected:** HTTP 422, `code: "inactive_module_not_selectable"`

### TC-S-004: Plan with no base modules rejected

**Action:** `POST /admin/v1/subscription-plans` with no base modules.

**Expected:** HTTP 422, `code: "base_modules_required"`

### TC-S-005: Missing company-size pricing bracket rejected

**Action:** `POST /admin/v1/subscription-plans` with selected size range `51-200` but no pricing row.

**Expected:** HTTP 422, `code: "missing_price_brackets"`

### TC-S-006: Plan creation requires manage permission

**Setup:** Platform user has `platform.subscriptions.read` only.

**Action:** `POST /admin/v1/subscription-plans`

**Expected:** HTTP 403

---

## Duplicate Entitlement And Billing

### TC-S-007: Tenant cannot be entitled twice to same module

**Setup:** Plan includes `leave` as a base module.

**Action:** Tenant upgrade request also selects `leave` as an optional add-on.

**Expected:** HTTP 422, `code: "duplicate_module_entitlement"`

### TC-S-008: Tenant cannot be charged twice for same module

**Setup:** Demo upgrade submit payload contains duplicate `monitoring` add-on rows.

**Action:** `POST /api/v1/demo/upgrade/submit`

**Expected:** HTTP 422, `code: "duplicate_module_charge"`

### TC-S-009: Base-included optional add-ons hidden during demo upgrade

**Setup:** Demo Profile allows `leave`, but selected plan already includes `leave` as base.

**Action:** `GET /api/v1/demo/upgrade/options`

**Expected:** `leave` is not returned as selectable optional add-on.

---

## Resource Limits

### TC-S-010: Storage is one shared tenant pool

**Setup:** Base plan has 100 GB. Selected module add-on contributes 25 GB. Extra Storage Pack contributes 50 GB. Tenant override adds 10 GB.

**Action:** Quote or approve activation.

**Expected:** Tenant storage limit is 185 GB in one shared pool.

### TC-S-011: AI token limit is one shared tenant allowance

**Setup:** Base plan has 100,000 tokens. AI module add-on contributes 50,000. Extra AI Token Pack contributes 200,000.

**Action:** Quote or approve activation.

**Expected:** Tenant AI allowance is 350,000 tokens.

### TC-S-012: Resource-only add-ons do not create module entitlements

**Action:** Activate tenant with Extra Storage Pack and Extra AI Token Pack.

**Expected:** No module entitlement rows are created for resource add-ons; invoice contains resource add-on line items.

---

## Existing Tenant Protection

### TC-S-013: Catalog reference changes do not update existing subscriptions

**Setup:** Tenant already has active subscription snapshot.

**Action:** Update Module Catalog pricing/storage/AI references.

**Expected:** Existing tenant subscription snapshot and resolved limits do not change.

### TC-S-014: Plan price changes do not rewrite existing subscription snapshots

**Setup:** Tenant already has active subscription snapshot.

**Action:** Update plan pricing bracket.

**Expected:** Existing tenant subscription snapshot is unchanged; tenant impact view shows affected tenants.

---

## Cancellation Blocking

### TC-S-015: Unpaid seat dues block cancellation

**Setup:** Monthly tenant has unpaid extra-seat dues.

**Action:** Request cancellation.

**Expected:** HTTP 422, `code: "unpaid_dues_block_cancellation"`

### TC-S-016: Annual unpaid added-seat dues block renewal changes

**Setup:** Annual tenant has unpaid added-seat dues for remaining months.

**Action:** Request renewal change.

**Expected:** HTTP 422, `code: "unpaid_added_seat_dues"`
