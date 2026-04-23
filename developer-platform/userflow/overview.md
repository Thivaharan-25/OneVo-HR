# User Flow Overview

## Purpose

This section documents the step-by-step flows a developer platform operator follows inside the OneVo Dev Console (`console.onevo.io`). It covers navigation, access levels, and login — with each flow detailed in the sibling files.

---

## Login Flow

1. Navigate to `console.onevo.io/login`
2. Click **Sign in with Google** — redirects to Google OAuth consent
3. Google returns an ID token; backend validates it against `dev_platform_accounts` (checks `is_active = true`)
4. Backend issues a platform-admin JWT (`iss: onevo-platform-admin`, 30-minute expiry)
5. Redirect to `/` — the Tenants list

Accounts not in `dev_platform_accounts` or with `is_active = false` are rejected at step 3 with a 403. There is no self-registration — accounts are provisioned by an existing super_admin.

---

## Navigation Map

| Section | Path | Purpose |
|---|---|---|
| **Tenants** | `/tenants` | List, search, and manage all tenant accounts — provisioning, suspension, impersonation, subscription override |
| **Feature Flags** | `/feature-flags` | View all feature flags, toggle global defaults, and manage per-tenant overrides |
| **Agents** | `/agents/versions` | Manage desktop agent version releases, deployment rings, and force-update commands |
| **Audit** | `/audit` | Read-only cross-tenant audit log with full filter and CSV export |
| **Config** | `/config` | Global default settings that new tenants inherit; override individual tenant settings for support escalations |
| **API Keys** | `/api-keys` | *(Phase 2)* Issue, scope, and revoke platform-level API keys for external integrations |

---

## Access Levels

All developer platform accounts hold one of three roles, stored in `dev_platform_accounts.role`.

| Role | Description |
|---|---|
| `super_admin` | Full access — all destructive and irreversible actions |
| `admin` | Day-to-day operations — reads, toggles, provisioning; cannot perform destructive or impersonation actions |
| `viewer` | Read-only access across all sections |

### Action-to-Role Mapping

| Action | Minimum Role |
|---|---|
| View tenant list and detail | viewer |
| View feature flags | viewer |
| View agent version catalog | viewer |
| View audit logs | viewer |
| Provision a new tenant (wizard) | admin |
| Toggle feature flag global default | admin |
| Toggle per-tenant feature flag override | admin |
| Publish a new agent version | admin |
| Assign tenant to deployment ring | admin |
| Set global config defaults | admin |
| Override individual tenant settings | admin |
| **Suspend / unsuspend tenant** | super_admin |
| **Subscription override** | super_admin |
| **Impersonate tenant admin** | super_admin |
| **Force-update agent ring** | super_admin |
| **Rollback agent version** | super_admin |
| **Recall an agent version** | super_admin |
| **Create / deactivate developer accounts** | super_admin |

The platform-admin JWT includes the `role` claim. All `/admin/v1/*` endpoints enforce role checks server-side — the frontend role gates are a secondary convenience, not the security boundary.

---

## Detailed Flows

| File | Covers |
|---|---|
| `tenant-management.md` | Tenant list, tenant detail, suspend/unsuspend, impersonation, subscription override |
| `provisioning-flow.md` | 6-step manual provisioning wizard |
| `feature-flags.md` | Global flag list, toggle global default, per-tenant override |
| `agent-versions.md` | Version catalog, publish, force-update ring, ring assignment, rollback |
