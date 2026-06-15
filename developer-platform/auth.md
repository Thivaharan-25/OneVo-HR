# OneVo Developer Platform - Authentication & Authorization

## Overview

The Developer Platform uses a three-step platform auth model:

1. Email/password primary login verifies the platform account credentials.
2. Mandatory MFA verifies the second factor before any console access is granted.
3. Platform-admin JWT authorizes all `/admin/v1/*` API calls after MFA succeeds.

Google OAuth may be enabled for invited platform managers as an alternate account setup or sign-in method, but it does not replace MFA. A full Developer Platform session is never created until MFA succeeds.

---

## Email/Password + MFA Login Flow

1. Platform user opens `console.onevo.io`.
2. Login screen requests email and password.
3. Frontend calls `POST /admin/v1/auth/login`.
4. Backend validates the account, password hash, active status, and lockout state.
5. Backend creates a pending MFA challenge and records the primary login event.
6. Frontend prompts for MFA.
7. Frontend calls `POST /admin/v1/auth/mfa/verify`.
8. Backend verifies the MFA factor.
9. If MFA succeeds, backend creates the platform session and issues the platform-admin JWT.
10. If MFA fails, no platform-admin session is created.

Required audit/security events:

- `platform_auth.login_success`
- `platform_auth.login_failed`
- `platform_auth.mfa_challenge_created`
- `platform_auth.mfa_success`
- `platform_auth.mfa_failed`
- `platform_auth.session_created`
- `platform_auth.session_revoked`
- `platform_auth.password_reset_requested`
- `platform_auth.password_reset_completed`

---

## Optional Google OAuth Setup

Invited platform managers may complete account setup with Google OAuth if the account policy enables it. OAuth identity verification must resolve to a pending or active platform account, and MFA remains mandatory before issuing a platform-admin JWT.

Google OAuth is not the primary production auth rule for the Developer Platform. Email/password plus MFA is the canonical Super Admin journey.

---

## Platform-Admin JWT

### Token Structure

```json
{
  "iss": "onevo-platform-admin",
  "aud": "onevo-admin-api",
  "sub": "<dev_platform_account_id>",
  "email": "admin@onevo.io",
  "permission_version": 17,
  "impersonation": false,
  "iat": 1714000000,
  "exp": 1714001800
}
```

### Token Properties

| Property | Value |
|:---|:---|
| Issuer (`iss`) | `onevo-platform-admin` |
| Audience (`aud`) | `onevo-admin-api` |
| Subject (`sub`) | `dev_platform_account_id` |
| TTL | 30 minutes |
| Signing key | Separate secret from tenant JWT signing key |
| Storage | HttpOnly cookie |
| Renewal | Re-issue after successful auth/MFA or approved session renewal |

Tenant JWTs presented to `/admin/v1/*` are rejected. Platform-admin JWTs presented to tenant-facing `/api/v1/*` endpoints are rejected. The issuer boundary is enforced by backend authorization middleware.

---

## Platform Permissions

Developer Platform authorization is permission-based. Built-in roles are seeded presets, not authorization rules. Custom roles are unlimited, and a platform account may have multiple active roles.

Effective access is the union of permissions resolved from:

- `dev_platform_account_roles`
- `dev_platform_roles`
- `dev_platform_role_permissions`
- `dev_platform_permissions`

Backend and frontend code must check permission codes, never role names. Frontend route filtering is not the security boundary.

The canonical access and rendering contract is `developer-platform/access-control-contract.md`.

### Seed Roles

| Seed Role | Initial Permission Scope |
|:---|:---|
| Platform Super Admin | All platform permissions |
| Tenant Operations Manager | Tenant lifecycle, demo/trial operations, tenant role materialization, and tenant read/manage actions |
| Billing Manager | Subscription plans, invoices, payment gateways, add-ons, billing reports, and commercial read/manage actions |
| Support Manager | Customer support tickets, support assignment, replies, internal notes, and knowledgebase promotion |
| Security Auditor | Security, audit, compliance, and retention read-only permissions |
| Module Catalog Manager | Product module catalog, integration catalog, role templates, and configuration templates |
| Operations Engineer | Platform health, services, feature flags, and system configuration review |
| Read-Only Viewer | Dashboard and broad read-only visibility without mutation permissions |

### High-Risk Permissions

| Permission | Meaning |
|:---|:---|
| `platform.accounts.manage` | Invite/deactivate platform accounts and revoke sessions |
| `platform.roles.manage` | Change platform role permission sets |
| `platform.tenants.manage` | Create/edit tenants and direct trial actions |
| `platform.tenants.suspend` | Suspend or unsuspend tenants |
| `platform.requests.manage` | Approve/reject activation and trial-extension requests |
| `platform.subscriptions.manage` | Change plans, add-ons, prices, billing rules, or resource allocations |
| `platform.demo_profiles.manage` | Change demo access, demo limits, and upgrade options |
| `platform.tenants.impersonate` | Issue short-lived impersonation token |

### Recoverable Admin Guard

The backend must reject any account, role, permission, or session change that would leave zero active recoverable admins.

A recoverable admin is an active platform account whose effective permissions include both:

- `platform.accounts.manage`
- `platform.roles.manage`

Failed requests return `recoverable_admin_required`.

---

## Impersonation Model

Impersonation allows an explicitly authorized platform account to inspect a tenant-user perspective for support/debugging. It is strictly controlled and requires `platform.tenants.impersonate`.

Impersonation rules:

- Always audit-log before token issuance.
- Token TTL is 15 minutes.
- Token is non-renewable.
- Token carries `impersonation: true`.
- Token cannot call normal mutation endpoints unless an endpoint explicitly allows impersonation.
- Impersonation does not create a normal tenant JWT.

---

## Security Summary

| Concern | Approach |
|:---|:---|
| Authentication | Email/password primary login plus mandatory MFA |
| Optional identity setup | Google OAuth may be enabled for invited managers, followed by MFA |
| Authorization | Platform-admin JWT, separate issuer (`onevo-platform-admin`) |
| Tenant endpoint isolation | Admin JWT issuer is rejected at all tenant endpoints |
| Permission enforcement | Effective platform permissions checked at backend policy/endpoint level |
| Impersonation | Separate short-lived JWT, non-renewable, always audit-logged |
| Network | IP allowlist or VPN where required |
| Session storage | HttpOnly cookies |
| Token signing | Separate signing key from tenant JWT infrastructure |
