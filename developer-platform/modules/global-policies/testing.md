# Global Policies — Testing

## Test Fixtures Required

- Platform account with `platform.system_config.manage`
- Platform account with `platform.system_config.read` only
- At least 5 active tenants
  - 2 with explicit `tenant_auth_policies` override on the test policy field (value differs from global default)
  - 3 with no override (value matches global default)

---

## View and Draft

### TC-GP-001: List returns all six auth policy keys
**Action:** `GET /admin/v1/global-policies`
**Expected:** Response contains exactly 6 policies with keys: `auth.mfa_required_default`, `auth.google_login_allowed_default`, `auth.password_login_allowed_default`, `auth.google_email_mismatch_allowed_default`, `auth.failed_login_lockout_threshold`, `auth.failed_login_lockout_minutes`. Each has `published_default`, `draft_value` (nullable), `data_type`, `display_name`.

### TC-GP-002: Update draft value does not affect published default or any tenant
**Action:** `PATCH /admin/v1/global-policies/{id}` `{ "draft_value": true }` on `auth.mfa_required_default`
**Expected:** HTTP 200. `draft_value: true`. `published_default` unchanged. No `tenant_auth_policies` rows modified.

---

## Publish

### TC-GP-003: Publish updates system_settings and writes audit log
**Setup:** `auth.mfa_required_default` published default = `false`. Draft set to `true`.
**Action:** `POST /admin/v1/global-policies/{id}/publish` `{ "reason": "Compliance requirement: MFA mandatory from 2026-Q3" }`
**Expected:** HTTP 200. `published_default: true`. `system_settings` row for `auth.mfa_required_default` updated. Audit log: `action = 'global_policy.published'`, `previous_default: false`, `new_default: true`, reason and actor recorded.

### TC-GP-004: Publish requires reason
**Action:** `POST /admin/v1/global-policies/{id}/publish` without `reason` field
**Expected:** HTTP 422.

### TC-GP-005: Read-only account cannot publish
**Setup:** Account with `platform.system_config.read` only.
**Action:** `POST /admin/v1/global-policies/{id}/publish`
**Expected:** HTTP 403.

### TC-GP-006: Tenant impact count excludes tenants with explicit overrides
**Setup:** 5 active tenants. `auth.mfa_required_default` published default = `false`. 2 tenants have `tenant_auth_policies.mfa_required = true` (explicit override). 3 tenants have `mfa_required = false` (matching global default).
**Action:** `GET /admin/v1/global-policies/{id}/tenant-impact`
**Expected:** `{ "affected_tenants": 3, "unaffected_tenants": 2 }`.

### TC-GP-007: Publish does not auto-propagate to existing tenants
**Setup:** Same as TC-GP-006. Draft = `true`.
**Action:** Publish.
**Expected:** All 5 existing tenants' `tenant_auth_policies` rows unchanged. New default takes effect only for future provisioning.

---

## Propagate

### TC-GP-008: Propagate updates only tenants without explicit override
**Setup:** Same as TC-GP-006. Policy published with new default `true`.
**Action:** `POST /admin/v1/global-policies/{id}/propagate` `{ "reason": "Propagating MFA requirement to existing tenants" }`
**Expected:**
- 3 tenants: `tenant_auth_policies.mfa_required` updated to `true`
- 2 tenants with explicit override: `tenant_auth_policies` unchanged
- Audit log: `action = 'global_policy.propagated'`, `applied_count: 3`, `skipped_count: 2`, reason and actor recorded

### TC-GP-009: Propagation is idempotent
**Setup:** Policy already propagated. All 3 affected tenants already have the new value.
**Action:** Fire propagation job again for the same publish event.
**Expected:** No tenant rows changed. `applied_count: 0`, `skipped_count: 5`. No duplicate audit entries.
**Note:** `skipped_count` covers all tenants not updated — explicit overrides (2) plus tenants already at the published value (3).

### TC-GP-010: Propagation failure on one tenant does not block others
**Setup:** 3 tenants to propagate. Simulate DB error on tenant 2.
**Expected:** Tenants 1 and 3 updated. Tenant 2 failure recorded individually in audit log. Response: `applied_count: 2`, `failed_count: 1`.

---

## Provisioning Integration

> **Note:** TC-GP-011 and TC-GP-012 require backend changes before they are valid. `CreateTenantCommandHandler` must be updated to read from `system_settings` instead of C# entity defaults, and `AuthService` must be updated to read lockout values from `system_settings`. These tests should be added to the integration suite when those changes are implemented.

### TC-GP-011: New tenant provisioned after publish receives new default
**Requires:** `CreateTenantCommandHandler` updated to read from `system_settings`.
**Setup:** `auth.mfa_required_default` published default = `true`.
**Action:** Provision a new tenant.
**Expected:** New tenant's `tenant_auth_policies.mfa_required = true`.

### TC-GP-012: Lockout settings apply at runtime — no per-tenant row
**Requires:** `AuthService` updated to read lockout values from `system_settings`.
**Setup:** `auth.failed_login_lockout_threshold` published default = `3`.
**Action:** Tenant user fails login 3 times.
**Expected:** Account locked. AuthService reads `system_settings` for the threshold value — no `tenant_auth_policies` column involved.
