# Subscription Manager - Testing

## Test Fixtures Required

- Platform account with `platform.subscriptions.manage`
- Platform account with `platform.subscriptions.read` only (billing manager, read-only)
- At least one seeded `module_catalog` row per Phase 1 module key
- No active plans initially (clean state for plan creation tests)

---

## Plan Creation

### TC-S-001: Create plan - happy path
**Input:**
```json
{
  "name": "Business Plan Q2",
  "tier": "business",
  "included_module_keys": ["core_hr", "leave", "monitoring", "workforce"],
  "employee_count_tiers": ["51-200"],
  "price_tiers": [{ "employee_count_tier": "51-200", "module_prices": { "core_hr": 8.00, "leave": 3.00, "monitoring": 6.00, "workforce": 4.00 }, "calculated_monthly_total": 2625.00 }],
  "supported_commercial_models": ["subscription"],
  "supported_billing_cycles": ["monthly","annual"],
  "is_active": true
}
```
**Action:** `POST /admin/v1/subscription-plans`
**Expected:**
- HTTP 201
- `subscription_plans` row created
- `subscription_plan_price_tiers` row created for `51-200`
- `calculated_monthly_total` stored; `override_monthly_total = null`

### TC-S-002: Duplicate plan name rejected
**Setup:** "Business Plan Q2" plan already active
**Action:** `POST /admin/v1/subscription-plans` with same name
**Expected:** HTTP 409, `code: "plan_name_taken"`

### TC-S-003: Plan with no modules rejected
**Action:** `POST /admin/v1/subscription-plans` with `included_module_keys: []`
**Expected:** HTTP 422, `code: "no_modules_selected"`

### TC-S-004: Plan missing price bracket for selected size range rejected
**Input:** `target_employee_count_tiers: ["51-200","201-500"]` but `price_tiers` only contains `51-200`
**Expected:** HTTP 422, `code: "missing_price_tiers"` - bracket required for each selected range

### TC-S-005: Phase 2 modules cannot be included in Phase 1 plans
**Input:** `included_module_keys: ["core_hr", "payroll"]` - payroll is Phase 2
**Expected:** HTTP 422, `code: "phase2_modules_rejected"`, error body lists the rejected keys

**Phase 2 keys that must all be rejected:** `payroll`, `performance`, `skills`, `learning`, `recruitment`, `hr_docs`, `grievance`, `expense`

Repeat this test individually for each Phase 2 key - each must be rejected, not silently dropped.

### TC-S-006: Plan creation requires manage permission
**Setup:** Account with `platform.subscriptions.read` only
**Action:** `POST /admin/v1/subscription-plans`
**Expected:** HTTP 403

---

## Price Calculation and Override

### TC-S-007: Calculated price and override price stored separately
**Action:** `POST /admin/v1/subscription-plans` with `calculated_monthly_total: 2625.00` and `override_monthly_total: 2500.00`, `override_reason: "Launch discount for Q2."`
**Expected:**
- `subscription_plan_price_tiers.calculated_monthly_total = 2625.00`
- `subscription_plan_price_tiers.override_monthly_total = 2500.00`
- `override_monthly_total` is stored - `calculated_monthly_total` is NOT overwritten or deleted

### TC-S-008: Override without reason rejected
**Action:** `PATCH /admin/v1/subscription-plans/{id}` with `override_monthly_total: 2000.00`, `override_reason: null`
**Expected:** HTTP 422, error on override_reason field

### TC-S-009: Plan update creates price history entry
**Setup:** Existing plan with `core_hr` unit price at `8.00` for `51-200`
**Action:** `PATCH /admin/v1/subscription-plans/{id}` changing `core_hr` price to `9.50`
**Expected:**
- `subscription_plan_price_history` row inserted: `module_key = 'core_hr'`, `previous_unit_price = 8.00`, `new_unit_price = 9.50`, `changed_by_id` set
- Existing `tenant_subscriptions` snapshots for tenants already on this plan are NOT changed

### TC-S-010: Plan deactivation blocks new tenant assignment
**Action:** `PATCH /admin/v1/subscription-plans/{id}` with `is_active: false`
**Expected:** Plan no longer appears in `GET /admin/v1/subscription-plans` results visible to provisioning wizard; existing tenant assignments preserved with their commercial snapshots intact

