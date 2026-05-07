# MFA - End-to-End Logic

**Module:** Auth
**Feature:** Multi-Factor Authentication

---

## Phase 1 Method

Phase 1 MFA uses email OTP. Authenticator-app TOTP is deferred/optional and must not be the default flow.

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
      -> Store hashed OTP in mfa_otp_challenges
      -> Expire challenge in 5 minutes
      -> Send OTP via email/notification service
      -> Return 202 with mfa_required = true and mfa_pending_token
```

## Resend OTP

```
POST /api/v1/auth/mfa/send
  -> Validate mfa_pending token
  -> Rate-limit resend
  -> Create a new OTP challenge and invalidate previous active challenge
  -> Send OTP via email/notification service
```

## Verify OTP

```
POST /api/v1/auth/mfa/verify
  -> Validate mfa_pending token
  -> Load active mfa_otp_challenges row
  -> Reject if expired, consumed, or locked
  -> Hash submitted code and compare
  -> If valid:
      -> Mark challenge consumed
      -> Generate access token + refresh token
      -> Return AuthResponseDto
  -> If invalid:
      -> Increment failed_attempts
      -> Lock after 3 failed attempts
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
