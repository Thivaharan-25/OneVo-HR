# Module Catalog

## Purpose

Module Catalog maintains the master list of actual ONEVO product modules. It defines module metadata, feature keys, seeded permission keys, setup defaults, and reference pricing/storage/AI values used by Subscription Plans.

It does not decide whether a module is a base package module or an optional add-on. That decision belongs to Subscription Plans.

## Required Screens

- Module Catalog list
- Module detail
- Create/Edit module
- Pricing references tab
- Permission keys tab
- Usage summary tab

## Required Fields

| Field | Notes |
|---|---|
| Module key | Permanent identifier; cannot change after creation |
| Display name | User-facing/operator-facing module name |
| Short description | Summary for catalog and plan setup |
| Active/inactive status | Inactive modules cannot be selected for new plans |
| Pillar/category | Product grouping only; not commercial package logic |
| Feature keys | Commercial feature keys inside the module |
| AI-enabled flag | Indicates whether AI token references are relevant |
| Storage-consuming flag | Indicates whether storage references are relevant |
| Setup defaults | Defaults used when a tenant is provisioned |
| Company-size pricing references | Reference only |
| Storage reference by company size | Reference only |
| AI token reference by company size | Reference only |

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `module_catalog` | Read + write - module metadata and active state |
| `module_catalog_pricing_references` | Read + write - company-size pricing references |
| `module_catalog_storage_references` | Read + write - company-size storage references |
| `module_catalog_ai_references` | Read + write - company-size AI token references |
| `module_features` | Read + write - feature keys inside each module |
| `module_permission_keys` | Read - permission keys shown for clarity |
| `module_permission_ownership` | Read + write - exclusive ownership of seeded tenant-facing permission codes where ownership mapping is required |
| `tenant_subscriptions` | Read - usage/tenant impact only |
| Audit log | Write every catalog change |

## Boundary Rules

- Module Catalog is the master list of actual ONEVO modules.
- Module Catalog does not decide base package vs optional add-on.
- Subscription Plans owns plan composition, add-on configuration, and resource-only add-ons.
- Permission keys are shown for clarity; normal module setup does not manually create new permission keys.
- Storage and AI values are references only.
- Existing tenant subscriptions do not automatically change when catalog references change.
- Inactive modules cannot be selected for new plans.

## Usage Summary

The module detail usage summary should show:

- Previous month usage across tenants
- Number of subscribed tenants
- Last updated by
- Module active since date

## Navigation

| Route | Permission |
|---|---|
| `/platform/module-catalog` | `platform.module_catalog.read` |
| Write operations | `platform.module_catalog.manage` |

## Key Rules

- Module key is permanent.
- Feature flags may reference module features for runtime control, but they do not define what the tenant bought.
- A tenant can access a feature only when the tenant has the module entitlement, the plan/custom contract includes that feature, the runtime flag status permits access, and the user has the required permission.
- Catalog reference updates do not retroactively reprice existing tenant subscription snapshots.
- Integration catalog is operator-managed; no hardcoded integration entries in ONEVO application code.

## Related

- [[developer-platform/modules/module-catalog-manager/end-to-end-logic|Module Catalog End-to-End Logic]]
- [[developer-platform/modules/subscription-manager/overview|Subscription Plans]]
- [[developer-platform/modules/feature-flag-manager/overview|Tenant Runtime Overrides]]
- [[developer-platform/modules/tenant-console/overview|Tenant Management]]
- [[developer-platform/modules/role-template-manager/overview|Role Template Manager]]
