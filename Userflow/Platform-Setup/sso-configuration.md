# SSO Configuration

**Area:** Platform Setup
**Trigger:** Admin navigates to SSO settings (user action — configuration)
**Required Permission(s):** `settings:admin`
**Related Permissions:** `users:manage` (to enforce SSO-only login for specific users)

---

## Preconditions

- Tenant is active with a valid subscription
- Admin has credentials for the identity provider (Google Workspace, Azure AD, or Okta)
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to SSO Settings
- **UI:** Settings > Security > Single Sign-On. Page shows current SSO status (Disabled/Enabled), configured provider (if any), and login method settings (SSO only, SSO + password, password only)
- **API:** `GET /api/v1/settings/sso`
- **Backend:** `SsoConfigurationService.GetConfigAsync()` → [[modules/shared-platform/sso-authentication/overview|Sso Authentication]]
- **Validation:** Permission check for `settings:admin`
- **DB:** `sso_configurations`

### Step 2: Select Identity Provider
- **UI:** Provider selection cards: Google Workspace, Azure AD (Microsoft Entra ID), Okta, Custom SAML 2.0, Custom OIDC. Each card shows setup complexity and estimated time. Click "Configure" on chosen provider
- **API:** N/A (client-side navigation)
- **Backend:** N/A
- **Validation:** N/A
- **DB:** None

### Step 3: Enter Provider Credentials
- **UI:** Form fields vary by provider:
  - **Google:** Client ID, Client Secret, Hosted Domain (optional, restricts to specific Google Workspace domain)
  - **Azure AD:** Application (client) ID, Client Secret, Tenant ID, Directory (tenant) ID
  - **Okta:** Okta Domain, Client ID, Client Secret
  - **Custom SAML:** Entity ID, SSO URL, Certificate (file upload), Attribute Mapping
  - **Custom OIDC:** Issuer URL, Client ID, Client Secret, Scopes
- **API:** N/A (client-side form entry)
- **Backend:** N/A
- **Validation:** Client-side format validation for URLs and IDs
- **DB:** None

### Step 4: Configure Callback URL
- **UI:** System displays the callback/redirect URL that must be registered in the identity provider's console (e.g., `https://{tenant}.onevo.app/api/v1/auth/sso/callback`). Copy button provided. Instructions panel with step-by-step guide for the selected provider
- **API:** N/A (display only)
- **Backend:** Callback URL generated from tenant configuration
- **Validation:** N/A
- **DB:** None

### Step 5: Configure Attribute Mapping
- **UI:** Map identity provider attributes to ONEVO user fields: Email (required), First Name, Last Name, Employee ID (optional), Department (optional). Default mappings pre-filled based on provider
- **API:** N/A (client-side form entry)
- **Backend:** N/A
- **Validation:** Email mapping is mandatory
- **DB:** None

### Step 6: Test Connection
- **UI:** Click "Test Connection" button. Opens a popup window that redirects to the identity provider login page. After successful authentication, popup closes and shows test results: connected user's email, mapped attributes, any warnings
- **API:** `POST /api/v1/settings/sso/test`
- **Backend:** `SsoConfigurationService.TestConnectionAsync()` — performs OAuth/SAML flow with the provider, validates response, returns mapped user data without creating a session
- **Validation:** Provider must return a valid response. Email attribute must be present. Certificate must be valid (SAML)
- **DB:** None (test only, nothing persisted)

### Step 7: Save and Enable SSO
- **UI:** Review configuration summary. Toggle "Enable SSO" switch. Select login policy: "SSO Only" (password login disabled), "SSO + Password" (both allowed), or "SSO Preferred" (SSO shown first, password link available). Click "Save Configuration"
- **API:** `POST /api/v1/settings/sso`
- **Backend:** `SsoConfigurationService.SaveAndEnableAsync()` → [[modules/shared-platform/sso-authentication/overview|Sso Authentication]]
  1. Encrypts and stores client secret using AES-256
  2. Saves configuration to `sso_configurations` table
  3. Updates tenant authentication settings
  4. If "SSO Only": marks all existing password-based sessions for re-authentication on next request
- **Validation:** Test connection must have succeeded before enabling. At least one admin must retain password login capability (safety net)
- **DB:** `sso_configurations`, `tenant_settings`

## Variations

### When SSO-only mode is enabled
- All existing user sessions are flagged for re-authentication
- Users must log in via SSO on their next request
- Password reset flow is disabled for SSO-only users
- Emergency admin bypass: at least one super admin retains password login

### When user does not exist in ONEVO but authenticates via SSO
- If auto-provisioning (JIT) is enabled: user account created automatically with default "Employee" role
- If auto-provisioning is disabled: login rejected with "Account not found. Contact your administrator"

### When updating an existing SSO configuration
- Existing configuration shown pre-filled
- Changes require re-testing the connection
- If switching providers: old provider disabled, new one enabled. Grace period of 24 hours where both work

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Invalid client ID/secret | Test connection fails | "Authentication failed. Please verify your Client ID and Client Secret in the identity provider's console" |
| Callback URL not registered | Provider returns redirect mismatch | "Redirect URI mismatch. Please ensure the callback URL is registered in your identity provider" |
| Certificate expired (SAML) | Signature validation fails | "The SAML certificate has expired. Please upload a new certificate from your identity provider" |
| Provider unreachable | Connection timeout | "Cannot reach the identity provider. Please check the provider URL and your network settings" |
| All admins locked out | Safety check prevents save | "At least one administrator must retain password login access. SSO-only mode cannot be enabled for all admins" |

## Events Triggered

- `SsoConfiguredEvent` → [[backend/messaging/event-catalog|Event Catalog]] — consumed by audit logging
- `AuditLogEntry` (action: `sso.configured`) → [[modules/auth/audit-logging/overview|Audit Logging]]
- `AuditLogEntry` (action: `sso.enabled`) → [[modules/auth/audit-logging/overview|Audit Logging]]

## Related Flows

- [[Userflow/Auth-Access/login-flow|Login Flow]] — SSO changes the login experience
- [[Userflow/Auth-Access/user-invitation|User Invitation]] — invited users may use SSO instead of password
- [[Userflow/Platform-Setup/tenant-provisioning|Tenant Provisioning]] — SSO typically configured after initial setup

## Module References

- [[modules/shared-platform/sso-authentication/overview|Sso Authentication]] — SSO implementation details
- [[security/auth-architecture|Auth Architecture]] — how SSO fits into the auth stack
- [[frontend/cross-cutting/authentication|Authentication]] — JWT issuance after SSO validation
- [[modules/auth/session-management/overview|Session Management]] — session handling with SSO
- [[modules/configuration/overview|Configuration]] — tenant-level SSO settings
