# Subscription Plans - End-to-End Logic

## Purpose

Subscription Plans maintains the paid plan catalog customers can buy. It owns plan identity, monthly/annual billing options, company-size pricing brackets, base package modules, optional module add-ons, resource-only add-ons, and tenant impact visibility.

Module Catalog is the source of active module definitions and reference values. Subscription Plans decides whether a selected module is included as base package or offered as an optional add-on.

Demo Profiles, not Subscription Plans, own demo/trial duration. Paid plans must not contain trial-day fields; they only define what a customer can buy after demo upgrade or direct paid provisioning.

## Current Commercial Rules

- Final billing equals one selected base plan plus selected optional module add-ons plus selected resource-only add-ons.
- A module cannot be both a base package module and an optional add-on in the same plan.
- A tenant cannot be entitled twice or charged twice for the same module.
- Inactive Module Catalog entries cannot be selected for new plans.
- Storage is one shared tenant pool.
- AI token allowance is one shared tenant allowance.
- Existing tenant subscriptions do not automatically change when plan or catalog references change.

## Route And Permission

**Route:** `/platform/subscription-plans`  
**Read permission:** `platform.subscriptions.read`  
**Manage permission:** `platform.subscriptions.manage`

## Screens

- Subscription Plans list
- Create/Edit Subscription Plan wizard
- Plan detail
- Pricing tab
- Modules tab
- Add-ons tab
- Usage/tenant impact tab

## Plan Fields

| Field | Notes |
|---|---|
| Plan name | Required, unique among active plans |
| Tier/label | Enterprise, Business, Professional, Custom, or product-approved label |
| Description | Operator-facing summary |
| Active status | Inactive plans cannot be selected for new tenants or demo upgrades |
| Supported billing cycles | Monthly, annual |
| Annual price override | Optional explicit annual price |
| Annual discount percentage | Optional discount applied to monthly x 12 |
| Company-size pricing brackets | Required |
| Shared base storage allocation | Base tenant storage pool |
| Shared base AI token allowance | Base tenant AI allowance |

Excluded fields:

- Trial duration / trial days. This belongs to Demo Profiles.
- Demo auto-expiry. This belongs to Demo Profiles.
- Demo-only resource caps. These belong to Demo Profiles.

## Module Selection

For each selected active catalog module, store:

| Field | Notes |
|---|---|
| Module key | From Module Catalog |
| Display name | From Module Catalog snapshot/reference |
| Package type | `base` or `optional_addon` |
| Price by company-size range | Stored on plan pricing |
| Storage contribution | Adds to shared tenant storage when selected |
| AI token contribution | Adds to shared tenant AI allowance when selected and AI-enabled |

Validation:

- Reject a plan if the same module appears as both base and optional add-on.
- Reject inactive catalog modules for new plans.
- Hide optional add-ons already included as base modules during tenant setup and demo upgrade.

## Resource-Only Add-ons

Resource-only add-ons are not modules and do not create module entitlements.

Required add-ons:

| Add-on | Effect |
|---|---|
| Extra Storage Pack | Adds storage to shared tenant pool |
| Extra AI Token Pack | Adds tokens to shared tenant AI allowance |

Fields:

- Add-on label
- Storage contribution per unit
- AI token contribution per unit
- Price per unit by company-size range
- Active status

## Create Or Edit Flow

1. Super Admin opens Subscription Plans.
2. Super Admin creates or edits a plan.
3. Frontend loads active Module Catalog entries.
4. Super Admin enters plan identity, billing cycles, annual settings, company-size brackets, and shared base resources.
5. Super Admin selects base modules and optional module add-ons.
6. Super Admin configures resource-only add-ons.
7. Backend validates duplicate-prevention, inactive-module, and pricing-bracket rules.
8. Backend writes plan records and audit history.
9. Existing tenant subscriptions remain unchanged.

## Tenant/Demo Consumption

Demo Profiles decide the trial window and which plans and optional add-ons a demo tenant can see during upgrade.

When a tenant upgrades:

1. Tenant selects one allowed plan.
2. Tenant selects allowed optional module add-ons.
3. Tenant selects resource-only add-ons if allowed.
4. Tenant chooses monthly or annual billing.
5. Backend calculates quote.
6. Demo upgrade submit applies the selected plan/add-ons in pending-payment state and generates the first invoice from the confirmed employee count/company-size bracket.

Resource limits are calculated as:

```text
base plan shared storage/AI
+ selected module add-on storage/AI contribution
+ selected resource add-on storage/AI contribution
+ approved tenant-specific overrides
```

## APIs

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/subscription-plans` | List plans | `platform.subscriptions.read` |
| POST | `/admin/v1/subscription-plans` | Create plan | `platform.subscriptions.manage` |
| GET | `/admin/v1/subscription-plans/{id}` | Plan detail | `platform.subscriptions.read` |
| PATCH | `/admin/v1/subscription-plans/{id}` | Update plan | `platform.subscriptions.manage` |
| POST | `/admin/v1/subscription-plans/{id}/clone` | Clone plan | `platform.subscriptions.manage` |
| DELETE | `/admin/v1/subscription-plans/{id}` | Deactivate plan | `platform.subscriptions.manage` |
| GET | `/admin/v1/subscription-plans/{id}/tenant-impact` | Tenant impact summary | `platform.subscriptions.read` |

## Tests

- Module cannot be both base and add-on in the same plan.
- Tenant cannot be entitled twice to the same module.
- Tenant cannot be charged twice for the same module.
- Inactive catalog module cannot be selected for new plans.
- Optional add-ons already included as base modules are hidden.
- Storage is calculated as one shared tenant pool.
- AI token limit is calculated as one shared tenant allowance.
- Resource add-ons increase shared limits.
- Existing tenant subscriptions do not change when plan references change.
