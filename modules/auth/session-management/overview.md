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
| `user_id` | `uuid` | FK → users |
| `tenant_id` | `uuid` | FK → tenants |
| `ip_address` | `varchar(45)` | |
| `user_agent` | `varchar(500)` | |
| `started_at` | `timestamptz` | |
| `last_activity_at` | `timestamptz` | |
| `expires_at` | `timestamptz` | |
| `is_revoked` | `boolean` | |

## Permission Revocation

When a user's permissions change (role assigned, permission revoked, role expired), their existing access token becomes stale. The system uses a **Redis permission version counter** to invalidate stale tokens immediately:

1. Any permission change → `INCR perm_version:{user_id}` in Redis
2. Auth middleware compares JWT `perm_ver` claim to Redis counter on every request
3. Mismatch → `401` with `code: "permissions_changed"` → frontend silently refreshes
4. New access token issued with fresh permissions from DB and updated `perm_ver`

**Result:** Revocation propagates within one request cycle (≤1 second for active users). The `sessions` table `is_revoked` flag handles full session termination (logout, security incident). The Redis counter handles mid-session permission changes without forcing full re-login.

See [[security/auth-architecture|Auth Architecture — Permission Revocation]] for the full design and `IPermissionVersionService` interface.

## Related

- [[modules/auth/overview|Auth Module]]
- [[frontend/cross-cutting/authentication|Authentication]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[modules/auth/mfa/overview|MFA]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
- [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]]
- [[security/auth-architecture|Auth Architecture]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[backend/messaging/error-handling|Error Handling]]
- [[code-standards/logging-standards|Logging Standards]]
- [[current-focus/DEV2-auth-security|DEV2: Auth Security]]
