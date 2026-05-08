# MFA Setup

**Area:** Auth & Access
**Trigger:** Employee navigates to security settings (user action - self-service)
**Required Permission(s):** None (any authenticated user can enable MFA on their own account)
**Related Permissions:** `users:manage` (admin can enforce MFA for all users or reset MFA for a user)

---

## Phase 1 Rule

MFA uses authenticator-app TOTP as the primary method. Email OTP is allowed only as a fallback or recovery method when policy permits it.

## Preconditions

- User is authenticated and has an active session.
- User has an authenticator app that supports TOTP, such as Microsoft Authenticator, Google Authenticator, 1Password, or similar.
- User has a verified email address for recovery and fallback notifications.
- Email delivery is configured through the notification/email boundary for fallback/recovery only. Phase 1 customer release requires Resend-backed delivery for any email fallback.

## Flow Steps

### Step 1: Navigate to Security Settings
- **UI:** Click user avatar > Security Settings or Profile > Security tab. Page shows password status, MFA status, verified email, and active sessions.
- **API:** `GET /api/v1/users/me/security`
- **DB:** `users`, `user_mfa`, `sessions`

### Step 2: Enable TOTP MFA
- **UI:** User clicks "Enable two-factor authentication". Page shows a QR code and manual setup key for an authenticator app.
- **API:** `POST /api/v1/auth/mfa/enable`
- **Backend:** `MfaService.BeginTotpSetupAsync()` creates `user_mfa.method = totp` with an encrypted TOTP secret and marks it unverified until confirmation.
- **Validation:** MFA must not already be enabled.
- **DB:** `user_mfa`

### Step 3: Confirm With TOTP
- **UI:** User enters the 6-digit code from their authenticator app.
- **API:** `POST /api/v1/auth/mfa/confirm`
- **Backend:** Verifies the submitted TOTP against the encrypted secret, allowing a small clock-skew window, then marks the method verified.
- **Validation:** Code must be current and must not be reused inside the accepted window.
- **DB:** `user_mfa`

### Step 4: MFA Enabled
- **UI:** Success message: "Two-factor authentication has been enabled." Security Settings now shows authenticator app enabled.
- **Events:** `MfaEnabledEvent`, audit log `mfa.enabled`.

## Admin Operations

- Admin can require MFA for all users through tenant security settings.
- Admin can reset a user's MFA via `DELETE /api/v1/users/{userId}/mfa` with `users:manage`.
- Reset deletes active `user_mfa` method rows for that user.

## Error Scenarios

| Scenario | Handling |
|:---|:---|
| Invalid TOTP | Return validation error |
| TOTP clock drift | Show guidance to sync device time |
| Recovery email not verified | Allow TOTP setup but require verified email before email fallback can be used |
| Email fallback unavailable | Production returns delivery failure for fallback/recovery only |

## Related

- [[Userflow/Auth-Access/login-flow|Login Flow]]
- [[Userflow/Auth-Access/password-reset|Password Reset]]
- [[Userflow/Auth-Access/user-invitation|User Invitation]]
- [[modules/auth/mfa/overview|MFA]]
- [[modules/notifications/overview|Notifications]]
- [[modules/auth/session-management/overview|Session Management]]
- [[modules/configuration/overview|Configuration]]
