# API Keys Userflow

> Phase 2 only. Do not expose in Phase 1 navigation.

## Actor

Platform Super Admin.

## Journey

1. Super Admin opens Settings -> API Keys.
2. Console lists active/revoked keys.
3. Super Admin creates key with scopes and expiry.
4. Backend returns raw key once and stores only hash.
5. Super Admin revokes key when no longer needed.

## APIs Used

- `GET /admin/v1/api-keys`
- `POST /admin/v1/api-keys`
- `DELETE /admin/v1/api-keys/{id}`
