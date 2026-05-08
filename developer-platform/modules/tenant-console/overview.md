# Tenant Console

## Purpose

The Tenant Console is the primary operator tool for managing the full lifecycle of OneVo tenants — from provisioning new accounts to suspending problematic ones. It is the authoritative UI for anything that touches a tenant's identity, subscription, and access configuration.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `tenants` | Read + write — status, plan, metadata |
| `users` | Read — per-tenant user list, last login |
| `tenant_settings` | Write — initial and override configuration |
| `subscription_plans` | Read reusable global plan catalog; assign selected plan to tenant |
| `tenant_subscriptions` | Write tenant-specific commercial terms, billing dates, payment collection modes, gateway refs, full-license payment evidence, custom contract value, and maintenance state |
| `module_catalog` | Read reusable global module catalog and default pricing |
| `payment_gateway_configs` | Read/write safe Stripe/PayHere gateway config metadata and encrypted secrets |
| module entitlement registry | Write through module interfaces - which modules are active per tenant |
| role templates / tenant roles | Read + write through Auth interfaces - starter role configuration |
| Payment gateway | Used for normal subscription collection and full-license maintenance collection; one-time full-license sales can be recorded manually |
| Auth service (JWT) | Write — impersonation token issuance |

## Capabilities

### Tenant List View
- Display all tenants: name, plan tier, status, employee count, created date
- Filter by status (`active`, `suspended`, `provisioning`, `trial`)

### Per-Tenant Detail View
- Current subscription plan and billing dates
- Commercial model: subscription or full license + maintenance
- Maintenance status and renewal date for full-license tenants
- Feature access grants (per-tenant flag overrides)
- Last login timestamp (any user in the tenant)
- Total agent count (desktop agents registered)

### Tenant Lifecycle Actions
- **Suspend / Unsuspend** — toggles `tenants.status`; suspended tenants cannot log in to OneVo
- **Impersonation** — generates a short-lived JWT scoped to the tenant's super-admin role, for support debugging without requiring the customer's credentials. All impersonation events are audit-logged.

### Subscription / Commercial Terms
Sets or changes a tenant's plan and commercial terms. This is used during provisioning and as a reviewed post-activation exception tool.

> **Important:** Post-activation override is an exception path. The normal, primary flow is: sales agreement -> operator creates provisioning draft -> operator assigns commercial terms/modules/role templates/settings -> invite tenant owner -> activate. Use post-activation subscription override only for:
> - Enterprise deals closed by sales or manually adjusted by finance
> - Trial extensions
> - Internal test accounts
> - Fixing a confirmed payment-gateway sync error

All overrides are audit-logged with the developer account and reason.

### Commercial Model Management
ONEVO supports two sales models in Phase 1:

- **Subscription** - the tenant pays recurring SaaS fees for the selected plan/modules.
- **Full license + maintenance** - the tenant has purchased the agreed suite/license, but continues paying recurring maintenance/support. New modules are sold as add-ons, trials, or maintenance-included upgrades depending on the contract.

Payment collection rules:

- Subscription customers normally pay recurring plan/module fees through the system payment gateway.
- Full-license customers may pay the one-time license manually/offline. The operator records the license amount, paid date, and invoice/reference number.
- Maintenance for full-license customers is a separate recurring commercial item and is normally collected through the system payment gateway.
- Manual subscription or manual maintenance collection is allowed only as a reviewed exception with an audit reason.
- The primary Phase 1 payment gateways are Stripe and PayHere. Operators configure gateway metadata/secrets through Developer Platform gateway config APIs; secrets are encrypted and never shown after save.

The console must keep commercial entitlements separate from RBAC permissions. Commercial state decides whether a tenant has bought or trialed a capability; RBAC decides which users inside that tenant can use it.

Pricing is configurable, not hardcoded. Operators can configure plan base prices, module add-on prices, per-employee/device rates, one-time full-license prices, annual maintenance rates, trial terms, and custom enterprise contract values. Module access is resolved from the active subscription/commercial terms, plan allowed modules, tenant module grants, and tenant feature grants.

Plan and module base costs are managed in the reusable catalogs:

