# OneVo Developer Platform — Authentication & Authorization

## Overview

The developer platform uses a **two-layer auth model**:

1. **Google OAuth** — identity verification at login (who you are)
2. **Platform-Admin JWT** — session authorization for all API calls (what you're allowed to do)

There are no passwords. All accounts must authenticate via Google using an approved `@onevo.io` email address.

---

## Google OAuth Login Flow

```
Developer                Dev Console              Google OAuth            OneVo Backend
    │                        │                         │                       │
    │── Open console ────────►│                         │                       │
    │                        │── Redirect to Google ──►│                       │
    │◄── Google login page ──│                         │                       │
    │── Sign in w/ Google ──►│                         │                       │
    │                        │◄── OAuth callback ──────│                       │
    │                        │    (code + id_token)    │                       │
    │                        │── POST /admin/v1/auth/google-callback ─────────►│
    │                        │   { google_id_token }                           │
    │                        │                                                 │
    │                        │         Verify id_token with Google             │
    │                        │         Check email domain = @onevo.io          │
    │                        │         Look up dev_platform_accounts           │
    │                        │         Check is_active = true                  │
    │                        │                                                 │
    │                        │◄── Platform-Admin JWT ──────────────────────────│
    │                        │    + role claim                                 │
    │◄── Session established─│                                                 │
```

**Backend validation steps (at `/admin/v1/auth/google-callback`):**

1. Verify the Google `id_token` signature against Google's public keys
2. Check `email` ends with `@onevo.io`
3. Look up the `dev_platform_accounts` record by `google_sub`
4. Verify `is_active = true`
5. Issue a platform-admin JWT with the account's role
6. Record `last_login_at`

If any step fails, return `401 Unauthorized`. No partial sessions.

---

## Platform-Admin JWT

### Token Structure

```json
{
  "iss": "onevo-platform-admin",
  "aud": "onevo-admin-api",
  "sub": "<dev_platform_account_id>",
  "email": "engineer@onevo.io",
  "platform_role": "admin",
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
| Subject (`sub`) | `dev_platform_account_id` (UUID, from `dev_platform_accounts` table) |
| TTL | 30 minutes |
| Signing key | Separate secret from tenant JWT signing key |
| Storage | httpOnly cookie (server-side session via NextAuth) |
| Renewal | Standard re-issue on login; no refresh tokens |

### What Happens at Tenant Endpoints

If a platform-admin JWT is presented at a tenant endpoint (e.g., `GET /api/v1/employees`):

1. The tenant endpoint's auth middleware checks `iss`
2. `iss = "onevo-platform-admin"` does **not** match expected `iss = "onevo-tenant"`
3. Request is rejected with `401 Unauthorized`
4. No data is returned

The inverse also applies: a tenant JWT presented at `/admin/v1/*` is rejected by the `PlatformAdmin` policy. The issuers are mutually exclusive by design. This is enforced in code, not just by convention.

---

## Platform Permissions

Developer Platform authorization is permission-based. Built-in roles are seeded presets, not authorization rules. Custom roles are unlimited, and a platform account may have multiple active roles.

| Seed Role | Initial Permission Scope |
|:---|:---|
| Platform Super Admin | All platform permissions, including platform account management and impersonation |
| Tenant Operations Manager | Tenant read/create/manage/activate, provisioning, role-template apply; no impersonation unless explicitly granted |
| Billing Manager | Subscription plans, payment gateways, invoices, commercial read/manage |
| Security Auditor | Security, audit, compliance, and retention read-only |
| Module Catalog Manager | Product module catalog, integration catalog, role-template, and configuration-template read/manage |
| Operations Engineer | Platform health, services, devices, infrastructure, jobs, agent versions |
| Read-Only Viewer | Dashboard and broad read-only visibility without mutation permissions |

Effective access is the union of permissions resolved from `dev_platform_account_roles`, `dev_platform_roles`, `dev_platform_role_permissions`, and `dev_platform_permissions`.

The platform-admin JWT includes account identity and either effective permission claims or a permission version reference. Authorization checks at the controller or policy level enforce permission boundaries. Frontend route filtering is not the security boundary. Backend and frontend code must check permission codes, never role names.

The canonical access and rendering contract is `developer-platform/access-control-contract.md`.

High-risk permissions include:

| Permission | Meaning |
|:---|:---|
| `platform.tenants.impersonate` | Issue short-lived impersonation token |
| `platform.accounts.manage` | Invite/deactivate platform accounts and revoke sessions |
| `platform.roles.manage` | Change platform role permission sets |
| `platform.tenants.suspend` | Suspend or unsuspend tenants |
| `platform.tenants.activate` | Activate provisioning tenants |
| `platform.agent_versions.force_update` | Push force-update commands to agent rings |

### Recoverable Admin Guard

The backend must reject any account, role, or permission change that would leave zero active recoverable admins. A recoverable admin is an active platform account whose effective permissions include both `platform.accounts.manage` and `platform.roles.manage`.

This guard applies to role permission replacement, account role assignment changes, account deactivation, role deactivation, and session/account changes that would remove the last recoverable admin's ability to fix access. Failed requests return `recoverable_admin_required`.

---

## Impersonation Model

Impersonation allows an explicitly authorized platform account to take a tenant-user's perspective for debugging. It is strictly controlled and requires `platform.tenants.impersonate`.

### How It Works

```
Authorized operator requests impersonation of user X in tenant Y
        │
        ▼
POST /admin/v1/tenants/{tenantId}/impersonate
{ "target_user_id": "..." }
        │
        ▼
Backend checks:
  - Caller has `platform.tenants.impersonate`
  - Target tenant and user exist and are active
  - Audit log entry written (cannot be skipped)
        │
        ▼
Returns: Impersonation JWT (separate, short-lived)
```

### Impersonation JWT Structure

```json
{
  "iss": "onevo-platform-admin",
  "aud": "onevo-admin-api",
  "sub": "<dev_platform_account_id>",
  "impersonation": true,
  "impersonated_tenant_id": "<tenant_id>",
  "impersonated_user_id": "<user_id>",
  "initiated_by": "<dev_platform_account_id>",
  "iat": 1714000000,
  "exp": 1714000900
}
```

### Impersonation Token Properties

| Property | Value |
|:---|:---|
| TTL | **15 minutes** — hard-coded, no exceptions |
| Renewable | **No** — must re-request after expiry; requires re-audit |
| `impersonation` claim | `true` — distinguishes this token from a regular admin token |
| Audit log | Always written before token is issued — cannot be bypassed |
| Who can issue | Accounts with `platform.tenants.impersonate` only — checked before issuance |
| Scope | Grants read access to that tenant's data through the admin API; does NOT grant a full tenant session |

**Scope Enforcement:**
The `impersonation: true` claim is checked by the `[Authorize(Policy = "PlatformAdmin")]` middleware. A separate `ImpersonationOnly` policy is applied to the impersonated session endpoints — any endpoint not tagged with this policy will reject tokens carrying `impersonation: true`. This prevents an impersonation token from being used to call non-impersonation admin endpoints (e.g., feature flag mutations). The policy ensures both that the issuer matches and that the endpoint scope matches the token's intended use.

### What Impersonation Is Not

Impersonation in the dev console is **not** a tenant login. It does not produce a tenant JWT. It does not allow the admin to act as the tenant user in the main product (`app.onevo.io`). It provides a privileged read-only view of that tenant user's data through the admin API, with every access recorded.

---

## Security Summary

| Concern | Approach |
|:---|:---|
| Authentication | Google OAuth only — no passwords |
| Identity verification | Google `id_token` verified server-side; email domain enforced |
| Authorization | Platform-admin JWT, separate issuer (`onevo-platform-admin`) |
| Tenant endpoint isolation | Admin JWT issuer is rejected at all tenant endpoints |
| Role enforcement | `platform_role` claim checked at policy and endpoint level |
| Impersonation | Separate short-lived JWT (15 min), non-renewable, always audit-logged |
| Network | IP allowlist or VPN required — enforced at infrastructure layer |
| Session storage | httpOnly cookies — not accessible to JavaScript |
| Token signing | Separate signing key from tenant JWT infrastructure |

---

## Development Mode Exception

> **Applies to Development environment only — enforced via `IWebHostEnvironment.IsDevelopment()`.**

In local development the Google OAuth flow requires a valid `@onevo.io` Google account and a running OAuth callback, which is impractical for backend-only development and testing. A dev-only carve-out allows email/password login against static credentials configured in `appsettings.Development.json`.

```
POST /admin/v1/auth/login
Content-Type: application/json

{ "email": "dev@onevo.io", "password": "<DevAdmin:Password>" }
```

**Behaviour:**
- Returns `403 Forbidden` in any environment where `IsDevelopment()` is `false` — the endpoint does not exist functionally in Production or Staging.
- Credentials are sourced exclusively from `appsettings.Development.json` under `DevAdmin:Email` and `DevAdmin:Password` — never from the database.
- The issued JWT is structurally identical to a standard platform-admin JWT with `platform_role: "super_admin"`.
- This carve-out does **not** create or modify a `dev_platform_accounts` row. It is a test scaffold, not a real account.
- The endpoint must never be wired to a database credential lookup even in development — static config only.

**Design decision:** Static credential chosen over Google OAuth mocking because mocking requires a running OAuth provider or token-stubbing in every developer environment. The `IsDevelopment()` guard ensures the carve-out cannot leak to production.
