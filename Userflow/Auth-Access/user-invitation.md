# User Invitation

**Area:** Auth & Access
**Required Permission(s):** `users:manage`
**Related Permissions:** `roles:manage` (to create new roles during invitation), `employees:write` (to create employee profile simultaneously)

---

## Preconditions

- Tenant is active with a valid subscription
- At least one role exists for assignment (system roles are always available)
- Email service is configured and operational
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to User Management
- **UI:** Administration > Users. List view shows all users with columns: Name, Email, Role, Status (Active/Invited/Disabled), Last Login. "Invite User" button in top-right
- **API:** `GET /api/v1/users?page=1&pageSize=20`
- **Backend:** `UserService.GetUsersAsync()` → [[authentication]]
- **Validation:** Permission check for `users:manage`
- **DB:** `users`, `user_roles`, `roles`

### Step 2: Click Invite User
- **UI:** Modal dialog opens with invitation form:
  - Email Address (required)
  - First Name (required)
  - Last Name (required)
  - Role (dropdown, required) — lists all tenant roles
  - Department (dropdown, optional) — if employee profile should be created
  - Job Family Level (dropdown, optional) — triggers auto-role assignment from [[job-family-setup|Job Family]]
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
- **Backend:** `UserInvitationService.InviteAsync()` → [[authentication]]
  1. Check if email already exists in tenant → reject if so
  2. Create user record with status `invited` and a secure invitation token (SHA-256 hashed, stored in DB)
  3. If department/job family provided: create employee profile stub
  4. If job family level provided: auto-assign the role linked to that job family level (overrides manually selected role)
  5. Assign selected role to user via `user_roles`
  6. Send invitation email with link: `https://{tenant}.onevo.app/accept-invite?token={token}`
  7. Invitation token expires in 72 hours
- **Validation:** Email must be unique within tenant. Role must exist. If job family level specified, it must be valid
- **DB:** `users` (status: `invited`), `user_roles`, `invitation_tokens`, `employees` (if department provided)

### Step 4: User Receives Invitation Email
- **UI:** Email contains: company name and logo (from [[tenant-branding]]), inviter's name, role being assigned, "Accept Invitation" button/link, expiry notice (72 hours)
- **API:** N/A (email delivery via [[notification-system]])
- **Backend:** `NotificationService.SendEmailAsync()` — uses tenant-branded email template
- **Validation:** Email delivery tracked. If bounce detected, admin notified
- **DB:** `notification_logs`

### Step 5: User Accepts Invitation
- **UI:** Clicking the link opens the registration page: pre-filled email (read-only), set password (with strength meter: min 8 chars, uppercase, lowercase, number, special char), confirm password, optional: phone number. "Create Account" button
- **API:** `POST /api/v1/auth/accept-invitation`
  ```json
  {
    "token": "invitation-token",
    "password": "SecurePass123!",
    "phone": "+94771234567"
  }
  ```
- **Backend:** `UserInvitationService.AcceptInvitationAsync()` → [[authentication]]
  1. Validate invitation token (not expired, not already used)
  2. Hash password with bcrypt (cost factor 12)
  3. Update user status from `invited` to `active`
  4. Mark invitation token as used
  5. Issue JWT access token + refresh token
  6. Create initial session record
  7. Redirect to dashboard
- **Validation:** Token must be valid and not expired. Password must meet complexity requirements
- **DB:** `users` (status → `active`, password_hash set), `invitation_tokens` (used_at set), `sessions`, `refresh_tokens`

### Step 6: Account Active
- **UI:** User lands on the dashboard. First-time onboarding tour shown (profile completion prompts). If GDPR consent required: [[gdpr-consent|consent dialog]] appears before dashboard access
- **API:** `GET /api/v1/dashboard`
- **Backend:** Dashboard loads based on user's role permissions. Only widgets for permitted features are shown
- **Validation:** Session and JWT valid
- **DB:** `sessions` (last_activity_at updated)

## Variations

### When inviting multiple users (bulk invite)
- Admin uploads CSV file with columns: email, firstName, lastName, roleName, department
- System validates all rows before sending any invitations
- Progress bar shows: "Sending 45 of 100 invitations..."
- Summary report: successful sends, failed (with reasons)

### When invitation expires
- User clicks expired link → "This invitation has expired. Please contact your administrator for a new invitation"
- Admin can resend invitation from the Users list: click user row → "Resend Invitation"
- New token generated, previous one invalidated

### When SSO is enabled for the tenant
- Invitation email still sent, but "Accept Invitation" links to SSO login instead of password creation
- User authenticates via SSO provider → account auto-activated
- No password is set (SSO-only authentication)

### When user already exists in another tenant
- Each tenant is isolated — same email can exist in multiple tenants
- User gets a separate account per tenant with independent credentials

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Email already registered | `409 Conflict` returned | "A user with this email already exists in your organization" |
| Invalid role ID | `404 Not Found` returned | "The selected role does not exist" |
| Email delivery fails | User created but marked `invite_pending` | Admin sees: "Invitation created but email delivery failed. Click to retry" |
| Expired invitation token | `410 Gone` returned | "This invitation has expired. Please contact your administrator" |
| Weak password | `400 Bad Request` returned | "Password must be at least 8 characters with uppercase, lowercase, number, and special character" |

## Events Triggered

- `UserInvitedEvent` → [[event-catalog]] — consumed by audit logging and notification module
- `UserActivatedEvent` → [[event-catalog]] — consumed by onboarding workflow
- `AuditLogEntry` (action: `user.invited`) → [[audit-logging]]
- `AuditLogEntry` (action: `user.activated`) → [[audit-logging]]

## Related Flows

- [[role-creation]] — create roles before inviting users
- [[permission-assignment]] — configure role permissions
- [[employee-onboarding]] — full onboarding flow after user accepts invitation
- [[login-flow]] — user's first login after accepting invitation
- [[gdpr-consent]] — consent collection on first login

## Module References

- [[authentication]] — user creation, password hashing, token issuance
- [[authorization]] — role assignment during invitation
- [[notification-system]] — invitation email delivery
- [[employee-profiles]] — employee profile stub creation
- [[job-hierarchy]] — auto-role assignment from job family level
