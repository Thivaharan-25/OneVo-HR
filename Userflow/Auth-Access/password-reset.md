# Password Reset

**Area:** Auth & Access  
**Trigger:** User clicks Forgot Password or admin initiates reset (user action)
**Required Permission(s):** Any user (self-service) or `users:manage` (admin-initiated)  
**Related Permissions:** `settings:admin` (configure password policy)

---

## Preconditions

- User account exists in the system
- Email service configured -> [[backend/notification-system|Notification System]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Initiate Reset (Self-Service)
- **UI:** Login page -> click "Forgot Password" -> enter registered email
- **API:** `POST /api/v1/auth/forgot-password`
- **Backend:** AuthService.InitiatePasswordResetAsync() -> [[frontend/cross-cutting/authentication|Authentication]]
- **Validation:** Email exists in system, account is active, not SSO-only user
- **DB:** `password_reset_tokens` - token created with expiry (24h)

### Step 2: Receive Reset Email
- **UI:** User checks email -> clicks reset link with token
- **Backend:** Email sent via Resend -> [[backend/notification-system|Notification System]]
- **Validation:** Delivery status is tracked in `email_delivery_logs`; bounced or failed reset emails are visible for support troubleshooting without exposing the reset token.
- **Validation:** Token is valid, not expired, not already used

### Step 3: Set New Password
- **UI:** Reset page -> enter new password + confirm -> submit
- **API:** `POST /api/v1/auth/reset-password`
- **Backend:** AuthService.ResetPasswordAsync() -> [[frontend/cross-cutting/authentication|Authentication]]
- **Validation:** Password meets policy (min length, complexity), token valid
- **DB:** `users` - password hash updated, `sessions` - all existing sessions invalidated

### Admin-Initiated Reset
- **UI:** Navigate to Users -> select user -> Actions -> Reset Password -> enter new password
- **API:** `POST /api/v1/users/{id}/reset-password`
- **Permission:** `users:manage`
- **Backend:** UserService.AdminResetPasswordAsync() -> [[frontend/cross-cutting/authentication|Authentication]]
- **DB:** Password updated, all sessions invalidated, user notified via email

## Variations

### When SSO is enabled for user
- Self-service reset is disabled - user must reset via SSO provider
- Admin can still force a local password reset if hybrid auth is configured

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Email not found | No error revealed (security) | "If the email exists, a reset link has been sent" |
| Token expired | Reset fails | "Reset link has expired. Please request a new one" |
| Weak password | Validation fails | Password policy requirements listed |
| Account locked | Reset blocked | "Account is locked. Contact administrator" |

## Events Triggered

- `PasswordResetRequested` -> [[backend/messaging/event-catalog|Event Catalog]]
- `PasswordResetCompleted` -> [[backend/messaging/event-catalog|Event Catalog]]
- Notification: reset email -> [[backend/notification-system|Notification System]]

## Related Flows

- [[Userflow/Auth-Access/login-flow|Login Flow]]
- [[Userflow/Auth-Access/mfa-setup|Mfa Setup]]
- [[Userflow/Auth-Access/user-invitation|User Invitation]]

## Module References

- [[frontend/cross-cutting/authentication|Authentication]]
- [[modules/auth/session-management/overview|Session Management]]
- [[backend/notification-system|Notification System]]
