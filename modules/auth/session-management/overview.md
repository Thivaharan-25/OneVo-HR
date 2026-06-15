# Session Management

**Module:** Auth & Security
**Feature:** Session Management

---

## Purpose

Tracks active user sessions with IP, user agent, and expiry.

## Database Tables

### `sessions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `user_id` | `uuid` | FK -> users |
| `tenant_id` | `uuid` | FK -> tenants |
| `ip_address` | `varchar(45)` | |
| `user_agent` | `varchar(500)` | |
| `started_at` | `timestamptz` | |
| `last_activity_at` | `timestamptz` | |
| `expires_at` | `timestamptz` | |
| `is_revoked` | `boolean` | |

## Permission Revocation

When a user's permissions change (role assigned, permission revoked, role expired), their backend-held permission snapshot becomes stale. Phase 1 uses an **in-memory permission version counter** to invalidate stale tokens inside the running API process. Redis is optional/future distributed infrastructure for multi-instance deployment:

1. Any permission change -> increment `perm_version:{user_id}` in the Phase 1 in-memory counter
2. Auth middleware compares JWT `perm_ver` claim to the current permission version counter on every request
3. Mismatch -> `401` with `code: "permissions_changed"` -> frontend silently refreshes
4. Backend-held session/auth state refreshed with permissions from DB and updated `perm_ver`

**Result:** Revocation propagates within one request cycle for users routed to the same API process. The `sessions` table `is_revoked` flag handles full session termination (logout, security incident). A future Redis counter would provide the same mid-session permission-change behavior across multiple API instances.

See [[security/auth-architecture|Auth Architecture - Permission Revocation]] for the full design and `IPermissionVersionService` interface.

## Related

- [[modules/auth/overview|Auth Module]]
- [[frontend/cross-cutting/authentication|Authentication]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[modules/auth/mfa/overview|MFA]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
- [[Userflow/Auth-Access/gdpr-consent|Legal & Privacy Acceptance]]
- [[security/auth-architecture|Auth Architecture]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[backend/messaging/error-handling|Error Handling]]
- [[code-standards/logging-standards|Logging Standards]]
- [[current-focus/DEV2-auth-security|DEV2: Auth Security]]

