# Platform Access

## Purpose

Platform Access manages the identities, roles, and session state for ONEVO's own engineering and operations team — the people who use the Developer Console. It handles platform account invites, platform role definitions, permission assignments, and session revocation.

**Platform accounts are completely separate from tenant users.** Platform roles and permissions have no relationship to ONEVO product permissions. A platform account with `platform.tenants.manage` cannot access any tenant-facing `/api/v1/*` endpoint — and a tenant JWT is rejected by every `/admin/v1/*` endpoint.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `dev_platform_accounts` | Read + write — platform identity records |
| `dev_platform_account_invites` | Read + write — pending invitations |
| `dev_platform_sessions` | Read + revoke — active login sessions |
| `dev_platform_roles` | Read + write — role definitions |
| `dev_platform_permissions` | Read — permission code catalog |
| `dev_platform_role_permissions` | Read + write — role permission mapping |
| `dev_platform_account_roles` | Read + write — account role assignments |
| Audit log | Write every access change |

## Capabilities

### Platform Accounts
- Invite new platform managers by `@onevo.io` email address — no other domains accepted
- View last login time and active session count per account
- Deactivate or reactivate an account — deactivation immediately revokes all active sessions
- Revoke individual sessions or all sessions for an account

### Platform Roles
- Create custom roles for specific work areas (e.g., "Billing Manager", "Security Auditor")
- Assign permission codes to roles
- Assign one or more roles to a platform account
- Built-in role presets are convenience groupings — authorization is always enforced by permission codes, not role names

### Built-In Role Presets

| Role | Intended Permissions |
|---|---|
| Platform Super Admin | All platform permissions including account management and impersonation |
| Tenant Operations Manager | Tenant lifecycle and provisioning; no security or platform access admin |
| Billing Manager | Subscription plans, gateways, invoices, commercial read/manage |
| Security Auditor | Security, audit, compliance, retention — read-only |
| Module Catalog Manager | Product module catalog and subscription plan configuration |
| Operations Engineer | Health, services, infrastructure, background jobs, agent versions |

## Permission Boundary

Platform permissions (e.g., `platform.tenants.manage`) control Developer Console screens and `/admin/v1/*` API actions only. They do not grant any access to tenant-facing `/api/v1/*` endpoints.

Tenant permissions (e.g., `employees:read`) control what tenant users can do in the main ONEVO app. They do not grant any access to the Developer Console.

## Navigation

| Route | Permission |
|---|---|
| `/platform/access` | `platform.accounts.read` |
| Write operations | `platform.accounts.manage` |
| Role permission edits | `platform.accounts.manage` |

## Key Rules

- Only `@onevo.io` email addresses can be invited as platform accounts
- Invite tokens are hashed before storage — raw token shown once to inviter via email, never stored
- Deactivating an account invalidates all its active sessions immediately
- All role and permission changes are audit-logged with previous and new state
- Session revocation of own session logs out the current operator immediately

## Related

- [[developer-platform/auth|Developer Platform Auth & Authorization]]
- [[developer-platform/modules/platform-access/end-to-end-logic|Platform Access End-to-End Logic]]
- [[developer-platform/modules/security-center/overview|Security Center]] — session revocation also accessible here
