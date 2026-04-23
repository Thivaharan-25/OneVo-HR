# Tenant Console

## Purpose

The Tenant Console is the primary operator tool for managing the full lifecycle of OneVo tenants — from provisioning new accounts to suspending problematic ones. It is the authoritative UI for anything that touches a tenant's identity, subscription, and access configuration.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `tenants` | Read + write — status, plan, metadata |
| `users` | Read — per-tenant user list, last login |
| `tenant_settings` | Write — initial and override configuration |
| `subscription_plans` | Read + write — plan assignment |
| `module_registry` | Write — which modules are active per tenant |
| Stripe | Read (normal path); bypassed on subscription override |
| Auth service (JWT) | Write — impersonation token issuance |

## Capabilities

### Tenant List View
- Display all tenants: name, plan tier, status, employee count, created date
- Filter by status (`active`, `suspended`, `provisioning`, `trial`)

### Per-Tenant Detail View
- Current subscription plan and billing dates
- Feature access grants (per-tenant flag overrides)
- Last login timestamp (any user in the tenant)
- Total agent count (desktop agents registered)

### Tenant Lifecycle Actions
- **Suspend / Unsuspend** — toggles `tenants.status`; suspended tenants cannot log in to OneVo
- **Impersonation** — generates a short-lived JWT scoped to the tenant's super-admin role, for support debugging without requiring the customer's credentials. All impersonation events are audit-logged.

### Subscription Override *(exception tool)*
Manually sets or changes a tenant's subscription plan, bypassing Stripe.

> **Important:** This is an exception path only. The normal, primary flow is: customer self-signup → Stripe checkout → plan auto-assigned. Use subscription override only for:
> - Enterprise deals closed by sales (no Stripe checkout)
> - Trial extensions
> - Internal test accounts
> - Fixing a confirmed Stripe sync error

All overrides are audit-logged with the developer account and reason.

### Manual Customer Provisioning Wizard
A 6-step, draft-safe wizard for onboarding tenants outside the self-signup flow. A tenant in `provisioning` status is invisible to the main OneVo app until the wizard is confirmed.

| Step | What Happens |
|---|---|
| 1. Account Setup | Company name, slug, country, industry, legal entity name, timezone |
| 2. Plan Assignment | Pick subscription plan + set billing start date |
| 3. Module Selection | Toggle which modules are active (writes `module_registry`) |
| 4. Initial Configuration | Set key `tenant_settings`: monitoring mode, leave policy defaults, transparency mode |
| 5. Admin User Invite | Create first super-admin user and send invite email |
| 6. Review & Confirm | Summary view — one-click confirm sets `tenants.status` to `active` |

The wizard is **draft-safe**: partially completed tenants remain in `provisioning` status and can be resumed before confirmation.

## Notes

- Subscription overrides must not be used as a routine billing management tool — direct tenants to Stripe for normal plan changes.
