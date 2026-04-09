# GDPR Consent

**Module:** Auth & Security
**Feature:** GDPR Consent

---

## Purpose

Tracks employee consent for data processing, biometric, monitoring, and marketing activities. Monitoring consent (`consent_type: "monitoring"`) must be recorded before monitoring features activate.

## Database Tables

### `gdpr_consent_records`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `user_id` | `uuid` | FK → users |
| `consent_type` | `varchar(50)` | `data_processing`, `biometric`, `monitoring`, `marketing` |
| `consented` | `boolean` | |
| `consented_at` | `timestamptz` | |
| `ip_address` | `varchar(45)` | |

## Key Business Rules

1. Monitoring consent must be recorded before monitoring features activate for an employee.
2. Biometric consent is mandatory before fingerprint enrollment (GDPR/PDPA).

## Related

- [[modules/auth/overview|Auth Module]]
- [[frontend/cross-cutting/authentication|Authentication]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
- [[modules/auth/session-management/overview|Session Management]]
- [[mfa]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/compliance|Compliance]]
- [[security/data-classification|Data Classification]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[current-focus/DEV2-auth-security|DEV2: Auth Security]]
