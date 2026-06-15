# Platform API Key Manager — Testing

> **Phase 2 module — not available in Phase 1.** All Phase 1 tests verify the module is not exposed. Phase 2 tests cover key lifecycle.

## Test Fixtures Required

- Phase 1: Platform account with any permission level
- Phase 2: Platform account with `platform.api_keys.manage`
- Phase 2: Platform account with `platform.api_keys.read` only

---

## Phase 1 — Module Not Exposed

### TC-AK-001: API key endpoints return 404 in Phase 1
**Action:** `GET /admin/v1/api-keys`
**Expected:** HTTP 404 — endpoint not available in Phase 1 deployment

### TC-AK-002: API key manager navigation item not rendered in Phase 1
**Action:** Load Developer Console sidebar
**Expected:** No "Platform API Keys" or "API Key Manager" menu item in sidebar. Not shown as disabled — entirely absent.

---

## Phase 2 — Key Lifecycle

### TC-AK-003: Key creation requires platform.api_keys.manage
**Setup:** Account with `platform.api_keys.read` only
**Action:** `POST /admin/v1/api-keys`
**Expected:** HTTP 403

### TC-AK-004: Raw key returned exactly once on creation — never again
**Action:** `POST /admin/v1/api-keys` `{"name": "CI Pipeline Key", "scopes": ["agent:view-health"]}`
**Expected:**
- HTTP 201
- Response includes `raw_key: "pk_live_..."` — shown once only
- Subsequent `GET /admin/v1/api-keys/{id}` does NOT include `raw_key` — only metadata
- `platform_api_keys.key_hash` in DB is SHA256 of raw key — plaintext never stored

### TC-AK-005: Stored key value is SHA256 hash — not plaintext
**Setup:** API key created
**Action:** Query `platform_api_keys` table directly (integration test)
**Expected:** `key_hash` column = SHA256(raw_key). Column `raw_key` does not exist.

### TC-AK-006: Revoked key rejected at authentication
**Setup:** Active API key `pk_live_abc123`. Revoke it via `DELETE /admin/v1/api-keys/{id}`.
**Action:** Make any admin API request using `Authorization: Bearer pk_live_abc123`
**Expected:** HTTP 401 — revoked key not accepted

### TC-AK-007: Expired key rejected
**Setup:** API key with `expires_at` in the past
**Action:** Make API request using expired key
**Expected:** HTTP 401 — expired key treated same as revoked

### TC-AK-008: Scope checks are enforced per endpoint
**Setup:** API key scoped to `["agent:view-health"]` only
**Action:** Use this key to call `PATCH /admin/v1/feature-flags/{key}` (requires `platform.runtime_flags.manage`)
**Expected:** HTTP 403 — key scope does not include feature flag management

### TC-AK-009: Key create and revoke write audit logs
**Action 1:** Create API key
**Expected:** Audit log: `action = 'api_key.created'`, actor, `name`, `scopes`

**Action 2:** Delete (revoke) API key
**Expected:** Audit log: `action = 'api_key.revoked'`, actor, key name
