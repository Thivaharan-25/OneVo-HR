# Platform Users And Roles Userflow

## Actors

- Platform Super Admin
- Restricted platform manager

## Invite Manager

1. Super Admin opens Platform Users.
2. Super Admin clicks Invite Platform Manager.
3. Super Admin enters ONEVO email, name, and role assignment.
4. Console calls `POST /admin/v1/platform-users/invite`.
5. Invitee accepts the invite and completes password setup, or optional Google OAuth setup if enabled by policy.
6. Invitee completes MFA before any platform-admin session is created.
7. Backend verifies invite, creates/activates user, assigns roles, and records audit.

## Restrict Manager Access

1. Super Admin opens Platform Roles.
2. Console loads `GET /admin/v1/platform-permissions/catalog`.
3. Super Admin creates a role with only the required module permissions.
4. Console calls `PUT /admin/v1/platform-roles/{id}/permissions`.
5. Manager logs in and sees only allowed sidebar items.
6. Direct URL access to forbidden routes returns access denied.

## Revoke Access

1. Super Admin opens platform user detail.
2. Super Admin deactivates user or revokes sessions.
3. Backend invalidates sessions and audits the action.

## APIs Used

- `GET /admin/v1/platform-users`
- `POST /admin/v1/platform-users/invite`
- `POST /admin/v1/platform-users/{id}/invite/resend`
- `POST /admin/v1/platform-users/{id}/invite/revoke`
- `GET /admin/v1/platform-users/{id}`
- `PATCH /admin/v1/platform-users/{id}`
- `POST /admin/v1/platform-users/{id}/deactivate`
- `POST /admin/v1/platform-users/{id}/reactivate`
- `GET /admin/v1/platform-users/{id}/sessions`
- `POST /admin/v1/platform-users/{id}/sessions/revoke`
- `GET /admin/v1/platform-users/{id}/access-history`
- `GET /admin/v1/platform-roles`
- `POST /admin/v1/platform-roles`
- `PATCH /admin/v1/platform-roles/{id}`
- `PUT /admin/v1/platform-roles/{id}/permissions`
- `GET /admin/v1/platform-permissions/catalog`

## Security Rules

Platform users are not tenant users. Platform roles do not create tenant permissions.
