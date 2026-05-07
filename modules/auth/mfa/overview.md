# Multi-Factor Authentication

**Module:** Auth & Security
**Feature:** MFA

---

## Purpose

Optional MFA support for enhanced security. MFA uses email OTP sent to the user's verified email address.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/auth/mfa/enable` | Authenticated | Enable email OTP MFA |
| POST | `/api/v1/auth/mfa/send` | `mfa_pending` | Send/resend 6-digit email OTP |
| POST | `/api/v1/auth/mfa/verify` | `mfa_pending` | Verify email OTP code |

## Rules

- OTP is 6 digits.
- OTP is sent to the user's verified email through the notification/email boundary.
- Local development may log the OTP, but Phase 1 customer release requires Resend-backed delivery.
- Raw OTP is never stored; only a hash is stored temporarily for verification.
- OTP expires after 5 minutes.
- OTP is single-use.
- Resend is rate-limited to prevent mailbox flooding.

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
