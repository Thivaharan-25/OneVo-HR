# Platform Users And Roles End-to-End Logic

## Invite Platform Manager

1. Super Admin opens Platform Users.
2. Super Admin enters name, ONEVO email, and role assignments.
3. Frontend calls `POST /admin/v1/platform-users/invite`.
4. Backend verifies `platform.accounts.manage`.
5. Backend creates `platform_user_invites` and sends an invite email.
6. Invitee opens the invite link and completes account setup with password creation, or optional Google OAuth setup if enabled by policy.
7. Backend verifies the invite token and email, then creates or activates `platform_users`.
8. Backend requires MFA setup/verification before a platform session can be issued.
9. Backend assigns one or more roles and records an audit event.

## Restrict Manager To Specific Modules

1. Super Admin opens Platform Roles.
2. Super Admin creates or edits a platform role.
3. Frontend loads `GET /admin/v1/platform-permissions/catalog`.
4. Super Admin selects allowed Developer Platform module permissions.
5. Frontend calls `PUT /admin/v1/platform-roles/{id}/permissions`.
6. Backend evaluates the recoverable-admin guard against the proposed permission set.
7. Backend rejects the request with `recoverable_admin_required` if the change would leave zero active users with both `platform.accounts.manage` and `platform.roles.manage`.
8. Backend replaces role permissions transactionally.
9. Backend revokes or marks affected sessions for re-issue when permission claims are stale.

## Session Revocation

1. Super Admin opens a platform user detail page.
2. Super Admin clicks revoke sessions.
3. Frontend calls `POST /admin/v1/platform-users/{id}/sessions/revoke`.
4. Backend evaluates the recoverable-admin guard when the target is a recoverable admin.
5. Backend invalidates `platform_user_sessions` for the user.
6. Active browser sessions must be forced to log in again.

## Recoverable Admin Guard

The guard is mandatory for every access-management mutation:

| Mutation | Guard Requirement |
|---|---|
| Replace role permissions | At least one active user must still effectively have `platform.accounts.manage` and `platform.roles.manage` after the replacement |
| Update user roles | At least one active user must still effectively have both recovery permissions after the assignment change |
| Deactivate user | The deactivated user cannot be the last recoverable admin |
| Deactivate/archive role | The role cannot be required by the last recoverable admin |
| Revoke sessions | Do not revoke the last recoverable admin's only active session unless another recoverable admin still has an active session |

Guard failure response:

```json
{
  "code": "recoverable_admin_required",
  "message": "At least one active platform user must retain platform user and role management permissions."
}
```

## APIs

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/platform-users` | List platform users | `platform.accounts.read` |
| POST | `/admin/v1/platform-users/invite` | Invite platform manager | `platform.accounts.manage` |
| POST | `/admin/v1/platform-users/{id}/invite/resend` | Resend pending invite | `platform.accounts.manage` |
| POST | `/admin/v1/platform-users/{id}/invite/revoke` | Revoke pending invite | `platform.accounts.manage` |
| GET | `/admin/v1/platform-users/{id}` | User detail | `platform.accounts.read` |
| PATCH | `/admin/v1/platform-users/{id}` | Update name/status/roles | `platform.accounts.manage` |
| POST | `/admin/v1/platform-users/{id}/deactivate` | Disable login | `platform.accounts.manage` |
| POST | `/admin/v1/platform-users/{id}/reactivate` | Re-enable user | `platform.accounts.manage` |
| GET | `/admin/v1/platform-users/{id}/sessions` | List active sessions | `platform.accounts.read` |
| POST | `/admin/v1/platform-users/{id}/sessions/revoke` | Revoke sessions | `platform.accounts.manage` |
| GET | `/admin/v1/platform-users/{id}/access-history` | Access history | `platform.accounts.read` |
| GET | `/admin/v1/platform-roles` | List platform roles | `platform.roles.read` |
| POST | `/admin/v1/platform-roles` | Create platform role | `platform.roles.manage` |
| GET | `/admin/v1/platform-roles/{id}` | Role detail | `platform.roles.read` |
| PATCH | `/admin/v1/platform-roles/{id}` | Update role metadata | `platform.roles.manage` |
| PUT | `/admin/v1/platform-roles/{id}/permissions` | Replace role permissions | `platform.roles.manage` |
| GET | `/admin/v1/platform-permissions/catalog` | Permission catalog | `platform.roles.read` |

## Audit Requirements

Audit every invite, invite resend, invite revoke, user activation/deactivation/reactivation, role assignment, permission change, guard failure, and session revocation with actor, target user or role, old value, new value, reason where provided, and timestamp.
