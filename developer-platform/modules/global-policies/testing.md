# Global Policies — Testing

## Test Fixtures Required

- Platform account with `platform.policies.manage`
- Platform account with `platform.policies.read` only
- At least 5 active tenants, 2 with explicit policy overrides for the test policy

---

## Create and Publish

### TC-GP-001: Create policy — happy path
**Action:** `POST /admin/v1/global-policies`
```json
{
  "policy_key": "monitoring.screenshot_capture_default",
  "display_name": "Screenshot Capture Default",
  "description": "Default value for screenshot capture when a tenant is provisioned.",
  "default_value": false,
  "data_type": "boolean"
}
```
**Expected:** HTTP 201. Policy exists in draft state. No tenants affected yet.

### TC-GP-002: Publish shows correct tenant impact count
**Setup:** 5 active tenants. 2 have explicit override for `monitoring.screenshot_capture_default`. 3 do not.
**Action:** `GET /admin/v1/global-policies/{id}/tenant-impact`
**Expected:** `affected_tenants: 3` — the 3 without explicit overrides would be affected. The 2 with overrides are not.

### TC-GP-003: Impact preview count matches actual propagation on publish
**Setup:** Same as TC-GP-002. Impact preview says 3 tenants.
**Action:** `POST /admin/v1/global-policies/{id}/publish` `{"reason": "Default change approved in compliance review"}`
**Expected:**
- Exactly 3 tenants have their setting updated (the ones without overrides)
- 2 tenants with explicit overrides: settings UNCHANGED
- Audit log: `action = 'global_policy.published'`, `affected_count: 3`, reason recorded

### TC-GP-004: Tenant-specific overrides are NOT overwritten by publish
**Setup:** Tenant T has explicit override for this policy
**Action:** Publish policy with new default value
**Expected:** Tenant T's override value unchanged. Only tenants with no override get the new default.

### TC-GP-005: Publish requires reason
**Action:** `POST /admin/v1/global-policies/{id}/publish` without `reason`
**Expected:** HTTP 422 — reason required for publish (high-impact action)

### TC-GP-006: Background propagation is idempotent
**Action:** Publish fires propagation job. Job runs twice (simulate retry).
**Expected:** Affected tenants end up with the correct value once — double application doesn't double-apply. No duplicate audit entries.

### TC-GP-007: Read-only account cannot publish
**Setup:** Account with `platform.policies.read` only
**Action:** `POST /admin/v1/global-policies/{id}/publish`
**Expected:** HTTP 403

### TC-GP-008: Every publish writes audit log with old and new values
**Setup:** Policy `default_value = false`
**Action:** Publish with new `default_value = true`
**Expected:** Audit log: `previous_default: false`, `new_default: true`, actor, reason, affected tenant count
