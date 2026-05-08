# Contract: Auth Session + Permissions

**Backend owner:** DEV1 Tasks 2-3  
**Consumers:** DEV5 Tasks 3+, DEV6, DEV7, DEV8 Task 1  
**Canonical source:** `ONEVO.Application/Features/Auth/` (authoritative once built)

---

## Customer Web Session Model

Customer-facing browser sessions use a BFF-style HttpOnly cookie model. The browser frontend never receives, stores, decodes, or forwards the tenant user JWT. JWT creation and validation stay inside the backend.

The backend sets:

- `onevo_session` - HttpOnly, Secure, SameSite cookie that represents the active web session.
- `onevo_csrf` - non-HttpOnly CSRF cookie/header pair for state-changing browser requests.

The backend may still create short-lived tenant JWTs internally, but they are not returned to the browser web app.

---

## POST `/api/v1/auth/login` - POST `/api/v1/auth/refresh`

```ts
interface AuthResponseDto {
  authenticated: boolean
  user: CurrentUserDto | null
  permissions: string[]
  active_modules: string[]
  must_change_password: boolean
  mfa_required: boolean       // true -> client must complete TOTP MFA before session is established
}
```

Successful login, MFA verification, and refresh responses set or rotate the HttpOnly session cookie. The response body contains only session state and authorization metadata needed by the UI.

## POST `/api/v1/auth/mfa/send`

Starts or resends an email OTP fallback challenge for an `mfa_pending` token when fallback is allowed by policy. Primary MFA uses TOTP from an authenticator app. Local development may log fallback OTPs; customer release requires Resend-backed delivery.

## POST `/api/v1/auth/mfa/verify` -> `AuthResponseDto` (same shape, `mfa_required: false`)

## POST `/api/v1/auth/password-reset/confirm` -> `204 No Content`

## Invitation Acceptance APIs

Invitation completion is part of the tenant-facing Auth API, not the Developer Platform Admin API. The admin/provisioning endpoint creates and emails the invite; these endpoints let the invited person inspect and complete it.

The invitation token is the authority for the pending account. The invited email is the delivery address and default account email. Completing the invite with password must use the invited email. Completing the invite with Google may use a different Google email only when tenant policy or the invitation explicitly allows it; mismatches are audit-logged and retained on the invitation/audit record. This policy does not require changing the user database entity by itself.

## GET `/api/v1/auth/invitations/{token}`

Returns safe invite preview data for the accept-invite page. It must not reveal sensitive tenant data beyond what the email recipient already received.

```ts
interface InvitationPreviewDto {
  invitation_id: string
  tenant_id: string
  tenant_name: string
  invited_email: string
  first_name: string
  last_name: string
  role_name: string
  expires_at: string
  status: "pending" | "expired" | "accepted" | "revoked"
  password_setup_enabled: boolean
  google_sign_in_enabled: boolean
  allow_google_email_mismatch: boolean
  allowed_email_domains: string[]
}
```

## POST `/api/v1/auth/invitations/{token}/accept-password` -> `AuthResponseDto`

```ts
interface AcceptInvitationWithPasswordDto {
  password: string
  phone?: string
}
```

This activates the invited account using the original `invited_email`, stores a BCrypt password hash, marks the invite used, and sets the HttpOnly session cookies. It does not let the user choose a different email address.

## POST `/api/v1/auth/invitations/{token}/accept-google` -> `AuthResponseDto`

```ts
interface AcceptInvitationWithGoogleDto {
  google_id_token: string
}
```

The backend validates the Google token and activates the account without a password using the existing Auth/SSO user model. If the Google email differs from `invited_email`, the backend allows it only when `allow_google_email_mismatch` is true and the Google email domain is permitted for the tenant/invitation. When allowed, the account's primary login email becomes the verified Google email and the original invited email is retained on the invitation/audit record. When not allowed, the API returns `409 Conflict`.

## GET `/api/v1/auth/me/permissions`

```ts
interface PermissionsDto {
  user_id: string             // uuid
  tenant_id: string           // uuid
  roles: string[]             // e.g. ["super_admin", "hr_manager"]
  permissions: string[]       // "resource:action" keys, e.g. ["employee:read", "leave:approve"]
  active_modules: string[]    // e.g. ["hr_management", "work_sync", "workforce_intelligence"]
}
```

## Notes

- Customer web frontend uses cookie-based session auth and calls APIs with `credentials: "include"`.
- Customer web frontend does not attach `Authorization: Bearer` for normal `/api/v1/*` calls.
- Tenant JWTs are backend-internal for browser sessions and are rejected by `/admin/v1/*`.
- IDE extension stores its own user tokens in `SecretStorage`, not `localStorage`; this is separate from browser web auth.
- `permissions` is the definitive source for `<PermissionGate>` and `useAuth().hasPermission()`

