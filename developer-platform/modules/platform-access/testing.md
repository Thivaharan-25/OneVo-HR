# Platform Access — Testing

## Test Fixtures Required

- Super Admin platform account (all permissions)
- Platform account with `platform.accounts.manage` only
- Platform account with `platform.accounts.read` only
- Platform account that is deactivated (`is_active = false`)
- At least 1 pending unexpired invite in `dev_platform_account_invites`

---

## Authentication and Access

### TC-PA-001: Tenant JWT is rejected by every Platform Access endpoint
**Action:** `GET /admin/v1/platform-accounts` with `iss: "onevo-tenant"` token
**Expected:** HTTP 401

### TC-PA-002: Deactivated account cannot log in
**Setup:** Platform account with `is_active = false`
**Action:** `POST /admin/v1/auth/google-callback` with valid Google id_token for deactivated account
**Expected:** HTTP 401 — `is_active` check fails at step 4 of login flow

### TC-PA-003: Expired invite cannot create a session
**Setup:** Invite with `expires_at` in the past
**Action:** Attempt to accept the expired invite link
**Expected:** HTTP 401 or HTTP 422, `code: "invite_expired"` — no session created

---

## Invite

### TC-PA-004: Invite validates @onevo.io email domain
**Action:** `POST /admin/v1/platform-accounts/invite` with `email: "user@gmail.com"`
**Expected:** HTTP 422 — only `@onevo.io` email addresses allowed for platform accounts

### TC-PA-005: Valid invite creates invite record and sends email
**Action:** `POST /admin/v1/platform-accounts/invite` `{"email": "newengineer@onevo.io", "full_name": "New Engineer"}`
**Expected:**
- HTTP 201
- `dev_platform_account_invites` row created: `email`, `expires_at = now + 72 hours`, `invited_by_id`
- `invite_token_hash` stored (raw token hashed — never stored plaintext)
- Email sent to `newengineer@onevo.io` via Resend

### TC-PA-006: Invite requires platform.accounts.manage
**Setup:** Account with `platform.accounts.read` only
**Action:** `POST /admin/v1/platform-accounts/invite`
**Expected:** HTTP 403

---

## Deactivate and Reactivate

### TC-PA-007: Deactivating an account invalidates their sessions
**Setup:** Target account has 2 active sessions
**Action:** `POST /admin/v1/platform-accounts/{id}/deactivate`
**Expected:**
- `dev_platform_accounts.is_active = false`
- Both sessions revoked (`dev_platform_sessions.revoked_at` set)
- Target account's next API call returns 401
- Audit log: `action = 'platform_account.deactivated'`

### TC-PA-008: Reactivate restores login capability
**Setup:** Account with `is_active = false`
**Action:** `POST /admin/v1/platform-accounts/{id}/reactivate`
**Expected:** `is_active = true`. Account can now log in via Google OAuth.

### TC-PA-009: Accounts.manage required to deactivate
**Setup:** Account with `platform.accounts.read` only
**Action:** `POST /admin/v1/platform-accounts/{id}/deactivate`
**Expected:** HTTP 403

---

## Role and Permission Management

### TC-PA-010: Role permission change affects API authorization on next request
**Setup:** Custom role "Junior Ops" has only `platform.dashboard.view`. Account assigned this role.
**Action 1:** Account calls `GET /admin/v1/feature-flags` → HTTP 403 (no feature_flags.read)
**Action 2:** `PUT /admin/v1/platform-roles/{roleId}/permissions` adding `platform.feature_flags.read`
**Action 3:** Same account calls `GET /admin/v1/feature-flags`
**Expected:** HTTP 200 — permission takes effect on next request without re-login

### TC-PA-011: Every access management change writes audit log
**Action:** `PATCH /admin/v1/platform-accounts/{id}` changing role assignment
**Expected:** `audit_log` entry: actor, target account, `action = 'platform_account.role_updated'`, previous role, new role

### TC-PA-012: Session revoke invalidates that specific session only
**Setup:** Account has 3 active sessions
**Action:** `POST /admin/v1/platform-accounts/{id}/sessions/revoke` targeting 1 session ID
**Expected:** Targeted session revoked. Other 2 sessions remain active.

---

## Permission Enforcement on Routes

### TC-PA-013: Account without manage permission sees read-only state
**Setup:** Account with `platform.accounts.read` only
**Action:** `GET /admin/v1/platform-accounts`
**Expected:** HTTP 200 — list returned. Edit/deactivate actions not present in response.

### TC-PA-014: Account without any permission cannot read platform accounts
**Setup:** Account with no permissions at all
**Action:** `GET /admin/v1/platform-accounts`
**Expected:** HTTP 403
