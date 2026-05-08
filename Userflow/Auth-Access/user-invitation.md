# User Invitation

**Area:** Auth & Access
**Trigger:** Admin clicks Invite User (user action)
**Required Permission(s):** `users:manage`
**Related Permissions:** `roles:manage` (to create new roles during invitation), `employees:write` (to create employee profile simultaneously)

---

## Preconditions

- Tenant is active with a valid subscription
- At least one role exists for assignment (system roles are always available)
- Email service is configured and operational
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to User Management
- **UI:** Administration > Users. List view shows all users with columns: Name, Email, Role, Status (Active/Invited/Disabled), Last Login. "Invite User" button in top-right
- **API:** `GET /api/v1/users?page=1&pageSize=20`
- **Backend:** `UserService.GetUsersAsync()` â†’ [[frontend/cross-cutting/authentication|Authentication]]
- **Validation:** Permission check for `users:manage`
- **DB:** `users`, `user_roles`, `roles`

### Step 2: Click Invite User
- **UI:** Modal dialog opens with invitation form:
  - Email Address (required)
  - First Name (required)
  - Last Name (required)
  - Role (dropdown, required) â€” lists all tenant roles
  - Department (dropdown, optional) â€” if employee profile should be created
  - Job Family Level (dropdown, optional) â€” triggers auto-role assignment from [[Userflow/Org-Structure/job-family-setup|Job Family]]
  - Send welcome email (checkbox, default: checked)
- **API:** N/A (client-side form)
- **Backend:** N/A
- **Validation:** Client-side email format validation
- **DB:** None

### Step 3: Submit Invitation
- **UI:** Click "Send Invitation" button. Loading state shown on button
- **API:** `POST /api/v1/users/invite`
  ```json
  {
    "email": "jane@acme.com",
    "firstName": "Jane",
    "lastName": "Doe",
    "roleId": "uuid",
    "departmentId": "uuid",
    "jobFamilyLevelId": "uuid"
  }
  ```
- **Backend:** `UserInvitationService.InviteAsync()` â†’ [[frontend/cross-cutting/authentication|Authentication]]
  1. Check if email already exists in tenant â†’ reject if so
  2. Create user record with status `invited` and a secure invitation token (SHA-256 hashed, stored in DB)
  3. If department/job family provided: create employee profile stub
  4. If job family level provided: auto-assign the role linked to that job family level (overrides manually selected role)
  5. Assign selected role to user via `user_roles`
  6. Send invitation email with link: `https://{tenant}.onevo.app/accept-invite?token={token}`
  7. Invitation token expires in 72 hours
- **Validation:** Email must be unique within tenant. Role must exist. If job family level specified, it must be valid
- **DB:** `users` (status: `invited`), `user_roles`, `invitation_tokens`, `employees` (if department provided)

### Step 4: User Receives Invitation Email
- **UI:** Email contains: company name and logo (from [[frontend/design-system/theming/tenant-branding|Tenant Branding]]), inviter's name, role being assigned, "Accept Invitation" button/link, expiry notice (72 hours)
- **API:** N/A (email delivery via [[backend/notification-system|Notification System]])
- **Backend:** `NotificationService.SendEmailAsync()` â€” uses tenant-branded email template
- **Validation:** Email delivery tracked. If bounce detected, admin notified
- **DB:** `notification_logs`

### Step 5: User Opens Invitation
- **UI:** Clicking the link opens the accept-invite page. The page shows tenant name, invited email, name, role, expiry, and available acceptance methods.
- **API:** `GET /api/v1/auth/invitations/{token}`
- **Backend:** `UserInvitationService.GetInvitationPreviewAsync()` -> [[frontend/cross-cutting/authentication|Authentication]]
  1. Validate invitation token exists
  2. Return safe preview data only
  3. Mark expired tokens as expired in the response
- **Validation:** Token must exist. Expired or used tokens are shown as not acceptable.
- **DB:** `invitation_tokens`, `users`, `roles`, `tenants`

### Step 6A: Accept Invite With Password
- **UI:** If password setup is enabled, the page shows pre-filled invited email (read-only), set password, confirm password, optional phone number, and "Create Account".
- **API:** `POST /api/v1/auth/invitations/{token}/accept-password`
  ```json
  {
    "password": "SecurePass123!",
    "phone": "+94771234567"
  }
  ```
- **Backend:** `UserInvitationService.AcceptInvitationWithPasswordAsync()` -> [[frontend/cross-cutting/authentication|Authentication]]
  1. Validate invitation token (not expired, not already used)
  2. Use the original invited email as the account email
  3. Hash password with BCrypt using the configured platform password hasher
  4. Update user status from `invited` to `active`
  5. Mark invitation token as used
  6. Create HttpOnly cookie-backed web session; do not return tenant JWT to browser JavaScript
  7. Create initial session record
  8. Redirect to dashboard when tenant is active; if tenant is still provisioning, show "account ready, waiting for activation"
- **Validation:** Token must be valid and not expired. Password must meet complexity requirements. Accepting with password does not allow changing the invited email.
- **DB:** `users` (status -> `active`, password_hash set), `invitation_tokens` (used_at set), `sessions`, `refresh_tokens`