---

## Payment Gateway Configuration

### TC-S-011: Gateway creation encrypts secrets - never returned in response
**Action:** `POST /admin/v1/payment-gateways` with `provider: "paddle"`, `credentials.api_key: "pdl_test_abc123"`, `credentials.webhook_secret: "pdl_ntfset_xyz"`
**Expected:**
- HTTP 201
- Response body does NOT contain `api_key`, `webhook_secret`, or `credentials` object
- `payment_gateway_configs.config_encrypted` in DB is not plaintext (verify it differs from input)

### TC-S-012: Gateway GET response never returns secrets
**Action:** `GET /admin/v1/payment-gateways/{id}`
**Expected:** Response contains `provider`, `name`, `country_codes`, `environment`, `is_active` - no `api_key`, `merchant_secret`, or `webhook_secret`

### TC-S-013: Paddle fields validate by provider
**Action:** `POST /admin/v1/payment-gateways` with `provider: "paddle"` but omitting `credentials.api_key`
**Expected:** HTTP 422, error: api_key required for Paddle provider

### TC-S-014: PayHere fields validate by provider
**Action:** `POST /admin/v1/payment-gateways` with `provider: "payhere"` but omitting `credentials.merchant_id`
**Expected:** HTTP 422, error: merchant_id required for PayHere provider

### TC-S-015: Rotate secrets replaces all encrypted fields atomically
**Action:** `PATCH /admin/v1/payment-gateways/{id}/rotate-secrets` with full new credentials object
**Expected:**
- `payment_gateways.config_encrypted` updated
- Audit log: `action = 'gateway.secrets_rotated'`, actor, gateway_id, rotation_reason

### TC-S-016: Cannot deactivate gateway with active tenant assignments
**Setup:** Gateway has 5 active tenant_subscriptions referencing it
**Action:** `DELETE /admin/v1/payment-gateways/{id}`
**Expected:** HTTP 409, `code: "gateway_in_use"`, count of active assignments in error detail

---

## Paddle Webhook Handling

### TC-S-017: Webhook with invalid signature is rejected
**Action:** `POST /webhooks/paddle` with forged or mismatched `Paddle-Signature` header
**Expected:** HTTP 400 - no processing, no DB changes

### TC-S-018: transaction.completed marks invoice Paid
**Setup:** Invoice with `status = 'open'`, `paddle_transaction_id = 'txn_test_abc'`
**Action:** `POST /webhooks/paddle` with `transaction.completed` event, `data.id: "txn_test_abc"`
**Expected:**
- `subscription_invoices.status = 'paid'`
- `subscription_invoices.paid_at` set
- `subscription_invoices.paddle_invoice_url` set from event data
- If active `billing.payment_failed` alert existed for this tenant: alert auto-resolved

### TC-S-019: Duplicate Paddle event is idempotent
**Setup:** `webhook_event_queue` already has `event_id = 'ntf_123'` with `status = 'completed'`
**Action:** `POST /webhooks/paddle` with same `ntf_123` event
**Expected:** HTTP 200 immediately; no duplicate DB changes; `attempt_count` not incremented

### TC-S-020: Failed webhook reaches dead-letter after 5 retries
**Setup:** Webhook event that causes processing error on every attempt
**Action:** `WebhookRetryJob` retries event up to 5 times
**Expected:**
- After 5 failures: `webhook_event_queue.status = 'dead_letter'`
- `platform_alerts` row created: `alert_code = 'billing.webhook_processing_failed'`, `severity = 'critical'`

---

## Invoice Lifecycle

### TC-S-021: Manual invoice can be marked paid with evidence
**Setup:** Invoice `status = 'open'`, `payment_method = null`
**Action:** `PATCH /admin/v1/invoices/{id}/mark-paid` with `payment_reference: "WIRE-2025-0042"`, `payment_date: "2025-05-19"`
**Expected:** `status = 'paid'`, `paid_at` set, `payment_reference` saved, audit log entry

### TC-S-022: Mark-paid requires evidence for manual invoices
**Action:** `PATCH /admin/v1/invoices/{id}/mark-paid` with no `payment_reference` and no `evidence_file_id`
**Expected:** HTTP 422, `code: "missing_payment_evidence"`