- `POST /admin/v1/subscription-plans` and `PATCH /admin/v1/subscription-plans/{id}` create/update reusable plan base prices.
- `POST /admin/v1/modules/catalog` and `PATCH /admin/v1/modules/catalog/{moduleKey}` create/update reusable module default prices.
- `PATCH /admin/v1/tenants/{id}/subscription` stores tenant-specific commercial terms and negotiated plan pricing.
- `PUT /admin/v1/tenants/{id}/modules` stores tenant-specific module sales state and price overrides.

Changing a reusable catalog price must not silently rewrite existing tenant contracts. Existing tenants keep their stored commercial terms unless ONEVO explicitly runs a reviewed reprice/migration process.

For subscription tenants, enabled modules are plan-included modules plus paid add-ons and trial modules, minus disabled modules. For full-license tenants, enabled modules are owned license modules plus maintenance-included modules, purchased add-ons, and trial modules, minus disabled modules. Expired maintenance may block support, updates, or new modules according to contract policy, but it should not automatically remove already-owned core modules unless the signed agreement says so.

### Manual Customer Provisioning Wizard
A 7-step, draft-safe wizard for onboarding tenants through the internal operator-only flow. A tenant in `provisioning` status is invisible to the main OneVo app until the wizard is confirmed.

| Step | What Happens |
|---|---|
| 1. Account Setup | Company name, slug, country, industry, legal entity name, timezone |
| 2. Plan Assignment | Pick reusable subscription plan, commercial model, payment collection mode, billing start date, contract value, discounts, full-license payment evidence, and maintenance billing terms |
| 3. Module Selection | Toggle active modules, sales state, trial dates, and module-level pricing overrides for add-ons/future modules |
| 4. Role Template Setup | Apply reusable ONEVO defaults, create reusable operator templates, or create tenant-specific roles from the module-filtered permission catalog |
| 5. Initial Configuration | Set key `tenant_settings`: monitoring mode, leave policy defaults, transparency mode |
| 6. Admin User Invite | Create first tenant owner/admin user, assign a valid tenant owner role, and send set-password invite email |
| 7. Review & Confirm | Summary view — one-click confirm sets `tenants.status` to `active` |

The wizard is **draft-safe**: partially completed tenants remain in `provisioning` status and can be resumed before confirmation.

### Plan, Module, and Cost Rules

- Operators do not create a new plan for every tenant. Plans are reusable catalog entries; tenant-specific pricing lives on `tenant_subscriptions` and module entitlement records.
- A selected plan can include modules, but the provisioning wizard must still show the effective module set so the operator can confirm, add trials, add purchased modules, or disable exceptions.
- Module prices can come from `module_catalog`, be included by plan, or be overridden per tenant. Store the pricing model, price, currency, dates, and sales state for audit and billing.
- `available` and `quoted` module states do not grant tenant-facing access. `purchased`, `trial`, `subscription_included`, and `maintenance_included` can grant access while valid.
- Commercial entitlement decides what the tenant has bought or trialed. RBAC decides which users inside that tenant can use the entitled modules.

### Role Rules During Provisioning

- Reusable role templates are global operator-managed blueprints.
- Tenant-specific roles can be created directly during provisioning without becoming global templates.
- Applying a template materializes normal tenant-scoped Auth roles and permissions.
- Role creation does not require job levels. Job levels and org hierarchy are only needed for scoped access, approvals, escalation, and workflow routing.
- The first owner/admin invite must assign a materialized tenant role that satisfies the minimum owner/admin permission set.
- The operator never sets the tenant owner's final password; the owner sets it through the invite link.

## Notes

- Subscription overrides must not be used as a routine billing management tool. Direct standard subscription changes through the configured Stripe/PayHere gateway flow.
- Role templates are starter configuration. After activation, the tenant owner can create and edit roles inside the tenant app, but only using permissions exposed by enabled modules.

## Related

- [[developer-platform/modules/role-template-manager|Role Template Manager]]
- [[developer-platform/userflow/provisioning-flow|Manual Customer Provisioning Flow]]
- [[modules/auth/overview|Auth & Security]]
- [[modules/configuration/app-allowlist/overview|App Allowlist]]
- [[modules/data-import/overview|Data Import]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]]
