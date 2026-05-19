# Platform Access Userflow

## Actors

- Platform Super Admin
- Restricted platform manager

## Invite Manager

1. Super Admin opens Platform Management -> Platform Users & Roles.
2. Super Admin clicks Invite Platform Manager.
3. Super Admin enters ONEVO email, name, and role assignment.
4. Console calls `POST /admin/v1/platform-accounts/invite`.
5. Invitee signs in with Google OAuth.
6. Backend verifies invite, creates/activates account, assigns roles, and records audit.

## Restrict Manager Access

1. Super Admin opens Platform Roles.
2. Console loads `GET /admin/v1/platform-permissions/catalog`.
3. Super Admin creates a role with only the required module permissions.
4. Console calls `PUT /admin/v1/platform-roles/{id}/permissions`.
5. Manager logs in and sees only allowed sidebar items.
6. Direct URL access to forbidden routes returns access denied.

## Revoke Access

1. Super Admin opens account detail.
2. Super Admin deactivates account or revokes sessions.
3. Backend invalidates sessions and audits the action.

## APIs Used

- `GET /admin/v1/platform-accounts`
- `POST /admin/v1/platform-accounts/invite`
- `GET /admin/v1/platform-accounts/{id}`
- `PATCH /admin/v1/platform-accounts/{id}`
- `POST /admin/v1/platform-accounts/{id}/deactivate`
- `POST /admin/v1/platform-accounts/{id}/reactivate`
- `POST /admin/v1/platform-accounts/{id}/sessions/revoke`
- `GET /admin/v1/platform-roles`
- `POST /admin/v1/platform-roles`
- `PATCH /admin/v1/platform-roles/{id}`
- `PUT /admin/v1/platform-roles/{id}/permissions`
- `GET /admin/v1/platform-permissions/catalog`

## Security Rules

Platform accounts are not tenant users. Platform roles do not create tenant permissions.