### TC-S-023: Cannot void an already-paid invoice
**Setup:** Invoice `status = 'paid'`
**Action:** `PATCH /admin/v1/invoices/{id}/void`
**Expected:** HTTP 422, `code: "invoice_already_paid"`

---

## Dunning

### TC-S-024: Dunning auto-suspension fires after grace period
**Setup:** Tenant subscription with `payment_attempt_count = 3` (all 3 retries failed) and `next_billing_date` 7+ days in the past; `payment_status = 'overdue'`
**Action:** `DunningJob` runs
**Expected:**
- `tenants.status = 'suspended'`
- Audit log: `action = 'tenant.auto_suspended_dunning'`, actor_type = 'system'
- Active `billing.payment_failed_final` critical alert exists for this tenant

### TC-S-025: Payment exception halts dunning
**Setup:** Tenant with `payment_exception_start <= today <= payment_exception_end` in `tenant_subscriptions`
**Action:** `DunningJob` runs
**Expected:** Tenant is NOT suspended; `DunningJob` skips tenants in active exception window

---

## Billable User Count

### Test Fixtures Required
- Tenant with Package 1 active
- 5 employees: 2 with monitoring enabled, 1 with monitoring fully disabled, 1 deactivated, 1 invited (not accepted)
- `monitoring_feature_toggles` rows set accordingly

### TC-S-026: Monitoring-disabled employee excluded from Package 1 billing count
**Setup:** Employee `emp-3` has all monitoring feature toggles set to `false` (both tenant-default and employee override = off)
**Action:** Billing snapshot job runs for end of month
**Expected:**
- `billing_snapshots.billable_user_count_p1` = 2 (only the 2 with monitoring enabled)
- `emp-3` does NOT appear in the billable count
- `emp-3` does appear in a separate `monitoring_disabled_users` count on the snapshot for audit

### TC-S-027: Deactivated user excluded from billing count
**Setup:** Employee `emp-4` has `users.status = 'deactivated'`
**Action:** Billing snapshot job runs
**Expected:** `emp-4` not included in `billable_user_count_p1`

### TC-S-028: Invited (not yet accepted) user excluded from billing count
**Setup:** Employee `emp-5` has `users.status = 'invited'`
**Action:** Billing snapshot job runs
**Expected:** `emp-5` not included in `billable_user_count_p1`

### TC-S-029: Active user with monitoring enabled is counted
**Setup:** Employee `emp-1` has `employees.status = 'active'`, `users.status = 'active'`, at least one monitoring toggle enabled
**Action:** Billing snapshot job runs
**Expected:** `emp-1` IS included in `billable_user_count_p1`

### TC-S-030: Billing snapshot is idempotent
**Setup:** Billing snapshot already exists for `tenant_id + billing_period_start`
**Action:** Billing snapshot job runs again for same period
**Expected:** No duplicate `billing_snapshots` row - existing row is upserted; `billable_user_count_p1` reflects current state

---

## Tenant Storage Limit

### TC-S-031: Storage is stored as shared tenant pool, not per-module
**Action:** `PATCH /admin/v1/tenants/{id}/subscription` with `tenant_storage_limit_gb: 250`
**Expected:**
- `tenant_subscriptions.tenant_storage_limit_gb = 250`
- No per-module storage columns written
- All modules (HR docs, screenshots, payslips, attachments) draw from this single value

### TC-S-032: Storage limit missing is rejected at activation
**Setup:** Tenant provisioning in progress; Step 3 saved without `tenant_storage_limit_gb`
**Action:** `PATCH /admin/v1/tenants/{id}/provision/confirm`
**Expected:** HTTP 422, `code: "missing_storage_limit"`

### TC-S-033: Storage at 100% blocks file uploads
**Setup:** `tenant_subscriptions.tenant_storage_limit_gb = 10`; tenant has used 10 GB
**Action:** Employee attempts to upload a file via `POST /api/v1/files`
**Expected:** HTTP 413, `code: "storage_limit_exceeded"`. Existing files are NOT deleted or affected.

