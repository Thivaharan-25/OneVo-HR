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

## Role Levels

| Role | Can Do | Cannot Do |
|:---|:---|:---|
| `super_admin` | Everything: all modules, impersonation, account management, system config | Nothing blocked |
| `admin` | All operational modules (tenants, flags, versions, audit, config) | Cannot impersonate tenants, cannot manage dev platform accounts |
| `viewer` | Read-only access to all modules | Cannot write, cannot impersonate, cannot manage accounts |

Role is encoded in the `platform_role` claim of the platform-admin JWT. Authorization checks at the controller or policy level enforce role boundaries. The `PlatformAdmin` policy verifies the role claim is present and valid; individual endpoint policies enforce what each role may call.

---

## Impersonation Model

Impersonation allows a `super_admin` to take a tenant-user's perspective for debugging — seeing exactly what that user sees in the main product. It is strictly controlled.

### How It Works

```
super_admin requests impersonation of user X in tenant Y
        │
        ▼
POST /admin/v1/tenants/{tenantId}/impersonate
{ "target_user_id": "..." }
        │
        ▼
Backend checks:
  - Caller has platform_role = super_admin
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
| Who can issue | `super_admin` only — checked before issuance |
| Scope | Grants read access to that tenant's data through the admin API; does NOT grant a full tenant session |

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
