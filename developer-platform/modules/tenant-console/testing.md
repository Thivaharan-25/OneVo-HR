# Tenant Console â€” Testing

## Test Fixtures Required

All tests require:
- A seeded `dev_platform_accounts` row (super_admin role)
- A valid platform-admin JWT (`iss: onevo-platform-admin`, `is_active: true`)
- At least one seeded `subscription_plans` row with price brackets for `51-200` size range
- At least one active `payment_gateway_configs` row (provider: paddle, environment: sandbox)

---

## Wizard â€” Step 1: Organization Info

### TC-001: Create provisioning draft â€” happy path
**Precondition:** Operator has `platform.tenants.create`
**Input:** `company_name: "Acme Corp"`, `legal_company_name: "Acme Corp Ltd"`, `domain: "acmecorp.io"`, `industry: "Technology"`, `estimated_employee_count: 120`
**Action:** `POST /admin/v1/tenants`
**Expected:**
- HTTP 201
- Response contains `tenant_code` matching format `TEN-YYYYMMDD-XXXX`
- `tenants` row: `status = 'provisioning'`
- `tenant_provisioning_states` row: `step_1_complete = true`, steps 2â€“4 all `false`
- Tenant does NOT appear in `GET /api/v1/*` (customer-facing) queries

### TC-002: Duplicate domain rejected
**Input:** Domain `acmecorp.io` already exists in `tenants` table
**Action:** `POST /admin/v1/tenants` with same domain
**Expected:** HTTP 409, `code: "domain_taken"`, inline error on Domain field

### TC-003: Missing required field rejected
**Input:** `company_name` omitted
**Action:** `POST /admin/v1/tenants`
**Expected:** HTTP 422, `code: "validation_failed"`, error for `company_name` field

### TC-004: Permission check â€” missing create permission
**Setup:** Platform account has only `platform.tenants.read`
**Action:** `POST /admin/v1/tenants`
**Expected:** HTTP 403, `code: "permission_denied"`

---

## Wizard â€” Step 3: Subscription

### TC-005: Subscription saves and syncs entitlements
**Precondition:** Tenant from TC-001 exists in provisioning state
**Action:** `PATCH /admin/v1/tenants/{id}/subscription` with `plan_id`, `selected_module_keys: ["core_hr","leave"]`, `collection_mode: "gateway"`, `payment_gateway_id: "{gatewayId}"`
**Expected:**
- HTTP 200, `step_3_complete: true`
- `tenant_subscriptions` row created with `is_current = true`
- `tenant_module_entitlements` rows created for `core_hr` and `leave` with `status = 'provisioning'`
- Both `calculated_price` and `override_price` stored separately (override_price = null when no override given)

### TC-006: Plan selection does NOT accept `plan_id` on `POST /admin/v1/tenants` (Step 1)
**Action:** `POST /admin/v1/tenants` with body including `plan_id`
**Expected:** HTTP 422 or plan_id field silently ignored â€” `tenants` row has no plan assignment after Step 1

### TC-007: Override price requires reason
**Action:** `PATCH /admin/v1/tenants/{id}/subscription` with `override_price: 3500`, `override_reason: null`
**Expected:** HTTP 422, error on `override_reason` field: "Reason is required when overriding the calculated price."

### TC-008: Manual collection requires billing evidence
**Action:** `PATCH /admin/v1/tenants/{id}/subscription` with `collection_mode: "manual"`, no `billing_evidence_reference` and no `billing_evidence_file_id`
**Expected:** HTTP 422, error: "Billing evidence or reference is required for manual collection."

### TC-009: AI token limit required when AI modules selected
**Input:** `selected_module_keys: ["chat_ai"]`, `ai_monthly_token_limit: null`
**Action:** `PATCH /admin/v1/tenants/{id}/subscription`
**Expected:** HTTP 422, error: "AI token limit is required when AI-capable modules are included."

---

## Activation Guard

### TC-010: Activation fails when steps incomplete
**Setup:** Tenant with only Step 1 complete (`step_2_complete = false`)
**Action:** `PATCH /admin/v1/tenants/{id}/provision/confirm`
**Expected:**
- HTTP 422
- Response `blockers` array contains `code: "provisioning_incomplete"` or specific missing-step codes
- `tenants.status` remains `'provisioning'`
- Tenant still invisible to `/api/v1/*`

