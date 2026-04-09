# Multi-Factor Authentication

**Module:** Auth & Security
**Feature:** MFA

---

## Purpose

Optional MFA support for enhanced security.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/auth/mfa/enable` | Authenticated | Enable MFA |
| POST | `/api/v1/auth/mfa/verify` | Authenticated | Verify MFA code |

## Related

- [[modules/auth/overview|Auth Module]]
- [[frontend/cross-cutting/authentication|Authentication]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[modules/auth/session-management/overview|Session Management]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
- [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]]
- [[security/auth-architecture|Auth Architecture]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[backend/messaging/error-handling|Error Handling]]
- [[current-focus/DEV2-auth-security|DEV2: Auth Security]]
