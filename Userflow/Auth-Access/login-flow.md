# Login Flow

**Area:** Auth & Access
**Trigger:** User navigates to login page (user action - every session)
**Required Permission(s):** None (public endpoint, any user)
**Related Permissions:** All - after login, the user's effective permissions determine what they can access

---

## Preconditions

- User account exists with status `active` (via [[Userflow/Auth-Access/user-invitation|User Invitation]] or [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]])
- User knows their email and password (or SSO is configured for their tenant)

## Flow Steps

### Step 1: Navigate to Login Page
- **UI:** User opens `https://{tenantSlug}.onevo.com/login`. Login page displays: tenant logo, email field, password field, "Remember me" checkbox, "Forgot Password?" link, "Sign in with SSO" button (if SSO configured), and footer links to Terms and Privacy. The login button is not blocked by legal checkboxes; required Legal & Privacy items are checked after authentication when the backend knows the exact user, tenant, policy, and accepted versions. If tenant not found by subdomain: generic ONEVO login page with tenant selector.
- **API:** `GET /api/v1/tenants/resolve?host={hostname}` (resolves tenant from ONEVO subdomain)
- **Backend:** `TenantResolver.ResolveAsync()` -> [[modules/infrastructure/overview|Infrastructure]]
- **Validation:** Tenant must exist and be active
- **DB:** `tenants`, `tenant_branding` (for logo/colors)

### Step 2: Enter Credentials
- **UI:** User enters email address and password. "Show password" toggle icon. Client-side validation: email format, password not empty
- **API:** N/A (client-side form entry)
- **Backend:** N/A
- **Validation:** Client-side: valid email format, password not empty
- **DB:** None

### Step 3: Submit Login
- **UI:** Click "Sign In" button or press Enter. Loading spinner on button
- **API:** `POST /api/v1/auth/login`
  ```json
  {
    "email": "jane@acme.com",
    "password": "SecurePass123!",
    "rememberMe": true
  }
  ```
- **Backend:** `AuthService.LoginAsync()` -> [[frontend/cross-cutting/authentication|Authentication]]
  1. Look up user by email + tenant_id
  2. Verify password hash (bcrypt compare)
  3. Check user status is `active` (not `disabled`, `invited`, or `locked`)
  4. Check for account lockout (5 failed attempts -> 15-minute lockout)
  5. Record login attempt in `login_attempts` (success or failure)
  6. If password valid and no MFA: proceed to Step 5
  7. If password valid and MFA enabled: return `mfa_required: true` with temporary MFA token
- **Validation:** Email must exist in tenant. Password must match hash. Account must not be locked. Account must be active
- **DB:** `users`, `login_attempts`

### Step 4: MFA Verification (if enabled)
- **UI:** MFA challenge screen appears: "Enter the 6-digit code from your authenticator app". Input field for TOTP code (6 digits, auto-tab between digits). If policy permits email fallback, "Use recovery option" can start an email OTP fallback flow.
- **API:** `POST /api/v1/auth/mfa/verify`
  ```json
  {
    "mfaToken": "temporary-mfa-token",
    "code": "123456"
  }
  ```
- **Backend:** `MfaService.VerifyAsync()` -> [[modules/auth/mfa/overview|MFA]]
  1. Validate temporary MFA token (valid for 5 minutes)
  2. Load verified `totp` MFA method for the user
  3. Verify submitted code against the encrypted TOTP secret with a small clock-skew window
  4. Reject reused codes inside the accepted window
  5. If valid: proceed to Step 5
  6. If invalid: return invalid MFA code
- **Validation:** MFA token must be valid. Code must match the current TOTP window.
- **DB:** `user_mfa`
- **Fallback:** If email fallback is enabled, user can request an email OTP through `POST /api/v1/auth/mfa/send`; the fallback challenge is hashed, short-lived, single-use, and separate from the primary TOTP method.

### Step 5: Session Creation
- **UI:** N/A (backend processing)
- **API:** Response from login or MFA verify sets an HttpOnly session cookie and returns safe session metadata:
  ```json
  {
    "authenticated": true,
    "user": {
      "id": "uuid",
      "firstName": "Jane",
      "lastName": "Doe",
      "email": "jane@acme.com"
    },
    "permissions": ["employees:read", "leave:create"],
    "active_modules": ["core_hr", "leave"],
    "active_features": ["core_hr.employee_profiles", "leave.requests"]
  }
  ```
- **Backend:** `AuthSessionService.CreateSessionAsync()` -> [[frontend/cross-cutting/authentication|Authentication]]
  1. Compute effective permissions: role permissions + overrides (see [[Userflow/Auth-Access/permission-assignment|Permission Assignment]])
  2. Create backend-held auth state or internal tenant token; do not return the JWT to browser JavaScript
  3. Create session record in `sessions` table
  4. Store refresh/session rotation state server-side
  5. Set HttpOnly Secure SameSite session cookie
  6. Return user, permissions, active module keys, and active feature keys in the response body
- **Validation:** N/A
- **DB:** `sessions` (created), `refresh_tokens` or session rotation records (created), `user_roles`, `role_permissions`, `user_permission_overrides`
### Step 6: Legal & Privacy Gate
- **UI:** If the user has pending platform-required Legal & Privacy items, redirect to `/legal-privacy` before dashboard access. If only WorkPulse collection-required monitoring/screenshot/biometric items are pending, the dashboard may load and shows a WorkPulse setup/status task instead of desktop collection checkboxes. The web Legal & Privacy screen shows only missing or changed web items, such as updated Terms & Conditions or updated Privacy Notice.
- **API:** `GET /api/v1/legal/pending`, then `POST /api/v1/legal/acceptances`
- **Backend:** Resolves pending web legal items from active legal document versions and the user's previous acceptance records. WorkPulse collection items are resolved for status display but completed inside the desktop app.
- **Validation:** Terms and Privacy Notice acknowledgement block dashboard access when missing. Monitoring/screenshot/biometric items block only the affected WorkPulse collection category unless product/legal policy explicitly requires full access blocking.
- **DB:** Legal acceptance/consent records