### Step 6B: Accept Invite With Google
- **UI:** If Google sign-in is enabled for invite acceptance, the page shows "Continue with Google". The user may choose the same email as the invitation, or a different Google account only when the invitation or tenant policy allows email mismatch.
- **API:** `POST /api/v1/auth/invitations/{token}/accept-google`
  ```json
  {
    "google_id_token": "google-id-token"
  }
  ```
- **Backend:** `UserInvitationService.AcceptInvitationWithGoogleAsync()` -> [[frontend/cross-cutting/authentication|Authentication]]
  1. Validate invitation token (not expired, not already used)
  2. Validate Google ID token, email verification, and Google subject
  3. If Google email matches invited email, activate normally
  4. If Google email differs, allow only when `allow_google_email_mismatch` is true and the Google email domain is permitted
  5. Store the verified Google identity according to the existing Auth/SSO user model, set the primary login email, and retain the original invited email on the invitation/audit record
  6. Do not set a password
  7. Mark invitation token as used
  8. Create HttpOnly cookie-backed web session when the tenant is active
- **Validation:** Token must be valid and not expired. Google email must be verified. Mismatched Google email is rejected by default unless explicitly allowed by tenant/invitation policy.
- **DB:** `users` (status -> `active`, google_sub set, invited_email retained), `invitation_tokens` (used_at set), `sessions`, `refresh_tokens`

### Step 7: Account Active
- **UI:** User lands on the dashboard. First-time onboarding tour shown (profile completion prompts). If GDPR consent required: [[Userflow/Auth-Access/gdpr-consent|consent dialog]] appears before dashboard access
- **API:** `GET /api/v1/dashboard`
- **Backend:** Dashboard loads based on user's role permissions. Only widgets for permitted features are shown
- **Validation:** Cookie-backed session valid
- **DB:** `sessions` (last_activity_at updated)

## Variations

### When inviting multiple users (bulk invite)
- Admin uploads CSV file with columns: email, firstName, lastName, roleName, department
- System validates all rows before sending any invitations
- Progress bar shows: "Sending 45 of 100 invitations..."
- Summary report: successful sends, failed (with reasons)

### When invitation expires
- User clicks expired link â†’ "This invitation has expired. Please contact your administrator for a new invitation"
- Admin can resend invitation from the Users list: click user row â†’ "Resend Invitation"
- New token generated, previous one invalidated

### When SSO is enabled for the tenant
- Invitation email still sent, but "Accept Invitation" links to SSO login instead of password creation
- User authenticates via SSO provider â†’ account auto-activated
- No password is set (SSO-only authentication)

### When Google email differs from invited email
- Default behavior: reject with `409 Conflict` and ask the user to sign in with the invited email or contact the administrator.
- Allowed behavior: if tenant/invitation policy permits mismatch and the Google email domain is allowed, activate the account using the verified Google email as primary login email.
- The original invited email is retained for audit and support.
- Every mismatch acceptance writes an audit log with invited email, accepted Google email, tenant, token ID, and acceptance time.

### When user already exists in another tenant
- Each tenant is isolated â€” same email can exist in multiple tenants
- User gets a separate account per tenant with independent credentials

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Email already registered | `409 Conflict` returned | "A user with this email already exists in your organization" |
| Invalid role ID | `404 Not Found` returned | "The selected role does not exist" |
| Email delivery fails | User created but marked `invite_pending` | Admin sees: "Invitation created but email delivery failed. Click to retry" |
| Expired invitation token | `410 Gone` returned | "This invitation has expired. Please contact your administrator" |
| Weak password | `400 Bad Request` returned | "Password must be at least 12 characters with uppercase, lowercase, number, and special character" |

## Events Triggered

- `UserInvitedEvent` â†’ [[backend/messaging/event-catalog|Event Catalog]] â€” consumed by audit logging and notification module
- `UserActivatedEvent` â†’ [[backend/messaging/event-catalog|Event Catalog]] â€” consumed by onboarding workflow
- `AuditLogEntry` (action: `user.invited`) â†’ [[modules/auth/audit-logging/overview|Audit Logging]]
- `AuditLogEntry` (action: `user.activated`) â†’ [[modules/auth/audit-logging/overview|Audit Logging]]

## Related Flows

- [[Userflow/Auth-Access/role-creation|Role Creation]] â€” create roles before inviting users
- [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] â€” configure role permissions
- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]] â€” full onboarding flow after user accepts invitation
- [[Userflow/Auth-Access/login-flow|Login Flow]] â€” user's first login after accepting invitation
- [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]] â€” consent collection on first login

## Module References

- [[frontend/cross-cutting/authentication|Authentication]] â€” user creation, password hashing, token issuance
- [[frontend/cross-cutting/authorization|Authorization]] â€” role assignment during invitation
- [[backend/notification-system|Notification System]] â€” invitation email delivery
- [[modules/core-hr/employee-profiles/overview|Employee Profiles]] â€” employee profile stub creation
- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]] â€” auto-role assignment from job family level

