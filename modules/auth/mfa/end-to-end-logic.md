# MFA - End-to-End Logic

**Module:** Auth
**Feature:** Multi-Factor Authentication

---

## Phase 1 Method

MFA uses authenticator-app TOTP as the primary method. Email OTP is fallback/recovery only when policy permits it.

## Enable TOTP MFA

```
POST /api/v1/auth/mfa/enable
  -> AuthController.EnableMfa()
    -> [Authenticated]
    -> MfaService.BeginTotpSetupAsync(userId, ct)
      -> 1. Generate TOTP secret
      -> 2. Store user_mfa row with method = totp, encrypted secret, and is_verified = false
      -> 3. Return QR-code URI and manual setup key
```

## Confirm TOTP Setup

```
POST /api/v1/auth/mfa/confirm
  -> Validate authenticated user
  -> Load pending totp method
  -> Verify submitted authenticator code
  -> Mark method is_verified = true
  -> Generate recovery codes
  -> Return success
```

## Login MFA Challenge

```
POST /api/v1/auth/login
  -> LoginCommandHandler validates password
  -> If TOTP MFA is enabled:
      -> Return 202 with mfa_required = true and mfa_pending_token
```

## Email OTP Fallback

```
POST /api/v1/auth/mfa/send
  -> Validate mfa_pending token
  -> Confirm fallback is allowed by tenant/user policy
  -> Generate a new 6-digit OTP
  -> Store fallback OTP hash with 5-minute expiry
  -> Send OTP via email/notification service
```

## Verify MFA

```
POST /api/v1/auth/mfa/verify
  -> Validate mfa_pending token
  -> Load verified totp MFA method
  -> Verify submitted code against encrypted TOTP secret
  -> Reject reused TOTP code inside accepted window
  -> If fallback challenge is being used:
      -> Compare submitted code against fallback OTP hash
      -> Reject if expired or already consumed
  -> If valid:
      -> Create or upgrade HttpOnly cookie-backed web session
      -> Return AuthResponseDto
  -> If invalid:
      -> Return failure("Invalid MFA code")
```

## Error Scenarios

| Error | Handling |
|:------|:---------|
| TOTP setup not confirmed | Return 400 and require setup confirmation |
| Email fallback delivery unavailable | Return 503 in production for fallback only; local development may log fallback OTP |
| Invalid TOTP code | Return 401 and increment attempt counter |
| Fallback OTP expired | Return 401; user must resend or restart login |
| TOTP code replayed or fallback OTP already consumed | Return 401 |
| MFA challenge locked | Return 423 |
| MFA not enabled for user | Return 400 |

## Related

- [[mfa|Overview]]
- [[frontend/cross-cutting/authentication|Authentication]]
- [[modules/auth/session-management/overview|Session Management]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
- [[modules/notifications/overview|Notifications]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]

