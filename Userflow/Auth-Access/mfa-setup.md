# MFA Setup

**Area:** Auth & Access
**Trigger:** Employee navigates to security settings (user action - self-service)
**Required Permission(s):** None (any authenticated user can enable MFA on their own account)
**Related Permissions:** `users:manage` (admin can enforce MFA for all users or reset MFA for a user)

---

## Phase 1 Rule

MFA uses email OTP in Phase 1. Authenticator-app TOTP is deferred/optional and must not be the default flow.

## Preconditions

- User is authenticated and has an active session.
- User has a verified email address.
- Email delivery is configured through the notification/email boundary. Local development may log OTPs; Phase 1 customer release requires Resend-backed delivery.

## Flow Steps

### Step 1: Navigate to Security Settings
- **UI:** Click user avatar > Security Settings or Profile > Security tab. Page shows password status, MFA status, verified email, and active sessions.
- **API:** `GET /api/v1/users/me/security`
- **DB:** `users`, `user_mfa`, `sessions`

### Step 2: Enable Email OTP MFA
- **UI:** User clicks "Enable two-factor authentication". Copy explains that sign-in will require a 6-digit code sent to the verified email address.
- **API:** `POST /api/v1/auth/mfa/enable`
- **Backend:** `MfaService.EnableEmailOtpAsync()` creates or verifies `user_mfa.method = email_otp`.
- **Validation:** Email must be verified. MFA must not already be enabled.
- **DB:** `user_mfa`

### Step 3: Confirm With OTP
- **UI:** System sends a 6-digit code and asks the user to enter it. The page shows masked email, expiry, and resend cooldown.
- **API:** `POST /api/v1/auth/mfa/send`, then `POST /api/v1/auth/mfa/verify`
- **Backend:** Creates `mfa_otp_challenges`, sends code, verifies hash, marks challenge consumed.
- **Validation:** Code expires after 5 minutes and locks after 3 failed attempts.
- **DB:** `mfa_otp_challenges`

### Step 4: MFA Enabled
- **UI:** Success message: "Two-factor authentication has been enabled." Security Settings now shows email OTP enabled.
- **Events:** `MfaEnabledEvent`, audit log `mfa.enabled`.

## Admin Operations

- Admin can require MFA for all users through tenant security settings.
- Admin can reset a user's MFA via `DELETE /api/v1/users/{userId}/mfa` with `users:manage`.
- Reset deletes active `user_mfa` method rows and unconsumed OTP challenges for that user.

## Error Scenarios

| Scenario | Handling |
|:---|:---|
| Email not verified | Block setup and require email verification |
| Resend/notification unavailable | Local dev logs code; production returns delivery failure |
| Invalid OTP | Increment attempt counter |
| OTP expired | User must resend code |
| Too many attempts | Challenge locks |

## Related

- [[Userflow/Auth-Access/login-flow|Login Flow]]
- [[Userflow/Auth-Access/password-reset|Password Reset]]
- [[Userflow/Auth-Access/user-invitation|User Invitation]]
- [[modules/auth/mfa/overview|MFA]]
- [[modules/notifications/overview|Notifications]]
- [[modules/auth/session-management/overview|Session Management]]
- [[modules/configuration/overview|Configuration]]
