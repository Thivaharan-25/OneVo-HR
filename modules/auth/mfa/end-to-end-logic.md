# MFA - End-to-End Logic

**Module:** Auth
**Feature:** Multi-Factor Authentication

---

## Phase 1 Method

MFA uses email OTP sent to the user's verified email address.

## Enable Email OTP MFA

```
POST /api/v1/auth/mfa/enable
  -> AuthController.EnableMfa()
    -> [Authenticated]
    -> MfaService.EnableEmailOtpAsync(userId, ct)
      -> 1. Confirm user has a verified email address
      -> 2. Store user_mfa row with method = email_otp and is_verified = true
      -> 3. Return success
```

## Login MFA Challenge

```
POST /api/v1/auth/login
  -> LoginCommandHandler validates password
  -> If email OTP MFA is enabled:
      -> Generate 6-digit OTP
      -> Store hashed OTP on the verified email_otp MFA method
      -> Expire challenge in 5 minutes
      -> Send OTP via email/notification service
      -> Return 202 with mfa_required = true and mfa_pending_token
```

## Resend OTP

```
POST /api/v1/auth/mfa/send
  -> Validate mfa_pending token
  -> Generate a new 6-digit OTP
  -> Replace the stored OTP hash on the verified email_otp MFA method
  -> Send OTP via email/notification service
```

## Verify OTP

```
POST /api/v1/auth/mfa/verify
  -> Validate mfa_pending token
  -> Load verified email_otp MFA method
  -> Reject if expired or already consumed
  -> Compare submitted code against the stored hash
  -> If valid:
      -> Clear stored OTP hash
      -> Generate access token + refresh token
      -> Return AuthResponseDto
  -> If invalid:
      -> Return failure("Invalid MFA code")
```

## Error Scenarios

| Error | Handling |
|:------|:---------|
| Email not verified | Return 400 and require email verification before MFA enable |
| OTP delivery unavailable | Return 503 in production; local development may log OTP |
| Invalid OTP code | Return 401 and increment attempt counter |
| OTP expired | Return 401; user must resend or restart login |
| OTP already consumed | Return 401 |
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
