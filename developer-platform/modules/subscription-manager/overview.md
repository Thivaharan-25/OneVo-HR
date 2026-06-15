# Subscription Plans

## Purpose

Subscription Plans maintains the global paid plan catalog: reusable plans, base package modules, optional module add-ons, resource-only add-ons, company-size pricing brackets, and billing rules. It provides the catalog data that Tenant Management and demo upgrade flows use when a tenant moves to paid service.

Subscription Plans do not define demo/trial duration. Demo Profiles own trial duration, auto-expiry, demo limits, demo module access, and the list of paid plans/add-ons a demo tenant can upgrade into.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `subscription_plans` | Read + write - reusable global plan definitions |
| `subscription_plan_modules` | Read + write - base package vs optional add-on classification |
| `subscription_plan_resource_addons` | Read + write - resource-only storage/AI token packs |
| `subscription_plan_price_brackets` | Read + write - per-plan, per-size-range pricing |
| `subscription_plan_price_history` | Write - immutable price change audit trail |
| `tenant_subscriptions` | Read - current tenant commercial state; write through tenant subscription APIs only |
| `subscription_invoices` | Read + write - invoice lifecycle management |
| `module_catalog` | Read - active module list and reference values for plan setup |
| Audit log | Write every billing action |

## Plan Module Source

Plans can only select active modules from Module Catalog. Inactive modules cannot be selected for new plans. Module Catalog does not decide whether a module is base package or optional add-on; that decision belongs to Subscription Plans.

Module Catalog defines the possible module and feature surface only. A plan can include a module without including every feature key registered under that module. Plan `included_feature_keys` defines the reusable package, and `tenant_subscriptions.selected_feature_keys` defines what a specific tenant actually has after plan/add-on/custom commercial assignment.

Foundation modules that are always required by the product can be auto-included by backend provisioning rules, but they should not be manually priced or exposed as optional add-ons unless product explicitly makes them sellable.

## Capabilities

### Subscription Plans
- Create reusable plans from Phase 1 modules with employee-count pricing tiers. Company-size/employee-count tiers live inside the subscription plan pricing table; they are not module configuration and not separate plan identities.
- Select active catalog modules and classify each as Base Package Module or Optional Add-on.
- Configure resource-only add-ons such as Extra Storage Pack and Extra AI Token Pack.
- Set unit price per base module/add-on/resource pack per employee-count tier -> calculated monthly/annual rate shown live.
- Select which commercial features inside each selected module are included in the plan. This controls what the tenant bought; feature flags only control runtime rollout after this check.
- Store calculated price, annual override, annual discount, and audit history separately.
- Support monthly and annual billing cycles. Tenant owner chooses monthly or annual during demo upgrade or subscription confirmation, not during tenant creation.
- Clone plans; deactivate plans without affecting existing tenant assignments

### Invoice Management
- View all invoices across all tenants with status, amount, and payment method
- Void open invoices
- Download invoice PDFs

## Navigation

| Route | Permission |
|---|---|
| `/platform/subscription-plans` | `platform.subscriptions.read` |
| Write operations | `platform.subscriptions.manage` |

## Key Rules

- Updating a plan's pricing does NOT rewrite existing tenant subscription snapshots
- A module cannot be both base package and optional add-on in the same plan.
- A tenant cannot be entitled or charged twice for the same module.
- Optional add-ons already included as base modules must be hidden during tenant setup and demo upgrade.
- Resource-only add-ons are not modules; they only increase shared tenant storage and/or AI token allowance.
- Tenant storage is one shared tenant pool calculated from base plan, selected add-ons, resource packs, and approved tenant overrides.
- If a plan includes only part of a module, that partial feature inclusion must be recorded in the plan/custom contract. Disabling features through Tenant Runtime Overrides do not reduce price or change billing.
- AI-enabled modules can contribute AI tokens to the shared tenant AI allowance.
- Resource-only add-ons increase shared limits but do not create module entitlements.
- Resource-only add-ons must not add `selected_feature_keys`.
- Trial duration must not be stored or configured on paid subscription plans. Demo/trial tenants receive their trial window from the applied Demo Profile; paid plans start governing access after upgrade/payment activation.
- Unpaid seat dues block cancellation.

## Related

- [[developer-platform/modules/subscription-manager/end-to-end-logic|Subscription Plans End-to-End Logic]]
- [[developer-platform/modules/tenant-console/overview|Tenant Management]] - applies plans to tenants
- [[developer-platform/modules/module-catalog-manager/overview|Module Catalog]] - module references used in plan setup
- [[developer-platform/modules/system-config/overview|System Config]] - payment gateway credential management

