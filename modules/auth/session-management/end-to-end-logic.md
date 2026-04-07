# Session Management — End-to-End Logic

**Module:** Auth
**Feature:** Session Management

---

## Logout

### Flow

```
POST /api/v1/auth/logout
  -> AuthController.Logout()
    -> [Authenticated]
    -> AuthService.LogoutAsync(ct)
      -> 1. Get current session from ICurrentUser
      -> 2. UPDATE sessions SET is_revoked = true
      -> 3. Revoke all refresh tokens for this session
         -> UPDATE refresh_tokens SET revoked_at = now WHERE user_id = @userId
      -> 4. Log to audit_logs: action = "user.logout"
      -> Return Result.Success()
```

## Session Tracking

### Flow

```
On every authenticated request:
  -> SessionMiddleware
    -> 1. Extract session_id from JWT claims
    -> 2. UPDATE sessions SET last_activity_at = now
       -> (Throttled: only update if > 1 min since last update)
    -> 3. Check session.is_revoked
       -> If revoked -> Return 401 (force re-login)
    -> 4. Check session.expires_at
       -> If expired -> Return 401
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Session revoked (admin action) | Next request returns 401, user must re-login |
| Session expired | Return 401 with "session_expired" code |
| Concurrent sessions | Allowed — each device gets its own session |

## Related

- [[session-management|Overview]]
- [[authentication]]
- [[audit-logging]]
- [[mfa]]
- [[event-catalog]]
- [[error-handling]]
