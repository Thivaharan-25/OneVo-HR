# Login Flow

**Area:** Auth & Access
**Required Permission(s):** None (public endpoint, any user)
**Related Permissions:** All — after login, the user's effective permissions determine what they can access

---

## Preconditions

- User account exists with status `active` (via [[user-invitation|User Invitation]] or [[employee-onboarding|Employee Onboarding]])
- User knows their email and password (or SSO is configured for their tenant)

## Flow Steps

### Step 1: Navigate to Login Page
- **UI:** User opens `https://{tenant}.onevo.app/login` (or custom domain if configured via [[tenant-branding]]). Login page displays: tenant logo, email field, password field, "Remember me" checkbox, "Forgot Password?" link, "Sign in with SSO" button (if SSO configured). If tenant not found by subdomain: generic ONEVO login page with tenant selector
- **API:** `GET /api/v1/tenants/resolve?domain={hostname}` (resolves tenant from subdomain/custom domain)
- **Backend:** `TenantResolver.ResolveAsync()` → [[infrastructure]]
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
- **Backend:** `AuthService.LoginAsync()` → [[authentication]]
  1. Look up user by email + tenant_id
  2. Verify password hash (bcrypt compare)
  3. Check user status is `active` (not `disabled`, `invited`, or `locked`)
  4. Check for account lockout (5 failed attempts → 15-minute lockout)
  5. Record login attempt in `login_attempts` (success or failure)
  6. If password valid and no MFA: proceed to Step 5
  7. If password valid and MFA enabled: return `mfa_required: true` with temporary MFA token
- **Validation:** Email must exist in tenant. Password must match hash. Account must not be locked. Account must be active
- **DB:** `users`, `login_attempts`

### Step 4: MFA Verification (if enabled)
- **UI:** MFA challenge screen appears: "Enter the 6-digit code from your authenticator app". Input field for TOTP code (6 digits, auto-tab between digits). "Use backup code" link. 30-second countdown timer showing code validity window
- **API:** `POST /api/v1/auth/mfa/verify`
  ```json
  {
    "mfaToken": "temporary-mfa-token",
    "code": "123456"
  }
  ```
- **Backend:** `MfaService.VerifyAsync()` → [[mfa]]
  1. Validate temporary MFA token (valid for 5 minutes)
  2. Verify TOTP code against user's MFA secret (using TOTP algorithm with 30-second window, allowing 1 step drift)
  3. If backup code used: mark code as consumed
  4. If valid: proceed to Step 5
  5. If invalid: increment MFA attempt counter (3 max attempts per MFA token)
- **Validation:** MFA token must be valid. Code must match. Max 3 attempts
- **DB:** `user_mfa_settings`, `mfa_backup_codes` (if backup code used)

### Step 5: Token Issuance
- **UI:** N/A (backend processing)
- **API:** Response from login or MFA verify:
  ```json
  {
    "accessToken": "jwt-access-token",
    "refreshToken": "refresh-token",
    "expiresIn": 900,
    "user": {
      "id": "uuid",
      "firstName": "Jane",
      "lastName": "Doe",
      "email": "jane@acme.com",
      "permissions": ["employees:read", "leave:create", ...]
    }
  }
  ```
- **Backend:** `TokenService.GenerateAccessTokenAsync()` → [[authentication]]
  1. Compute effective permissions: role permissions + overrides (see [[permission-assignment]])
  2. Generate JWT RS256 access token (15-minute expiry) with claims: `sub` (userId), `tenant_id`, `permissions[]`, `employee_id`, `iat`, `exp`
  3. Generate refresh token (7-day expiry, or 30 days if "remember me"), store hash in `refresh_tokens`
  4. Create session record in `sessions` table
  5. Set refresh token in HTTP-only secure cookie (SameSite=Strict)
  6. Return access token in response body
- **Validation:** N/A
- **DB:** `sessions` (created), `refresh_tokens` (created), `user_roles`, `role_permissions`, `user_permission_overrides`

### Step 6: Redirect to Dashboard
- **UI:** User redirected to `/dashboard`. Dashboard loads based on permissions:
  - Widgets visible based on permission checks (e.g., "Team Leave" widget requires `leave:read-team`)
  - Navigation sidebar built from permitted modules
  - Quick actions based on write permissions
  - Pending approvals count (if user has any `*:approve` permissions)
- **API:** `GET /api/v1/dashboard`
- **Backend:** `DashboardService.GetDashboardAsync()` — assembles widgets based on user's effective permissions
- **Validation:** JWT validated on every request via middleware
- **DB:** Various tables for dashboard widgets

### Step 7: SignalR Connection Established
- **UI:** No visible UI change. Connection status icon in footer (green dot = connected)
- **API:** WebSocket connection to `/hubs/notifications`
- **Backend:** `NotificationHub.OnConnectedAsync()` — registers user's connection for real-time notifications, permission updates, and presence tracking
- **Validation:** JWT included in WebSocket handshake for authentication
- **DB:** None (in-memory connection tracking)

## Variations

### When SSO login is used
- User clicks "Sign in with SSO"
- Redirected to identity provider (Google/Azure AD) login page
- After successful IDP authentication, redirected back to callback URL
- `AuthService.HandleSsoCallbackAsync()` validates the IDP token, maps user, issues ONEVO JWT
- MFA step is skipped (handled by the IDP)

### When GDPR consent is pending
- After successful login, before dashboard access
- [[gdpr-consent|GDPR Consent Flow]] dialog appears
- User must accept required consents before proceeding
- If monitoring consent declined: monitoring features disabled for this user

### When session already exists (returning user)
- If valid refresh token exists in cookie: attempt silent refresh
- `POST /api/v1/auth/refresh` with refresh token
- If valid: new access token issued, user goes straight to dashboard
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

- `UserLoggedInEvent` → [[event-catalog]] — consumed by session tracking, audit logging
- `LoginFailedEvent` → [[event-catalog]] — consumed by security monitoring, lockout counter
- `SessionCreatedEvent` → [[event-catalog]] — consumed by presence tracking
- `AuditLogEntry` (action: `auth.login.success` or `auth.login.failed`) → [[audit-logging]]

## Related Flows

- [[password-reset]] — "Forgot Password?" link on login page
- [[mfa-setup]] — enabling MFA before this flow
- [[sso-configuration]] — SSO setup by admin
- [[gdpr-consent]] — consent collection after login
- [[user-invitation]] — account creation before first login
- [[employee-offboarding]] — disabled accounts cannot login

## Module References

- [[authentication]] — login logic, JWT RS256 token issuance
- [[authorization]] — effective permission computation for JWT claims
- [[session-management]] — session creation and tracking
- [[mfa]] — TOTP verification
- [[auth-architecture]] — overall auth design
- [[auth-flow]] — authentication flow diagrams
- [[infrastructure]] — tenant resolution, multi-tenancy
