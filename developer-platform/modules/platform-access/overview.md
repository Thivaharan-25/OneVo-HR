# Platform Users And Platform Roles

## Purpose


Platform users are completely separate from tenant users. Platform roles and permissions have no relationship to ONEVO product permissions. A platform user with `platform.tenants.manage` cannot access any tenant-facing `/api/v1/*` endpoint, and a tenant JWT is rejected by every `/admin/v1/*` endpoint.

The canonical access and UI rendering contract is `developer-platform/access-control-contract.md`.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `platform_users` | Read + write: platform identity records |
| `platform_user_invites` | Read + write: pending invitations |
| `platform_user_sessions` | Read + revoke: active login sessions |
| `platform_roles` | Read + write: role definitions |
| `platform_permissions` | Read: permission code catalog |
| `platform_role_permissions` | Read + write: role permission mapping |
| `platform_user_roles` | Read + write: user role assignments |
| `platform_auth_events` | Read + write: login, MFA, password reset, session revoke, and role-change history |
| Audit log | Write every access change |

## Capabilities

### Platform Users

- Invite new platform managers by `@onevo.io` email address; no other domains accepted.
- View last login time, MFA status, invite status, access history, and active sessions.
- Deactivate or reactivate a user; deactivation immediately revokes all active sessions.
- Revoke individual sessions or all sessions for a user.
- Assign one or more active roles to a platform user.

### Platform Roles

- Seed default system roles at startup.
- Edit seeded system role permissions, subject to the recoverable-admin guard.
- Create unlimited custom roles for specific work areas.
- Assign permission codes to roles.
- Archive custom roles when lifecycle rules allow it.
- Merge effective permissions across all active roles assigned to a user.
- Enforce authorization by permission codes, not role names.

### Built-In Role Presets

| Role | Initial Permission Scope |
|---|---|
| Platform Super Admin | All platform permissions including account management and impersonation |
| Tenant Operations Manager | Tenant lifecycle and provisioning; no security or platform access admin |
| Billing Manager | Subscription plans, add-ons, invoices, commercial read/manage |
| Security Auditor | Security, audit, compliance, retention: read-only |
| Module Catalog Manager | Product module catalog, integration catalog, role templates, configuration templates |
| Operations Engineer | Health, services, feature flags, and system configuration review |
| Read-Only Viewer | Dashboard and broad read-only visibility without mutation permissions |

Seeded system roles are editable but cannot be deleted. Custom roles are unlimited.

## Permission Boundary

Platform permissions such as `platform.tenants.manage` control Developer Console screens and `/admin/v1/*` API actions only. They do not grant access to tenant-facing `/api/v1/*` endpoints.

Tenant permissions such as `employees:read` control what tenant users can do in the main ONEVO app. They do not grant access to the Developer Console.

## Navigation

| Route | Permission |
|---|---|
| `/platform/platform-users` | `platform.accounts.read` |
| `/platform/platform-roles` | `platform.roles.read` |
| Account write operations | `platform.accounts.manage` |
| Role write operations | `platform.roles.manage` |

## Recoverable Admin Guard

The backend must reject any role, role-permission, user-role, user-status, or session-revocation change that would time_off zero active recoverable admins.

A recoverable admin is an active platform user whose effective permissions include both:

- `platform.accounts.manage`
- `platform.roles.manage`

The guard must evaluate effective permissions after the proposed change. This prevents accidental lockout after editing seeded roles or removing roles from users.

## UI Rendering Rules

- Missing sidebar route permission: hide the nav item.
- Direct URL without route permission: show the Angular 403 page.
- Read permission without manage permission: render the page read-only.
- Missing action permission: hide the action.
- Disabled controls are only for invalid state, not missing permission.

## Key Rules

- Only `@onevo.io` email addresses can be invited as platform users.
- Invite tokens are hashed before storage; raw tokens are never stored.
- Deactivating a user invalidates all active sessions immediately.
- All role and permission changes are audit-logged with previous and new state.
- Session revocation of own session logs out the current operator immediately.
- The recoverable-admin guard must run before access-management changes are committed.

## Related

- [[developer-platform/auth|Developer Platform Auth & Authorization]]
- [[developer-platform/access-control-contract|Developer Platform Access Control Contract]]
- [[developer-platform/modules/platform-access/end-to-end-logic|Platform Users And Roles End-to-End Logic]]
- [[developer-platform/modules/security-center/overview|Security Center]]: session revocation is also accessible here.