### TC-011: Activation succeeds when all steps complete
**Setup:** Tenant with all 4 steps complete in `tenant_provisioning_states`
**Action:** `PATCH /admin/v1/tenants/{id}/provision/confirm`
**Expected:**
- HTTP 200
- `tenants.status = 'active'`
- `tenant_module_entitlements` rows for selected modules: `status = 'active'`
- If `send_invite_on_activation = true`: invite email sent (verify `users.invite_sent_at` is set)
- Audit log entry: `action = 'tenant.activated'`
- Tenant now returns from `GET /api/v1/*` tenant-scoped queries

### TC-012: Provisioning tenant invisible to customer-facing API
**Setup:** Tenant in `status = 'provisioning'`
**Action:** `GET /api/v1/tenants` (customer-facing namespace) or any tenant-scoped endpoint
**Expected:** Provisioning tenant does NOT appear in any result

---

## Tenant Status Transitions

### TC-013: Suspend active tenant
**Precondition:** Tenant `status = 'active'`, operator has `platform.tenants.suspend`
**Action:** `PATCH /admin/v1/tenants/{id}/status` `{"status":"suspended","reason":"Non-payment after 3 retries."}`
**Expected:**
- HTTP 200, `new_status: "suspended"`, `sessions_invalidated` > 0
- `tenants.status = 'suspended'`
- All active user sessions for this tenant invalidated
- Tenant does not appear in `/api/v1/*` results
- Audit log: `action = 'tenant.suspended'` with reason

### TC-014: Suspend requires reason of min length
**Action:** `PATCH /admin/v1/tenants/{id}/status` `{"status":"suspended","reason":"ok"}`
**Expected:** HTTP 422, error: reason too short

### TC-015: Unsuspend restores access
**Precondition:** Tenant `status = 'suspended'`
**Action:** `PATCH /admin/v1/tenants/{id}/status` `{"status":"active"}`
**Expected:** `tenants.status = 'active'`, tenant appears again in tenant-facing queries

### TC-016: Cannot activate directly from suspended (must go through unsuspend)
**Action:** `PATCH /admin/v1/tenants/{id}/status` `{"status":"provisioning"}` on a suspended tenant
**Expected:** HTTP 409, `code: "invalid_status_transition"`

---

## Impersonation

### TC-017: Impersonation requires explicit permission
**Setup:** Platform account with `platform.tenants.read` but NOT `platform.tenants.impersonate`
**Action:** `POST /admin/v1/tenants/{id}/impersonate`
**Expected:** HTTP 403, `code: "impersonation_permission_required"`

### TC-018: Impersonation token is short-lived and non-renewable
**Precondition:** Account has `platform.tenants.impersonate`
**Action:** `POST /admin/v1/tenants/{id}/impersonate` with valid target_user_id and reason
**Expected:**
- HTTP 200, `impersonation_token` present
- Token `exp` claim = `iat + 900` seconds exactly (15 minutes)
- Token carries `impersonation: true` claim
- Audit log entry written BEFORE token is returned

### TC-019: Impersonation audit log is mandatory â€” cannot be bypassed
**Action:** Inspect `audit_log` table after TC-018
**Expected:** Row exists with `action = 'tenant.impersonated'`, `actor_id`, `target_tenant_id`, `target_user_id`, `reason`, `source_ip`, `session_expiry`

### TC-020: Impersonation token rejected at admin endpoints
**Action:** Use impersonation token to call `PATCH /admin/v1/tenants/{id}/status`
**Expected:** HTTP 403 â€” impersonation tokens are scoped only to `[AllowImpersonation]`-tagged endpoints

### TC-021: Cannot impersonate in a suspended tenant
**Setup:** Target tenant `status = 'suspended'`
**Action:** `POST /admin/v1/tenants/{id}/impersonate`
**Expected:** HTTP 422, `code: "impersonation_target_inactive"`

---

## Multi-Tenant Email Rule

### TC-022: Same email can be invited to multiple tenants
**Action:** Create Tenant A and Tenant B both with admin email `owner@company.com`
**Action:** `POST /admin/v1/tenants/{tenantA_id}/invite-admin` and `POST /admin/v1/tenants/{tenantB_id}/invite-admin`
**Expected:**
- Both succeed (HTTP 200)
- Two separate `users` rows created â€” one per tenant â€” each with `tenant_id` scoped correctly
- Accepting Tenant A invite does not affect Tenant B access

---

## Tenant List Filters

### TC-023: Status filter returns correct tenants
**Action:** `GET /admin/v1/tenants?status=suspended`
**Expected:** Only tenants with `status = 'suspended'` in response; provisioning/active/cancelled not included

### TC-024: Search by domain
**Action:** `GET /admin/v1/tenants?search=acmecorp`
**Expected:** Tenant with domain `acmecorp.io` appears; partial match on name or domain works

