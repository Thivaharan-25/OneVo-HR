# MFA — End-to-End Logic

**Module:** Auth
**Feature:** Multi-Factor Authentication

---

## Enable MFA

### Flow

```
POST /api/v1/auth/mfa/enable
  -> AuthController.EnableMfa()
    -> [Authenticated]
    -> MfaService.EnableAsync(userId, ct)
      -> 1. Generate TOTP secret (RFC 6238)
      -> 2. Store encrypted secret in user profile
      -> 3. Generate QR code URI for authenticator app
      -> Return Result.Success(new MfaSetupDto { QrCodeUri, BackupCodes })
```

## Verify MFA Code

### Flow

```
POST /api/v1/auth/mfa/verify
  -> AuthController.VerifyMfa(VerifyMfaCommand)
    -> MfaService.VerifyAsync(userId, code, ct)
      -> 1. Load TOTP secret for user
      -> 2. Validate code against current + previous time window (30s tolerance)
      -> 3. If valid:
         -> Generate access token + refresh token (same as normal login)
         -> Return Result.Success(TokenPairDto)
      -> 4. If invalid:
         -> Increment MFA attempt counter
         -> If attempts >= 5 -> Lock MFA for 15 min
         -> Return failure("Invalid MFA code")
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Invalid TOTP code | Return 401, increment attempt counter |
| MFA locked (too many attempts) | Return 423 |
| MFA not enabled for user | Return 400 |

## Related

- [[mfa|Overview]]
- [[frontend/cross-cutting/authentication|Authentication]]
- [[modules/auth/session-management/overview|Session Management]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
