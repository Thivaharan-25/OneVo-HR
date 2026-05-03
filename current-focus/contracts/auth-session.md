# Contract: Auth Session + Permissions

**Backend owner:** DEV1 Tasks 2-3  
**Consumers:** DEV5 Tasks 3+, DEV6, DEV7, DEV8 Task 1  
**Canonical source:** `ONEVO.Application/Features/Auth/` (authoritative once built)

---

## POST `/api/v1/auth/login` - POST `/api/v1/auth/refresh`

```ts
interface AuthResponseDto {
  access_token: string        // short-lived JWT
  refresh_token: string       // opaque, backend-managed, rotated on each use
  expires_in: number          // seconds
  token_type: "Bearer"
  must_change_password: boolean
  mfa_required: boolean       // true -> client must complete MFA before access_token is usable
}
```

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

- `access_token` is a tenant-issuer JWT; rejected by `/admin/v1/*`
- IDE extension stores tokens in `SecretStorage`, not `localStorage`
- `permissions` is the definitive source for `<PermissionGate>` and `useAuth().hasPermission()`

