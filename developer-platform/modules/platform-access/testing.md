# Platform Users And Roles - Testing

## Test Fixtures Required

- Platform Super Admin user with all permissions
- Platform user with `platform.accounts.manage` only
- Platform user with `platform.accounts.read` only
- Platform user with `status = inactive`
- At least one pending unexpired invite in `platform_user_invites`

---

## Authentication And Access

### TC-PA-001: Tenant JWT is rejected by every Platform Users endpoint

**Action:** `GET /admin/v1/platform-users` with `iss: "onevo-tenant"` token.

**Expected:** HTTP 401

### TC-PA-002: Inactive user cannot log in

**Setup:** Platform user with `status = inactive`.

**Action:** `POST /admin/v1/auth/login` with valid credentials.

**Expected:** HTTP 401 before MFA challenge creation.

### TC-PA-003: Expired invite cannot create a session

**Setup:** Invite with `expires_at` in the past.

**Action:** Accept expired invite link.

**Expected:** HTTP 401 or HTTP 422, `code: "invite_expired"`; no session created.

---

## Invites

### TC-PA-004: Invite validates ONEVO email domain

**Action:** `POST /admin/v1/platform-users/invite` with `email: "user@gmail.com"`.

**Expected:** HTTP 422.

### TC-PA-005: Valid invite creates invite record and sends email

**Action:** `POST /admin/v1/platform-users/invite`

**Expected:**

- HTTP 201
- `platform_user_invites` row created
- Raw invite token is never stored
- Audit event `platform_account.invited` written

### TC-PA-006: Resend invite writes audit event

**Action:** `POST /admin/v1/platform-users/{id}/invite/resend`

**Expected:** Audit event `platform_account.invite_resent` written.

### TC-PA-007: Revoke invite blocks later acceptance

**Action:** `POST /admin/v1/platform-users/{id}/invite/revoke`

**Expected:** Invite cannot be accepted; audit event `platform_account.invite_revoked` written.

---

## Deactivate, Reactivate, Sessions

### TC-PA-008: Deactivating user invalidates sessions

**Setup:** Target user has 2 active sessions.

**Action:** `POST /admin/v1/platform-users/{id}/deactivate`

**Expected:**

- `platform_users.status = inactive`
- Active `platform_user_sessions` are revoked
- Audit event `platform_account.deactivated` written

### TC-PA-009: Reactivate restores login capability

**Action:** `POST /admin/v1/platform-users/{id}/reactivate`

**Expected:** `platform_users.status = active`; audit event `platform_account.reactivated` written.

### TC-PA-010: Session revoke invalidates selected sessions

**Action:** `POST /admin/v1/platform-users/{id}/sessions/revoke`

**Expected:** Target sessions revoked; audit event `platform_account.sessions_revoked` written.

---

## Roles And Permissions

### TC-PA-011: Role permission change affects API authorization

**Setup:** Custom role has only dashboard/read permission.

**Action:** Add `platform.tenants.feature_overrides.read` through `PUT /admin/v1/platform-roles/{roleId}/permissions`.

**Expected:** Assigned users can access feature flags on next authorization check.

### TC-PA-012: Role assignment change is audited

**Action:** `PATCH /admin/v1/platform-users/{id}` changing role assignment.

**Expected:** Audit event `platform_account.roles_changed` written with previous and new role sets.

### TC-PA-013: Recoverable Super Admin cannot be removed

**Action:** Deactivate or strip roles from the last recoverable Super Admin.

**Expected:** HTTP 422, `code: "recoverable_admin_required"`.

---

## Permission Enforcement

### TC-PA-014: User without manage permission sees read-only state

**Setup:** User has `platform.accounts.read` only.

**Action:** `GET /admin/v1/platform-users`

**Expected:** HTTP 200; mutation actions are absent or disabled by response/action model.

### TC-PA-015: User without read permission cannot read platform users

**Setup:** User has no platform account permissions.

**Action:** `GET /admin/v1/platform-users`

**Expected:** HTTP 403.
