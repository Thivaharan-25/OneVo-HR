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

## Related

- [[auth|Auth Module]]
- [[authentication]]
- [[authorization]]
- [[mfa]]
- [[audit-logging]]
- [[gdpr-consent]]
- [[auth-architecture]]
- [[multi-tenancy]]
- [[error-handling]]
- [[logging-standards]]
- [[WEEK1-auth-security]]
