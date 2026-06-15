# Platform API Key Manager

> **Phase 2 only.** Not available in Phase 1. All routes and navigation items for API key management must be absent from Phase 1 deployments. `/admin/v1/api-keys` returns HTTP 404 in Phase 1.

## Purpose

Platform API Key Manager enables programmatic access to the Admin API for CI/CD pipelines, automation scripts, and external tooling without requiring a human platform-admin session. Keys are scoped to specific platform permissions, support optional expiry, and can be revoked at any time.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `platform_api_keys` | Read + write — key name, scopes, expiry, revoked_at, `key_hash` (SHA256 of raw key) |
| Audit log | Write every key creation and revocation event |

## How Keys Work

A raw key is generated once, shown to the operator in a one-time display dialog, and then discarded — the backend stores only the SHA256 hash. Subsequent API calls present the raw key in the `Authorization: Bearer` header; the backend hashes it and looks up the match. If found and not expired/revoked, the key's scopes become the effective permission set for that request.

## Capabilities

### Key Issuance
- Create a named platform API key with selected permission scopes (subset of platform permission catalog) and optional expiry date
- Raw key shown **once only** in a one-time dialog — cannot be retrieved again; operator must copy it immediately

### Key Management
- View all keys (active, expired, revoked) with name, scopes, created by, created at, last used, and status
- Revoke any active key instantly — takes effect on the very next request using that key

### Key Usage Logs
- View per-key usage history: last used timestamp, request count, endpoint breakdown
- Useful for auditing external integrations and detecting anomalous access patterns

## Navigation

| Route | Permission |
|---|---|
| `/platform/api-keys` *(Phase 2 only)* | `platform.api_keys.read` |
| Issue / Revoke | `platform.api_keys.manage` |

## Key Rules

- Raw key shown exactly once — the backend never stores it; only SHA256 hash is persisted
- Revoked and expired keys are rejected with HTTP 401 on the next request — no grace period
- Scope enforcement: a key can only call endpoints whose required permission is within the key's declared scopes
- All create and revoke events are audit-logged with actor, key name, and scopes (never the raw key itself)
- Phase 1: endpoint returns 404; no navigation item rendered anywhere in the console

## Related

- [[developer-platform/modules/api-key-manager/end-to-end-logic|API Key Manager End-to-End Logic]]
- [[developer-platform/auth|Developer Platform Auth]] — JWT-based human operator authentication (Phase 1)
- [[developer-platform/modules/platform-access/overview|Platform Users and Platform Roles]] — human operator account management
