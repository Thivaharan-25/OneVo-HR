# Tenant Runtime Overrides — Testing

## Test Fixtures Required

- Platform account with `platform.runtime_flags.manage`
- Platform account with `platform.runtime_flags.read` only (global flag read-only)
- Platform account with `platform.tenants.feature_overrides.manage`
- Platform account with `platform.tenants.feature_overrides.read` only (tenant override read-only)
- At least 2 active tenants in `active` status
- At least 1 active module in `module_catalog`
- Clean `feature_flags` table (no pre-existing flags) for creation tests
- Seeded `module_features` rows for any tenant-facing product flags under test

---

## Flag Creation

### TC-FF-001: Create flag — happy path
**Setup:** Account with `platform.runtime_flags.manage`
**Input:** `flag_key: "chat_ai.streaming_responses"`, `default_value: false`, `rollout_percentage: 0`, `module_key: "chat_ai"`, `phase: 1`
**Action:** `POST /admin/v1/feature-flags`
**Expected:**
- HTTP 201
- `feature_flags` row created with exact values
- `rollout_percentage = 0`
- Audit log: `action = 'feature_flag.created'`, `actor_id` set, `default_value = false`

### TC-FF-002: Duplicate flag key rejected
**Setup:** `chat_ai.streaming_responses` flag already exists
**Action:** `POST /admin/v1/feature-flags` with same `flag_key`
**Expected:** HTTP 409, `code: "flag_key_taken"`

### TC-FF-003: Invalid rollout percentage rejected
**Input:** `rollout_percentage: 101`
**Action:** `POST /admin/v1/feature-flags`
**Expected:** HTTP 422, `code: "invalid_rollout_percentage"` — must be 0–100

### TC-FF-004: Rollout percentage has no effect when default_value = false
**Setup:** Flag with `default_value: false`, `rollout_percentage: 80`
**Action:** `GET /admin/v1/tenants/{tenantId}/feature-flags/{flagKey}`
**Expected:** Tenant receives `value: false` — rollout % is irrelevant when default is OFF

### TC-FF-005: Read-only account cannot create flags
**Setup:** Account with `platform.runtime_flags.read` only
**Action:** `POST /admin/v1/feature-flags`
**Expected:** HTTP 403

---

## Global Toggle

### TC-FF-006: Toggle default value requires reason
**Setup:** Account with `platform.runtime_flags.manage`
**Action:** `PATCH /admin/v1/feature-flags/{flagKey}` with `default_value: true`, `reason: null`
**Expected:** HTTP 422 — reason is required when changing `default_value`

### TC-FF-007: Toggle default ON — affects tenants without override
**Setup:** 10 active tenants, none with override for this flag. Flag: `default_value: false`, `rollout_percentage: 0`
**Action:** `PATCH /admin/v1/feature-flags/{flagKey}` `{"default_value": true, "rollout_percentage": 100, "reason": "Full rollout approved"}`
**Expected:**
- `feature_flags.default_value = true`, `rollout_percentage = 100`
- All 10 tenants now evaluate flag as `true` on next request
- Audit log: `action = 'feature_flag.default_changed'`, `previous_value: false`, `new_value: true`, `reason` recorded

### TC-FF-008: Rollout percentage — deterministic hash
**Setup:** Flag `default_value: true`, `rollout_percentage: 50`. 100 tenants, no overrides.
**Action:** Read flag value for each tenant via `GET /admin/v1/tenants/{id}/feature-flags/{flagKey}`
**Expected:** Approximately 50 tenants receive `true`, 50 receive `false`. Same tenant ALWAYS gets the same result — calling again returns identical value. Not random per-request.

### TC-FF-009: Flag change is audit-logged with previous state
**Action:** `PATCH /admin/v1/feature-flags/{flagKey}` changing `rollout_percentage` from 10 to 30
**Expected:** Audit log entry includes `previous_rollout_percentage: 10`, `new_rollout_percentage: 30`, actor, timestamp

---

## Per-Tenant Override

### TC-FF-010: Tenant override wins over global default regardless of rollout %
**Setup:** Account with `platform.tenants.feature_overrides.manage`. Flag `default_value: false`, `rollout_percentage: 0` (all tenants get OFF by default)
**Action:** `PATCH /admin/v1/tenants/{tenantId}/feature-flags/{flagKey}` `{"value": true, "reason": "Beta partner"}`
**Expected:**
- `feature_flag_overrides` row created: `value = true`, `tenant_id`, `granted_by_id`, `reason`
- `GET /admin/v1/tenants/{tenantId}/feature-flags/{flagKey}` returns `value: true` — override wins
- Other tenants without override still get `false`

### TC-FF-011: Removing override falls back to global evaluation
**Setup:** Tenant has explicit override `value: true` for a flag with `default_value: false`
**Action:** `DELETE /admin/v1/tenants/{tenantId}/feature-flags/{flagKey}`
**Expected:**
- `feature_flag_overrides` row deleted
- Tenant now evaluates flag via rollout % hash — if hash puts them in OFF segment, they get `false`
- Audit log: `action = 'feature_flag.tenant_override_removed'`

### TC-FF-012: Override on non-entitled module is rejected
**Setup:** Tenant not entitled to `chat_ai` module. Flag `chat_ai.streaming_responses` exists.
**Action:** `PATCH /admin/v1/tenants/{tenantId}/feature-flags/chat_ai.streaming_responses`
**Expected:** HTTP 422, `code: "module_not_entitled"` — cannot override a flag for a module the tenant doesn't have

---

## Module Runtime Disable

### TC-FF-013: Runtime disable does not change billing
**Setup:** Tenant entitled to `chat_ai` with `sales_state = 'subscription_included'`
**Action:** `PATCH /admin/v1/tenants/{tenantId}/modules/chat_ai/runtime-status` `{"enabled": false, "reason": "Investigating inappropriate content"}`
**Expected:**
- `tenant_module_entitlements.runtime_override = false`
- `tenant_module_entitlements.sales_state` UNCHANGED — still `subscription_included`
- `tenant_subscriptions` UNCHANGED — billing unaffected
- Audit log: `action = 'module.runtime_disabled'`

### TC-FF-014: Runtime disable with connected integrations shows warning and disconnects
**Setup:** Tenant has `chat_ai` entitled. `ms_teams` integration connected (`tenant_integration_credentials.status = 'connected'`). `ms_teams` requires `chat_ai` module.
**Action:** `PATCH /admin/v1/tenants/{tenantId}/modules/chat_ai/runtime-status` `{"enabled": false, "reason": "..."}`
**Expected:**
- Response includes `integrations_affected: ["ms_teams"]` warning before confirming
- After confirmation: `tenant_integration_credentials` for `ms_teams` updated to `status = 'disabled'` (not `disconnected`)
- Re-enabling module restores `ms_teams` to `status = 'connected'` automatically

### TC-FF-015: Runtime re-enable restores disabled integrations
**Setup:** `chat_ai` module is runtime-disabled. `ms_teams` has `status = 'disabled'` due to prior disable.
**Action:** `PATCH /admin/v1/tenants/{tenantId}/modules/chat_ai/runtime-status` `{"enabled": true, "reason": "Investigation complete"}`
**Expected:**
- `tenant_module_entitlements.runtime_override = true`
- `ms_teams` `tenant_integration_credentials.status` restored to `'connected'`
- Audit log: `action = 'module.runtime_enabled'`

### TC-FF-016: Tenant JWT cannot call feature flag manager endpoints
**Action:** Any `GET /admin/v1/feature-flags` with tenant-scoped JWT (`iss: "onevo-tenant"`)
**Expected:** HTTP 401
