# Authentication — End-to-End Logic

**Module:** Auth
**Feature:** Authentication

---

## Login

### Flow

```
POST /api/v1/auth/login
  -> AuthController.Login(LoginCommand)
    -> Public endpoint (no auth required)
    -> Validation: email, password required
    -> AuthService.LoginAsync(command, ct)
      -> 1. Find user by email + tenant (from request header or subdomain)
         -> If not found -> Return failure("Invalid credentials")
      -> 2. Verify password via bcrypt hash comparison
         -> If mismatch -> Return failure("Invalid credentials")
         -> Increment failed_attempts counter (Redis)
         -> If failed_attempts >= 5 -> Lock account for 15 min
      -> 3. Check user.is_active
         -> If false -> Return failure("Account disabled")
      -> 4. Check if MFA is enabled for user
         -> If yes -> Return Result.Success(new { RequiresMfa = true, MfaToken })
      -> 5. Load user roles and permissions via role_permissions + user_roles
      -> 6. Generate access token (JWT RS256, 15 min expiry)
         -> Claims: user_id, tenant_id, permissions[], email
      -> 7. Generate refresh token (random, SHA-256 hashed, 7 day expiry)
         -> INSERT into refresh_tokens
      -> 8. Create session record in sessions table
      -> 9. UPDATE users SET last_login_at = now
      -> 10. Log to audit_logs: action = "user.login"
      -> Return Result.Success(TokenPairDto { AccessToken, RefreshToken })
```

## Refresh Token

### Flow

```
POST /api/v1/auth/refresh
  -> AuthController.Refresh(RefreshTokenCommand)
    -> AuthService.RefreshTokenAsync(refreshToken, ct)
      -> 1. Hash incoming token with SHA-256
      -> 2. Find refresh_tokens WHERE token_hash = @hash
         -> If not found -> Return failure("Invalid token")
      -> 3. Check if token is revoked
         -> If revoked -> REVOKE ENTIRE CHAIN (token theft detection)
         -> Return failure("Token reuse detected")
      -> 4. Check expiry (7 days)
      -> 5. Generate new access token + new refresh token
      -> 6. Mark old refresh token: replaced_by_id = new_token.id
      -> Return Result.Success(new TokenPairDto)
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Invalid credentials | Return 401, generic message (no email enumeration) |
| Account locked | Return 423, include unlock time |
| Account disabled | Return 403 |
| Token expired | Return 401 with "token_expired" code |
| Refresh token reuse | Revoke entire chain, return 401 |

## Related

- [[frontend/cross-cutting/authentication|Overview]]
- [[modules/auth/session-management/overview|Session Management]]
- [[mfa]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
