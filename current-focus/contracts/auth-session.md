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

