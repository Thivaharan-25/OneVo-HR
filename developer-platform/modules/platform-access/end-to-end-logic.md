# Platform Access End-to-End Logic

## Invite Platform Manager

1. Super Admin opens Platform Management -> Platform Users & Roles.
2. Super Admin enters name, ONEVO email, and role assignment.
3. Frontend calls `POST /admin/v1/platform-accounts/invite`.
4. Backend verifies `platform.accounts.manage`.
5. Backend creates `dev_platform_account_invites` and sends an invite email.
6. Invitee signs in with Google OAuth.
7. Backend verifies email/sub against the invite and creates or activates `dev_platform_accounts`.
8. Backend assigns roles and records an audit event.

## Restrict Manager To Specific Modules

1. Super Admin creates or edits a platform role.
2. Frontend loads `GET /admin/v1/platform-permissions/catalog`.
3. Super Admin selects allowed Developer Platform module permissions.
4. Frontend calls `PUT /admin/v1/platform-roles/{id}/permissions`.
5. Backend replaces role permissions transactionally.
6. Backend revokes or marks affected sessions for re-issue when permission claims are stale.

## Session Revocation

1. Super Admin opens a platform account detail page.
2. Super Admin clicks revoke sessions.
3. Frontend calls `POST /admin/v1/platform-accounts/{id}/sessions/revoke`.
4. Backend invalidates `dev_platform_sessions` for the account.
5. Active browser sessions must be forced to log in again.

## APIs

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/platform-accounts` | List platform accounts | `platform.accounts.read` |
| POST | `/admin/v1/platform-accounts/invite` | Invite platform manager | `platform.accounts.manage` |
| GET | `/admin/v1/platform-accounts/{id}` | Account detail | `platform.accounts.read` |
| PATCH | `/admin/v1/platform-accounts/{id}` | Update name/status/roles | `platform.accounts.manage` |
| POST | `/admin/v1/platform-accounts/{id}/deactivate` | Disable login | `platform.accounts.manage` |
| POST | `/admin/v1/platform-accounts/{id}/reactivate` | Re-enable account | `platform.accounts.manage` |
| POST | `/admin/v1/platform-accounts/{id}/sessions/revoke` | Revoke sessions | `platform.accounts.manage` |
| GET | `/admin/v1/platform-roles` | List platform roles | `platform.roles.read` |
| POST | `/admin/v1/platform-roles` | Create platform role | `platform.roles.manage` |
| GET | `/admin/v1/platform-roles/{id}` | Role detail | `platform.roles.read` |
| PATCH | `/admin/v1/platform-roles/{id}` | Update role metadata | `platform.roles.manage` |
| PUT | `/admin/v1/platform-roles/{id}/permissions` | Replace role permissions | `platform.roles.manage` |
| GET | `/admin/v1/platform-permissions/catalog` | Permission catalog | `platform.roles.read` |

## Audit Requirements

Audit every invite, account activation/deactivation, role assignment, permission change, and session revocation with actor, target account, old value, new value, reason where provided, and timestamp.