### TC-S-034: Storage warning alert raised at 80%
**Setup:** Tenant storage at 8 GB of 10 GB limit (80%)
**Action:** Storage check background job runs (or file upload triggers check)
**Expected:** Warning platform alert raised: `code = 'storage.limit_approaching'`, `severity = 'warning'`; no upload blocked at 80%

---

## Plan Change Rules

### TC-S-035: Module added - entitlement effective immediately
**Setup:** Active tenant without `chat` module
**Action:** `PUT /admin/v1/tenants/{id}/modules` with `{ "module_key": "chat", "state": "subscription_included", "source": "manual_override" }`
**Expected:**
- `tenant_module_entitlements` row upserted: `module_key = 'chat'`, `state = 'subscription_included'`, `is_access_granting = true`
- Tenant permission catalog updated to include chat permissions immediately
- No billing period delay

### TC-S-036: Module removed - entitlement disabled at end of billing period, not immediately
**Setup:** Active tenant with `chat` module, `billing_period_end = 2025-06-30`
**Action:** Operator sets `chat` module state to `disabled` via `PUT /admin/v1/tenants/{id}/modules`
**Expected:**
- `tenant_module_entitlements.state = 'disabled'` effective from `billing_period_end`
- Tenant retains chat access until `billing_period_end`
- Data and configuration preserved until that date

### TC-S-037: Cancellation - cancel_at_period_end set; tenant retains access
**Setup:** Active subscription tenant
**Action:** `POST /api/v1/billing/subscription/cancel` with `{ "reason": "No longer needed." }`
**Expected:**
- `tenant_subscriptions.cancel_at_period_end = true`
- `tenant_subscriptions.cancellation_requested_at` set to now
- `tenants.status` remains `'active'` - NOT immediately changed
- Tenant retains full module access until `billing_period_end`
- Info alert raised: `billing.cancellation_requested`

### TC-S-038: Cancellation cannot be reversed by tenant
**Setup:** Tenant subscription with `cancel_at_period_end = true`
**Action:** Tenant user calls `DELETE /api/v1/billing/subscription/cancel` (or equivalent reversal endpoint)
**Expected:** HTTP 403 or 422 - reversal requires platform admin action only

### TC-S-039: Data retained 90 days after billing_period_end
**Setup:** Tenant with `tenants.status = 'cancelled'`; `billing_period_end` was 91 days ago
**Action:** Data retention / cleanup job runs
**Expected:** Tenant data deletion job queued or executed; after completion all tenant records soft-deleted or purged per retention policy

### TC-S-040: Restart within 90-day window - data intact
**Setup:** Tenant with `tenants.status = 'cancelled'`; `billing_period_end` was 45 days ago; data still present
**Action:** Platform admin re-activates tenant via `PATCH /admin/v1/tenants/{id}/unsuspend` (or reactivation endpoint)
**Expected:**
- `tenants.status = 'active'`
- All prior tenant data still accessible
- New `billing_start_date` set from reactivation date

---

## Usage Limits

### TC-S-041: AI token limit - warning at 80%
**Setup:** `tenant_subscriptions.ai_token_limit_per_month = 1000000`; tenant has consumed 800,000 tokens this month
**Action:** AI token consumption check runs (triggered on token use or background sweep)
**Expected:** Warning alert raised: `code = 'ai_tokens.limit_approaching'`, `severity = 'warning'`; AI features NOT blocked yet

### TC-S-042: AI token limit - features blocked at 100%
**Setup:** Tenant has consumed 1,000,000 of 1,000,000 tokens
**Action:** Tenant user attempts to use Chat AI
**Expected:** HTTP 402 or 429, `code: "ai_token_limit_exceeded"`; Chat AI returns user-facing message; platform admin alert raised: `code = 'ai_tokens.limit_exceeded'`, `severity = 'critical'`

### TC-S-043: No device-based billing - device count not used in billing snapshot
**Setup:** Tenant with 10 registered agents (`registered_agents`) and 5 active employees with monitoring enabled
**Action:** Billing snapshot job runs
**Expected:**
- `billing_snapshots.billable_user_count_p1 = 5` (employee-based)
- No `billable_device_count` column written or used
- Invoice line items reference user quantity, not device quantity

