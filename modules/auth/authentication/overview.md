# Authentication

**Module:** Auth & Security
**Feature:** Authentication

---

## Purpose

BFF-style customer web authentication with HttpOnly session cookies and backend-held tenant auth state/JWTs. Includes device JWT for desktop agents.

## Database Tables

### `refresh_tokens`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `user_id` | `uuid` | FK â†’ users |
| `token_hash` | `varchar(128)` | SHA-256 hash of token |
| `expires_at` | `timestamptz` | 7 days from creation |
| `replaced_by_id` | `uuid` | Self-referencing â€” token rotation |
| `revoked_at` | `timestamptz` | Nullable |
| `created_at` | `timestamptz` | |

## Key Business Rules

1. Customer web BFF session â€” HttpOnly session cookies with backend-held auth state.
2. Refresh token rotation â€” each use generates a new token, old one marked with `replaced_by_id`.
3. If a revoked token is reused, revoke the entire chain (token theft detection).
4. Device JWT for agents â€” `device_id` + `tenant_id` + `type: "agent"` claim, no user permissions.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/auth/login` | Public | Login |
| POST | `/api/v1/auth/refresh` | Public | Refresh cookie-backed session |
| POST | `/api/v1/auth/logout` | Authenticated | Logout |

## Related

- [[modules/auth/overview|Auth Module]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[modules/auth/session-management/overview|Session Management]]
- [[modules/auth/mfa/overview|MFA]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
- [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]]
- [[security/auth-architecture|Auth Architecture]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[backend/messaging/error-handling|Error Handling]]
- [[code-standards/logging-standards|Logging Standards]]
- [[current-focus/DEV2-auth-security|DEV2: Auth Security]]





