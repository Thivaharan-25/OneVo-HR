# Platform Access End-to-End Logic

## Invite Platform Manager

1. Super Admin opens Platform Management -> Platform Users.
2. Super Admin enters name, ONEVO email, and role assignments.
3. Frontend calls `POST /admin/v1/platform-accounts/invite`.
4. Backend verifies `platform.accounts.manage`.
5. Backend creates `dev_platform_account_invites` and sends an invite email.
6. Invitee signs in with Google OAuth.
7. Backend verifies email/sub against the invite and creates or activates `dev_platform_accounts`.
8. Backend assigns one or more roles and records an audit event.

## Restrict Manager To Specific Modules

1. Super Admin opens Platform Management -> Platform Roles.
2. Super Admin creates or edits a platform role.
3. Frontend loads `GET /admin/v1/platform-permissions/catalog`.
4. Super Admin selects allowed Developer Platform module permissions.
5. Frontend calls `PUT /admin/v1/platform-roles/{id}/permissions`.
6. Backend evaluates the recoverable-admin guard against the proposed permission set.
7. Backend rejects the request with `recoverable_admin_required` if the change would leave zero active accounts with both `platform.accounts.manage` and `platform.roles.manage`.
8. Backend replaces role permissions transactionally.
9. Backend revokes or marks affected sessions for re-issue when permission claims are stale.

## Session Revocation

1. Super Admin opens a platform account detail page.
2. Super Admin clicks revoke sessions.
3. Frontend calls `POST /admin/v1/platform-accounts/{id}/sessions/revoke`.
4. Backend evaluates the recoverable-admin guard when the target is a recoverable admin.
5. Backend invalidates `dev_platform_sessions` for the account.
6. Active browser sessions must be forced to log in again.

## Recoverable Admin Guard

The guard is mandatory for every access-management mutation:

| Mutation | Guard Requirement |
|---|---|
| Replace role permissions | At least one active account must still effectively have `platform.accounts.manage` and `platform.roles.manage` after the replacement |
| Update account roles | At least one active account must still effectively have both recovery permissions after the assignment change |
| Deactivate account | The deactivated account cannot be the last recoverable admin |
| Deactivate/archive role | The role cannot be required by the last recoverable admin |
| Revoke sessions | Do not revoke the last recoverable admin's only active session unless another recoverable admin still has an active session |

Guard failure response:

```json
{
  "code": "recoverable_admin_required",
  "message": "At least one active platform account must retain platform account and role management permissions."
}
```

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

Audit every invite, account activation/deactivation, role assignment, permission change, guard failure, and session revocation with actor, target account or role, old value, new value, reason where provided, and timestamp.
