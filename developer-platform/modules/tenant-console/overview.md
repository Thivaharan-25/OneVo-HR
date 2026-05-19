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
| setup services catalog | Read + write — module-connected free/global and paid setup services |
| configuration templates | Read + write — reusable setup templates and tenant-specific template applications |
| `payment_gateway_configs` | Read/write safe Paddle/PayHere gateway config metadata and encrypted secrets |
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
Sets or changes a tenant's plan and commercial terms. This is used during tenant creation Step 2 and as a reviewed post-activation exception tool.

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
- The primary Phase 1 payment gateways are Paddle (international) and PayHere (Sri Lanka). Operators configure gateway metadata/secrets through Developer Platform gateway config APIs; secrets are encrypted and never shown after save.

The console must keep commercial entitlements separate from RBAC permissions. Commercial state decides whether a tenant has bought or trialed a capability; RBAC decides which users inside that tenant can use it.

Pricing is configurable, not hardcoded. Operators can configure module price brackets by company-size range, reusable plan calculated prices, plan override prices, per-employee rates (billing is user-based; no device-based billing), one-time full-license prices, annual maintenance rates, trial terms, AI monthly token limits, tenant storage limits, and custom enterprise contract values. **Users with monitoring fully disabled are excluded from the Package 1 billable seat count.** Module access is resolved from the active subscription/commercial terms, plan allowed modules, tenant module grants, and tenant feature grants.

Plan and module base costs are managed in the reusable catalogs:

- `POST /admin/v1/subscription-plans` and `PATCH /admin/v1/subscription-plans/{id}` create/update reusable plans from selected packages/modules, company-size range, calculated prices, optional override prices, active state, and AI monthly token limits.
- `POST /admin/v1/modules/catalog` and `PATCH /admin/v1/modules/catalog/{moduleKey}` create/update reusable module metadata, module-owned permission set, `price_brackets`, full-license price, and maintenance rate.
- `PATCH /admin/v1/tenants/{id}/subscription` stores tenant-specific commercial terms, selected company-size range, selected module keys, calculated price snapshots, negotiated monthly/annual/full-license/maintenance pricing, AI monthly token limit, Work Management storage limit, billing evidence references, and payment exception/grace dates.
- `PUT /admin/v1/tenants/{id}/modules` stores tenant-specific module sales state and price overrides.

Changing a reusable catalog price must not silently rewrite existing tenant contracts. Existing tenants keep their stored commercial terms unless ONEVO explicitly runs a reviewed reprice/migration process.

For subscription tenants, enabled modules are plan-included modules plus paid add-ons and trial modules, minus disabled modules. For full-license tenants, enabled modules are owned license modules plus maintenance-included modules, purchased add-ons, and trial modules, minus disabled modules. Expired maintenance may block support, updates, or new modules according to contract policy, but it should not automatically remove already-owned core modules unless the signed agreement says so.

### 4-Step Tenant Creation Wizard

A draft-safe 4-step wizard creates the tenant through the internal operator-only flow (`+ Create Tenant` on the Tenants list). A tenant in `provisioning` status is invisible to the main OneVo app until activated.

| Step | Label | What Happens |
|---|---|---|
| 1 | Organization Info | Company name, legal name, domain, industry (pre-set to Technology/IT — read-only label in Phase 1), company size, description, phone, website. Creates the tenant row with `status = 'provisioning'`. |
| 2 | Admin Account | Owner's first name, last name, email, role assignment, send-invite-on-activation flag. |
| 3 | Subscription Plan | Select reusable plan, confirm company-size price band, select Phase 1 modules only (Package 1 HR Core/Intelligence and/or Package 2 WorkSync — Phase 2 modules not shown), set commercial model, billing cycle, payment collection mode, gateway, AI token limit, tenant storage limit (shared pool for entire tenant), optional pricing override with audit reason. |
| 4 | Configuration | Work mode, monitoring/privacy settings including camera photo capture toggle (if Intelligence modules selected), leave defaults (if Leave selected), data import template, app allowlist template, setup services checklist. |
| Review & Confirm | — | Read-only summary of all steps. Each section has an Edit link. "Activate Tenant" button runs the activation guard and flips status to `active`. |

The wizard is **draft-safe**: after Step 1, the tenant exists and can be resumed. The Tenants list shows a yellow "In Progress" badge. Clicking the row reopens the wizard at the last incomplete step with all saved values pre-populated.

### Post-Activation Management

After activation, all ongoing management happens from the **Tenant Detail page** (click any tenant row in the Tenants list). The detail page has 9 tabs:

| Tab | Contents |
|---|---|
| Overview | KPI cards, user activity chart, work mode distribution, subscription & limits progress bars, recent alerts, top departments, integrations status |
| Usage & Analytics | DAU trend, session duration, feature usage, module engagement heatmap |
| Users | Read-only tenant user list with role, status, last login |
| Devices | Read-only device list with agent version badge and deployment ring |
| Subscriptions | Current plan, module entitlements table, invoices table, override action |
| Policies | Feature flag overrides, global policy overrides for this tenant |
| Integrations | Integration connection status and last sync |
| Activity Log | Full audit trail for this tenant, all actor types |
| Settings | Editable tenant profile, operational settings, monitoring configuration |

No invite email is sent automatically by any wizard step or activation. Email is sent only by the explicit "Send Owner Invite" action.

### Plan, Module, and Cost Rules

- Operators do not create a new plan for every tenant. Plans are reusable catalog entries; tenant-specific pricing lives on `tenant_subscriptions` and module entitlement records.
- Reusable plan prices are calculated from selected `module_catalog.price_brackets` for the selected company-size range. Example: Core HR `$3.50` plus Work Management `$4.00` in the `51-200` range displays `$7.50 per employee`.
- The company-size price band uses the same values as tenant creation, defaults from `tenants.company_size_range`, and can be changed by the operator before saving commercial terms.
- Operator price overrides never erase calculated prices; both calculated and effective/override values are preserved for audit.
- AI-enabled plans require a positive monthly token limit; non-AI plans leave the token limit blank.
- All tenants require a tenant storage limit (`tenant_storage_limit_gb`). Storage is a **single shared pool for the entire tenant** — not split per module. All modules (HR documents, screenshots, payslips, verification photos, attachments) draw from this pool.
- Manual subscription, manual full-license payment, and manual maintenance payment require billing evidence or an approved external reference plus an audit reason.
- Payment exception/grace periods are commercial exceptions that can apply to subscription tenants or full-license/maintenance tenants and are snapshotted onto the tenant commercial record.
- A selected plan can include modules, but the post-creation Manage/Configure flow must still show the effective module set so the operator can confirm, add trials, add purchased modules, or disable exceptions.
- Module prices can come from `module_catalog`, be included by plan, or be overridden per tenant. Store the pricing model, price, currency, dates, and sales state for audit and billing.
- `available` and `quoted` module states do not grant tenant-facing access. `purchased`, `trial`, `subscription_included`, and `maintenance_included` can grant access while valid.
- Commercial entitlement decides what the tenant has bought or trialed. RBAC decides which users inside that tenant can use the entitled modules.

### Role Rules During Provisioning

- Reusable role templates are global operator-managed blueprints.
- Tenant-specific roles can be created directly during Manage/Configure without becoming global templates.
- Applying a template materializes normal tenant-scoped Auth roles and permissions.
- Role creation does not require job levels. Job levels and org hierarchy are only needed for scoped access, approvals, escalation, and workflow routing.
- The first owner/admin invite must assign a materialized tenant role that satisfies the minimum owner/admin permission set.
- The operator never sets the tenant owner's final password; the owner sets it through the invite link.
- No invite email is sent automatically by profile creation, commercial selection, module configuration, setup completion, or activation. Owner invitation is an explicit operator action.
- The same owner email can be invited to more than one tenant. Each accepted invitation grants access only to that tenant.

### Module Catalog Permission Rules

- Each permission belongs to exactly one module.
- Module Catalog screens must show which module owns each permission.
- A permission assigned to one module cannot be assigned to another module unless it is first removed from the original module through an explicit catalog change.
- Subscription plan creation and tenant role/template setup use this module ownership to filter assignable permissions.

### Setup Services And Templates

- Every setup service is connected to one or more module keys.
- Free/global setup services are auto-added when a tenant has a matching entitled module, can still be configured by the operator, and must not create billing.
- Paid setup services must be explicitly selected and tracked.
- A setup service can only be applied when at least one linked module is in the tenant's entitled module set.
- Reusable templates include Configuration Templates, Role Templates, Org Structure Templates, Job Family Templates, Leave Policy Templates, Onboarding Templates, App Allowlist Templates, Monitoring Policy Templates, and Data Import Mapping Templates.
- Applying a reusable template creates tenant-specific configuration that can be customized without changing the global template.

## Notes

- Subscription overrides must not be used as a routine billing management tool. Direct standard subscription changes through the configured Paddle/PayHere gateway flow.
- Role templates are starter configuration. After activation, the tenant owner can create and edit roles inside the tenant app, but only using permissions exposed by enabled modules.

## Related

- [[developer-platform/modules/role-template-manager/overview|Role Template Manager]]
- [[developer-platform/userflow/provisioning-flow|Manual Customer Provisioning Flow]]
- [[modules/auth/overview|Auth & Security]]
- [[modules/configuration/app-allowlist/overview|App Allowlist]]
- [[modules/data-import/overview|Data Import]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]]