### Step 7: Redirect to Dashboard
- **UI:** User redirected to `/dashboard`. Dashboard loads based on permissions:
  - Widgets visible based on permission checks (e.g., "Team Leave" widget requires `leave:read` with team/reporting access policy)
  - Navigation sidebar built from permitted modules
  - Quick actions based on write permissions
  - Pending approvals count (if user has any `*:approve` permissions)
- **API:** `GET /api/v1/dashboard`
- **Backend:** `DashboardService.GetDashboardAsync()` - assembles widgets based on user's effective permissions
- **Validation:** HttpOnly session cookie validated on every request via middleware
- **DB:** Various tables for dashboard widgets

### Step 8: SignalR Connection Established
- **UI:** No visible UI change. Connection status icon in footer (green dot = connected)
- **API:** WebSocket connection to `/hubs/notifications`
- **Backend:** `NotificationHub.OnConnectedAsync()` - registers user's connection for real-time notifications, permission updates, and presence tracking
- **Validation:** cookie-backed session included in the WebSocket handshake for authentication
- **DB:** None (in-memory connection tracking)

## Variations

### When SSO login is used
- User clicks "Sign in with SSO"
- Redirected to identity provider (Google/Azure AD) login page
- After successful IDP authentication, redirected back to callback URL
- `AuthService.HandleSsoCallbackAsync()` validates the IDP token, maps user, creates the ONEVO web session
- MFA step is skipped (handled by the IDP)

### When Legal & Privacy items are pending
- After successful login, before dashboard access
- [[Userflow/Auth-Access/gdpr-consent|Legal & Privacy Acceptance]] screen appears
- User must accept/acknowledge required Terms and Privacy Notice items before proceeding
- If a tenant later enables activity monitoring, screenshots, or photo/biometric verification, the web dashboard may show a WorkPulse setup/status task
- If monitoring/screenshot/photo/biometric items remain incomplete, affected desktop collection is disabled until the user completes the notice/consent inside WorkPulse

### When session already exists (returning user)
- If valid session cookie exists: attempt session refresh
- `POST /api/v1/auth/refresh` with `credentials: "include"`
- If valid: session metadata is refreshed, then the Legal & Privacy gate is evaluated before dashboard access or affected collection
- If invalid/expired: redirect to login page

### When user has sessions on multiple devices
- Each login creates a separate session
- Session list viewable in Security Settings
- Admin can view all user sessions and revoke any

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Invalid email | `401 Unauthorized` (generic) | "Invalid email or password" (no hint about which is wrong) |
| Invalid password | `401 Unauthorized` (generic), attempt counter incremented | "Invalid email or password" |
| Account locked (5 failed attempts) | `423 Locked` returned | "Account temporarily locked due to multiple failed attempts. Try again in 15 minutes or contact your administrator" |
| Account disabled | `403 Forbidden` returned | "Your account has been disabled. Contact your administrator" |
| Tenant inactive | `403 Forbidden` returned | "This organization's account is currently inactive" |
| Invalid MFA code | Attempt counter incremented | "Invalid verification code. X attempts remaining" |
| MFA token expired | Must restart login | "Verification session expired. Please sign in again" |
| SSO provider error | Redirect back with error | "Single sign-on failed. Please try again or contact your administrator" |

## Events Triggered

- `UserLoggedInEvent` -> [[backend/messaging/event-catalog|Event Catalog]] - consumed by session tracking, audit logging
- `LoginFailedEvent` -> [[backend/messaging/event-catalog|Event Catalog]] - consumed by security monitoring, lockout counter
- `SessionCreatedEvent` -> [[backend/messaging/event-catalog|Event Catalog]] - consumed by presence tracking
- `AuditLogEntry` (action: `auth.login.success` or `auth.login.failed`) -> [[modules/auth/audit-logging/overview|Audit Logging]]

## Related Flows

- [[Userflow/Auth-Access/password-reset|Password Reset]] - "Forgot Password?" link on login page
- [[Userflow/Auth-Access/mfa-setup|Mfa Setup]] - enabling MFA before this flow
- [[Userflow/Platform-Setup/sso-configuration|Sso Configuration]] - SSO setup by admin
- [[Userflow/Auth-Access/gdpr-consent|Legal & Privacy Acceptance]] - legal/privacy notices after login and policy changes
- [[Userflow/Auth-Access/user-invitation|User Invitation]] - account creation before first login
- [[Userflow/Employee-Management/employee-offboarding|Employee Offboarding]] - disabled accounts cannot login

## Module References

- [[frontend/cross-cutting/authentication|Authentication]] - login logic, BFF session creation, backend-held auth state
- [[frontend/cross-cutting/authorization|Authorization]] - effective permission computation for backend session metadata
- [[modules/auth/session-management/overview|Session Management]] - session creation and tracking
- [[modules/auth/mfa/overview|MFA]] - TOTP verification with optional email fallback
- [[security/auth-architecture|Auth Architecture]] - overall auth design
- [[security/auth-flow|Auth Flow]] - authentication flow diagrams
- [[modules/infrastructure/overview|Infrastructure]] - tenant resolution, multi-tenancy



