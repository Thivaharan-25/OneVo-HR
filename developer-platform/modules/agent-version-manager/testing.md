# Agent Version Manager — Testing

## Test Fixtures Required

- Platform account with `platform.agent_versions.manage` + `platform.agent_versions.force_update`
- Platform account with `platform.agent_versions.read` only
- `agent_deployment_rings` seeded with 3 rings (Internal=0, Beta=1, GA=2)
- At least 2 active tenants
- At least 1 `agent_version_releases` row (stable channel)

---

## Version Publishing

### TC-AV-001: Publish version — happy path
**Action:** `POST /admin/v1/agent-versions`
```json
{
  "version": "1.5.0",
  "release_channel": "beta",
  "min_os_version": "10.0.26000",
  "release_notes": "Bug fixes and performance improvements.",
  "download_url": "https://cdn.onevo.io/agent/v1.5.0/setup.exe"
}
```
**Expected:**
- HTTP 201
- `agent_version_releases` row: `version = "1.5.0"`, `release_channel = "beta"`, `recalled_at = null`
- Audit log: `action = 'agent_version.published'`

### TC-AV-002: Version publish requires manage permission
**Setup:** Account with `platform.agent_versions.read` only
**Action:** `POST /admin/v1/agent-versions`
**Expected:** HTTP 403

### TC-AV-003: Semver format enforced
**Action:** `POST /admin/v1/agent-versions` with `version: "1.5"` (not semver)
**Expected:** HTTP 422 — version must be in `major.minor.patch` format

---

## Channel Management

### TC-AV-004: Recall sets recalled_at — version excluded from deployment queries
**Setup:** Version `1.4.0` in stable channel. Tenant T assigned to GA ring → would normally get `1.4.0`.
**Action:** `PATCH /admin/v1/agent-versions/{id}/channel` `{"channel": "recalled"}`
**Expected:**
- `agent_version_releases.release_channel = "recalled"`
- `agent_version_releases.recalled_at` = now()
- Version no longer returned in deployment eligibility queries for GA ring tenants
- Existing installs of `1.4.0` are flagged for update

### TC-AV-005: Recalled version cannot be set back to stable without new publish
**Action:** `PATCH /admin/v1/agent-versions/{recalled_version_id}/channel` `{"channel": "stable"}`
**Expected:** HTTP 422 — recalled versions cannot be un-recalled; publish a new version instead

---

## Ring Assignment

### TC-AV-006: One active ring per tenant enforced
**Setup:** Tenant T assigned to Beta ring (ring_id = 1)
**Action:** `PUT /admin/v1/tenants/{id}/agent-ring` `{"ring_id": "<GA ring id>"}`
**Expected:**
- Previous Beta assignment removed
- New GA assignment created
- `UNIQUE(tenant_id, ring_id)` satisfied — only 1 ring per tenant at any time

### TC-AV-007: Ring assignment is audit-logged
**Action:** `PUT /admin/v1/tenants/{id}/agent-ring` `{"ring_id": "<Internal ring id>"}`
**Expected:** Audit log: `action = 'agent_ring.assigned'`, `previous_ring`, `new_ring`, actor

---

## Force Update

### TC-AV-008: Force update requires force_update permission
**Setup:** Account with `platform.agent_versions.manage` but NOT `platform.agent_versions.force_update`
**Action:** `POST /admin/v1/agent-versions/{id}/force-update`
**Expected:** HTTP 403

### TC-AV-009: Force update creates update commands for all devices in ring
**Setup:** Version `1.4.0` has 50 devices across Internal ring tenants. Newer version `1.5.0` exists.
**Action:** `POST /admin/v1/agent-versions/{v140Id}/force-update` (push update from 1.4.0 to current stable)
**Expected:**
- `UPDATE_AGENT` command queued for all 50 devices
- Audit log: `action = 'agent_version.force_update_queued'`, version, ring, device count

### TC-AV-010: Tenant JWT rejected
**Action:** `GET /admin/v1/agent-versions` with tenant JWT
**Expected:** HTTP 401
