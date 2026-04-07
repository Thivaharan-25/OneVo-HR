# MFA Setup

**Area:** Auth & Access
**Required Permission(s):** None (any authenticated user can enable MFA on their own account)
**Related Permissions:** `users:manage` (admin can enforce MFA for all users or reset MFA for a user)

---

## Preconditions

- User is authenticated and has an active session
- User has a TOTP-compatible authenticator app installed (Google Authenticator, Authy, Microsoft Authenticator, etc.)

## Flow Steps

### Step 1: Navigate to Security Settings
- **UI:** Click user avatar (top-right) > "Security Settings" or navigate to Profile > Security tab. Page shows: Password section (last changed date, "Change Password" button), MFA section (status: Enabled/Disabled), Active Sessions list
- **API:** `GET /api/v1/users/me/security`
- **Backend:** `UserSecurityService.GetSecuritySettingsAsync()` → [[authentication]]
- **Validation:** Authenticated user only (JWT required)
- **DB:** `users`, `user_mfa_settings`, `sessions`

### Step 2: Click Enable MFA
- **UI:** In the MFA section, click "Enable Two-Factor Authentication" button. Information panel explains: "Two-factor authentication adds an extra layer of security. You'll need to enter a code from your authenticator app each time you sign in"
- **API:** `POST /api/v1/auth/mfa/enable`
- **Backend:** `MfaService.InitiateSetupAsync()` → [[mfa]]
  1. Generate a random TOTP secret (Base32 encoded, 160 bits)
  2. Store secret temporarily (not yet confirmed) with status `pending_verification`
  3. Generate QR code data URL from the OTP Auth URI: `otpauth://totp/ONEVO:{email}?secret={secret}&issuer=ONEVO&algorithm=SHA1&digits=6&period=30`
  4. Generate 10 backup codes (8-character alphanumeric, cryptographically random)
  5. Return QR code and backup codes to client
- **Validation:** MFA must not already be enabled for this user
- **DB:** `user_mfa_settings` (status: `pending_verification`, secret stored encrypted)

### Step 3: Scan QR Code
- **UI:** Modal displays:
  1. QR code image (scannable by authenticator app)
  2. Manual entry key (text format of the secret, for manual entry if QR scanning fails)
  3. "I've scanned the QR code" button to proceed
  4. Instructions: "Open your authenticator app, tap + to add account, scan this QR code"
- **API:** N/A (client-side display)
- **Backend:** N/A
- **Validation:** N/A
- **DB:** None

### Step 4: Verify Setup Code
- **UI:** Input field: "Enter the 6-digit code displayed in your authenticator app to verify setup". Submit button. This ensures the user has correctly scanned the QR code
- **API:** `POST /api/v1/auth/mfa/verify-setup`
  ```json
  {
    "code": "123456"
  }
  ```
- **Backend:** `MfaService.ConfirmSetupAsync()` → [[mfa]]
  1. Retrieve pending MFA secret for the user
  2. Validate TOTP code against the secret (30-second window, 1 step drift allowed)
  3. If valid: update `user_mfa_settings` status to `active`
  4. Hash and store backup codes in `mfa_backup_codes`
  5. Publish `MfaEnabledEvent`
- **Validation:** Code must match the TOTP algorithm output. Code must not be reused (replay protection via last-used timestamp)
- **DB:** `user_mfa_settings` (status → `active`), `mfa_backup_codes` (10 codes stored as bcrypt hashes)

### Step 5: Display Backup Codes
- **UI:** Backup codes displayed in a grid (10 codes):
  ```
  A7K2-M3NP    B8L4-Q5RS    C9M6-T7UV
  D1N8-W9XY    E2P0-Z1AB    F3Q2-C4DE
  G4R5-F6GH    H5S7-J8KL    I6T9-M0NP
  J7U1-Q2RS
  ```
  "Download as text file" button, "Copy to clipboard" button, "Print" button.
  Warning: "Save these backup codes in a safe place. Each code can only be used once. If you lose access to your authenticator app, you can use a backup code to sign in"
  
  Checkbox: "I have saved my backup codes" (must be checked to proceed)
- **API:** N/A (codes were returned in Step 2 response, displayed here)
- **Backend:** N/A
- **Validation:** User must acknowledge saving backup codes
- **DB:** None

### Step 6: MFA Enabled
- **UI:** Success message: "Two-factor authentication has been enabled". Security Settings page updates to show MFA status: Enabled, with options: "View Backup Codes" (requires password re-entry), "Regenerate Backup Codes", "Disable MFA"
- **API:** N/A
- **Backend:** N/A
- **Validation:** N/A
- **DB:** None

## Variations

### When admin enforces MFA for all users
- Admin navigates to Settings > Security > MFA Policy
- Toggle "Require MFA for all users"
- `PUT /api/v1/settings/security/mfa-policy` → sets `mfa_required: true` in `tenant_settings`
- On next login, users without MFA see a mandatory setup flow (cannot skip)
- Users receive notification: "Your organization now requires two-factor authentication"

### When admin resets a user's MFA
- Admin navigates to user profile > Security > click "Reset MFA"
- `DELETE /api/v1/users/{userId}/mfa` (requires `users:manage`)
- User's MFA secret and backup codes are deleted
- User must set up MFA again on next login (if MFA is enforced by policy)
- User receives email notification: "Your two-factor authentication has been reset"

### When user disables their own MFA
- From Security Settings, click "Disable MFA"
- Must enter current password to confirm
- If tenant policy requires MFA: disable is blocked with message "Your organization requires two-factor authentication"
- If allowed: MFA secret and backup codes deleted, status set to `disabled`

### When regenerating backup codes
- From Security Settings, click "Regenerate Backup Codes"
- Must enter current password to confirm
- Old backup codes invalidated, 10 new codes generated
- New codes displayed for download/saving

### When using a backup code during login
- During [[login-flow|login]], on MFA screen, click "Use backup code"
- Enter 8-character backup code instead of TOTP code
- Code validated against stored hashes, marked as used
- Warning shown: "You have X backup codes remaining. Consider regenerating if running low"

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| MFA already enabled | `409 Conflict` returned | "Two-factor authentication is already enabled on your account" |
| Invalid verification code | `400 Bad Request` returned | "Invalid verification code. Please check your authenticator app and try again" |
| QR code scanned incorrectly | Code verification fails | "The code doesn't match. Please scan the QR code again or enter the key manually" |
| All backup codes used | No backup codes remaining | "All backup codes have been used. Please generate new backup codes from Security Settings" |
| MFA disable blocked by policy | `403 Forbidden` returned | "Your organization requires two-factor authentication. MFA cannot be disabled" |

## Events Triggered

- `MfaEnabledEvent` → [[event-catalog]] — consumed by audit logging and notification module
- `MfaDisabledEvent` → [[event-catalog]] — consumed by audit logging and security alerting
- `AuditLogEntry` (action: `mfa.enabled`, `mfa.disabled`, `mfa.reset`) → [[audit-logging]]

## Related Flows

- [[login-flow]] — MFA verification during login
- [[password-reset]] — password reset does not disable MFA
- [[user-invitation]] — MFA can be enforced from first login

## Module References

- [[mfa]] — TOTP implementation, backup codes
- [[authentication]] — integration with login flow
- [[session-management]] — session handling after MFA verification
- [[configuration]] — tenant-level MFA policy
