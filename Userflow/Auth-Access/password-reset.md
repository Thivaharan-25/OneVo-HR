# Password Reset

**Area:** Auth & Access  
**Required Permission(s):** Any user (self-service) or `users:manage` (admin-initiated)  
**Related Permissions:** `settings:admin` (configure password policy)

---

## Preconditions

- User account exists in the system
- Email service configured → [[notification-system]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Initiate Reset (Self-Service)
- **UI:** Login page → click "Forgot Password" → enter registered email
- **API:** `POST /api/v1/auth/forgot-password`
- **Backend:** AuthService.InitiatePasswordResetAsync() → [[authentication]]
- **Validation:** Email exists in system, account is active, not SSO-only user
- **DB:** `password_reset_tokens` — token created with expiry (24h)

### Step 2: Receive Reset Email
- **UI:** User checks email → clicks reset link with token
- **Backend:** Email sent via Resend → [[notification-system]]
- **Validation:** Token is valid, not expired, not already used

### Step 3: Set New Password
- **UI:** Reset page → enter new password + confirm → submit
- **API:** `POST /api/v1/auth/reset-password`
- **Backend:** AuthService.ResetPasswordAsync() → [[authentication]]
- **Validation:** Password meets policy (min length, complexity), token valid
- **DB:** `users` — password hash updated, `sessions` — all existing sessions invalidated

### Admin-Initiated Reset
- **UI:** Navigate to Users → select user → Actions → Reset Password → enter new password
- **API:** `POST /api/v1/users/{id}/reset-password`
- **Permission:** `users:manage`
- **Backend:** UserService.AdminResetPasswordAsync() → [[authentication]]
- **DB:** Password updated, all sessions invalidated, user notified via email

## Variations

### When SSO is enabled for user
- Self-service reset is disabled — user must reset via SSO provider
- Admin can still force a local password reset if hybrid auth is configured

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Email not found | No error revealed (security) | "If the email exists, a reset link has been sent" |
| Token expired | Reset fails | "Reset link has expired. Please request a new one" |
| Weak password | Validation fails | Password policy requirements listed |
| Account locked | Reset blocked | "Account is locked. Contact administrator" |

## Events Triggered

- `PasswordResetRequested` → [[event-catalog]]
- `PasswordResetCompleted` → [[event-catalog]]
- Notification: reset email → [[notification-system]]

## Related Flows

- [[login-flow]]
- [[mfa-setup]]
- [[user-invitation]]

## Module References

- [[authentication]]
- [[session-management]]
- [[notification-system]]
