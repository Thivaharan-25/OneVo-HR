# Platform API Key Manager - End-to-End Logic

> **Phase 2 only.** This module does not exist in Phase 1. Phase 1 navigation must not include any API key manager links or routes. The endpoint `/admin/v1/api-keys` returns HTTP 404 in Phase 1 deployments.

## Purpose

Platform API Key Manager enables programmatic access to the Admin API for CI/CD pipelines, external tooling, and automation scripts without requiring a human platform-admin session. Keys are scoped to specific permission sets, have optional expiry, and can be revoked at any time.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `platform_api_keys` | Read + write - key metadata and SHA256 hash; raw key never stored |
| Audit log | Write every key create and revoke action |

## Issue Key - Full Flow

1. Platform Super Admin opens API Keys (`/platform/api-keys`)
2. Clicks `+ Issue New Key`
3. Fills form:

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| Name | "Key Name" | Text input | Yes | Human-readable label for identification in the list |
| Scopes | "Permissions / Scopes" | Multi-select from platform permission catalog | Yes | Subset of platform permissions this key is allowed to use |
| Expiry | "Expiry (Optional)" | Date picker | No | If set, key is rejected after this date |
| Rate Limit | "Rate Limit (requests/minute)" | Number input | No | Optional per-key rate limit |

4. Clicks "Issue Key"
5. Backend:
   - Generates a cryptographically random raw key (e.g., `pk_live_...`)
   - Computes `SHA256(raw_key)` and stores only the hash in `platform_api_keys.key_hash`
   - Raw key is NEVER stored - discarded from memory immediately after returning it
6. Response: raw key shown **once** in a one-time-display dialog. Operator copies it. Dialog cannot be re-opened.
7. Audit log: `action = 'api_key.created'`, actor, name, scopes (not the raw key)

**API:** `POST /admin/v1/api-keys`

**Request:**
```json
{
  "name": "CI Pipeline Key",
  "scopes": ["platform.agent_versions.read", "platform.health.read"],
  "expires_at": "2027-05-17T00:00:00Z"
}
```

**Response (201 Created - raw key shown ONCE only):**
```json
{
  "key_id": "uuid",
  "name": "CI Pipeline Key",
  "raw_key": "pk_live_abc123xyz...",
  "scopes": ["platform.agent_versions.read", "platform.health.read"],
  "expires_at": "2027-05-17T00:00:00Z",
  "created_at": "2026-05-17T09:00:00Z"
}
```

Subsequent `GET /admin/v1/api-keys/{id}` returns metadata only - no `raw_key`.

## Revoke Key

**Trigger:** "Revoke" action on any active key row.

No confirmation dialog - revocation is instant and the key is unusable immediately.

**API:** `DELETE /admin/v1/api-keys/{id}`

Sets `platform_api_keys.revoked_at = now()`. Any request using the revoked key returns HTTP 401 from that moment. Revoked keys remain in the list with `status = "revoked"` for audit history.

Audit log: `action = 'api_key.revoked'`, actor, key name.

## API Authentication With a Platform API Key

Instead of a platform-admin JWT, callers send:
```http
Authorization: Bearer pk_live_abc123xyz...
```

The backend:
1. Computes `SHA256(presented_key)`
2. Looks up `platform_api_keys WHERE key_hash = <hash> AND revoked_at IS NULL AND (expires_at IS NULL OR expires_at > NOW())`
3. If found: uses the key's `scopes` as the effective permission set for authorization checks
4. If not found or expired/revoked: HTTP 401

**Scopes are enforced at every endpoint** - a key with only `platform.health.read` cannot call any endpoint requiring `platform.runtime_flags.manage` or `platform.tenants.feature_overrides.manage`.

## Key List Screen

**Route:** `/platform/api-keys`
**API:** `GET /admin/v1/api-keys`

| Column | Description |
|---|---|
| Name | Label |
| Scopes | Permission tags |
| Created | Date |
| Created By | Platform account name |
| Expires | Date or "Never" |
| Last Used | Timestamp of last successful authenticated request |
| Status | Active (green) / Expired (gray) / Revoked (red) |
| Actions | Revoke (active keys only) |

## APIs

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/api-keys` | List keys (no raw values) | `platform.api_keys.read` |
| POST | `/admin/v1/api-keys` | Issue new key | `platform.api_keys.manage` |
| GET | `/admin/v1/api-keys/{id}` | Key metadata | `platform.api_keys.read` |
| DELETE | `/admin/v1/api-keys/{id}` | Revoke key | `platform.api_keys.manage` |
