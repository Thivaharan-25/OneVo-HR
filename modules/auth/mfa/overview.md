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

- [[auth|Auth Module]]
- [[authentication]]
- [[authorization]]
- [[session-management]]
- [[audit-logging]]
- [[gdpr-consent]]
- [[auth-architecture]]
- [[multi-tenancy]]
- [[error-handling]]
- [[WEEK1-auth-security]]
