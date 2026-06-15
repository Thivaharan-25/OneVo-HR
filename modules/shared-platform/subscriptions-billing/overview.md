# Subscriptions & Billing

**Module:** Shared Platform  
**Feature:** Subscriptions & Billing

---

## Purpose

Subscriptions & Billing supports demo-to-paid upgrade, tenant invoices, payments, plan/add-on entitlements, shared storage limits, shared AI token allowances, and billing audit history.

Current corrected model:

```text
final billing =
  one selected base plan
  + selected optional module add-ons
  + selected resource-only add-ons
```

Storage and AI limits are calculated as:

```text
base plan shared storage/AI
+ selected module add-on storage/AI contribution
+ selected resource add-on storage/AI contribution
+ approved tenant-specific overrides
```

## Database Areas

### `subscription_plans`

Global paid plan definitions. Plans define name, tier/label, description, active status, supported billing cycles, annual override/discount, company-size pricing brackets, shared base storage allocation, and shared base AI token allowance.

Paid subscription plans do not define demo/trial duration. Demo Profiles define trial duration, auto-expiry, demo limits, and upgrade eligibility before a tenant becomes paid.

### `subscription_plan_modules`

Plan module composition. Each selected module is either:

- `base` - included automatically with the selected plan
- `optional_addon` - charged only when selected

A module cannot be both base and optional add-on in the same plan.

### `subscription_plan_resource_addons`

Resource-only add-ons such as Extra Storage Pack and Extra AI Token Pack. These increase shared tenant resource limits and do not create module entitlements.

### `module_catalog`

Global module registry. Module Catalog provides active module definitions and reference values only. It does not decide base/add-on classification and does not automatically change existing tenant subscriptions.

### `tenant_subscriptions`

Tenant commercial snapshot: selected plan, billing cycle, confirmed employee count/company size, selected optional module add-ons, selected resource add-ons, calculated prices, overrides, status, invoice/payment state, and cancellation state.

### `tenant_resource_limits`

Resolved shared tenant storage and AI allowances after base plan, add-ons, resource packs, and tenant-specific overrides.

### `subscription_invoices`

Invoices generated for first payment and recurring billing. Statuses include `draft`, `open`, `paid`, and `void`.

## Demo Upgrade Flow

1. Tenant opens upgrade options.
2. Backend returns only plans and add-ons allowed by the active Demo Profile.
3. Tenant confirms actual employee count/company size.
4. Tenant selects one allowed subscription plan.
5. Tenant selects allowed optional add-ons and resource-only add-ons.
6. Tenant selects monthly or annual billing.
7. Backend returns quote.
8. Tenant submits upgrade with company details, confirmed employee count, selected plan/add-ons, billing cycle, and billing contact.
9. Backend generates the first invoice from the matching company-size price bracket, applies the selected plan/add-ons in pending-payment state, calculates shared storage/AI, and writes audit history.
10. Tenant pays the first invoice and becomes active when payment succeeds.

## Billing Rules

- First invoice uses the confirmed employee count/company-size bracket.
- Annual amount starts from monthly amount x 12, then applies annual override or annual discount when configured.
- Monthly tenants can add users beyond purchased seats; extra seats become due on the next monthly invoice.
- Annual added seats are charged for remaining months in the annual term.
- Cancellation and renewal changes are blocked while unpaid seat dues or unpaid added-seat dues exist.
- A tenant cannot be charged twice for the same module.
- A tenant cannot be entitled twice to the same module.

## Tenant-Facing APIs

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/demo/upgrade/options` | `billing:read` | Allowed plans/add-ons from active demo profile |
| POST | `/api/v1/demo/upgrade/quote` | `billing:read` | Calculate price, storage, AI allowance, and billing cycle totals |
| POST | `/api/v1/demo/upgrade/submit` | `billing:manage` | Generate first invoice for self-service demo upgrade |
| GET | `/api/v1/billing/invoices` | `billing:read` | List tenant invoices |
| POST | `/api/v1/billing/payment` | `billing:manage` | Pay first or open invoice |
| POST | `/api/v1/trial-extension/request` | `billing:manage` | Request trial extension |
| GET | `/api/v1/support/tickets` | `support:read` | Tenant support tickets |
| POST | `/api/v1/support/tickets` | `support:manage` | Create support ticket |

## Related

- [[modules/shared-platform/overview|Shared Platform Module]]
- [[developer-platform/modules/subscription-manager/overview|Subscription Plans]]
- [[developer-platform/modules/module-catalog-manager/overview|Module Catalog]]
- [[developer-platform/modules/demo-profiles/overview|Demo Profiles]]
- [[developer-platform/modules/requests-center/overview|Requests Center]]
