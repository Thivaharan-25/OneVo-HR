# Module Catalog Manager

## Purpose

Module Catalog Manager maintains the ONEVO product module catalog: the global registry that defines what ONEVO sells, which commercial features belong to each module, what it costs, which seeded permissions each module owns, and what integrations it enables. Every tenant provisioning decision, subscription plan, role template, and integration availability flows from this catalog.

It manages ONEVO product modules only. Developer Platform sidebar access is owned by [[developer-platform/modules/platform-access/overview|Platform Access]].

## Phase 1 Modules in Catalog

**Foundation (always included - not separately sellable):**
`auth`, `configuration`, `roles`, `notifications`, `org`, `workflow_engine`

**Package 1 - HR Core:** `core_hr`, `leave`, `calendar`

**Package 1 - Intelligence:** `monitoring`, `workforce`, `verification`, `exceptions`, `analytics`

**Package 2 - Work Management:** `work_management`, `chat`, `chat_ai`, `integrations`

**Phase 2 (catalog entries exist but `is_active = false`, `phase = 2`):**
`payroll`, `performance`, `skills`, `learning`, `recruitment`, `hr_docs`, `grievance`, `expense`, `documents`, `reports`

The authoritative Phase 1 commercial feature list is in [[developer-platform/modules/module-catalog-manager/end-to-end-logic|Module Catalog Manager End-to-End Logic]] under "Phase 1 Commercial Feature Registry". Implementation must seed only that list for Phase 1.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `module_catalog` | Read + write - module metadata, pricing brackets, limits |
| `module_features` | Read + write - commercial feature registry inside each module |
| `module_permission_ownership` | Read + write - exclusive ownership of seeded tenant-facing permission codes |
| `module_catalog_price_history` | Write - immutable price change history |
| `integration_catalog` | Read + write - integration entries, their category, auth type, required modules |
| `module_integration_links` | Read + write - which integrations are linked to which modules |
| `tenant_module_entitlements` | Read - tenant impact queries only; writes go through Tenant Console |
| Auth permission catalog | Read - seeded/version-controlled tenant-facing permissions available for ownership assignment |
| Audit log | Write every catalog change |

## Capabilities

### Product Module Catalog
- Create product module entries with full field spec: module key, display name, pillar, pricing unit, sellable state, phase, AI capability flag, storage flag, setup service keys, price brackets, permission ownership, default permissions, and active state
- Define the commercial feature list inside each module. Example: `work_management.projects`, `work_management.tasks`, `work_management.time_tracking`, `work_management.ai_task_suggestions`.
- Update module metadata, limits, and pricing via the module detail page (separate tabs for Permissions and Pricing)
- Maintain pricing tiers by employee-count range; changes create immutable price history entries
- Maintain full-license price and annual maintenance rate
- Assign seeded permission codes to exactly one module via the permission picker; permission ownership is exclusive
- Mark owned permissions as default permissions for future tenant Owner role materialization
- When a permission is removed from a module's owned set, its default marker is removed with it
- Preview tenant impact before any catalog change
- View per-module integration links

### Integration Catalog
- Create operator-managed integration entries; nothing is hardcoded. Every integration tenants can connect is created here (GitHub, Teams, Slack, etc.)
- Set integration category: **Customer OAuth** (tenant users log in with their own account) or **Platform-Managed** (ONEVO configures it)
- Set auth type: OAuth2, API Key, Webhook, SAML, Platform-Managed
- Link to a Platform OAuth App registration (from System Config) for OAuth2 integrations
- Upload integration logo (PNG/SVG/JPEG, max 500KB)
- Set required module entitlement condition (ANY of / ALL of selected module keys)

### Module-Integration Linking
- Link any integration to any module via the module detail page -> Integrations tab
- When a tenant is entitled to a module, all integrations linked to that module become available to them
- Unlink with impact warning showing how many tenants would lose integration access

## Navigation

| Route | Permission |
|---|---|
| `/platform/module-catalog` | `platform.module_catalog.read` |
| Write operations | `platform.module_catalog.manage` |

## Key Rules

- Module key is permanent; it cannot change after creation
- Module features are commercial packaging units inside a module. Plans and custom contracts choose from these features when partial module packaging is sold.
- Feature flags may reference module features for runtime control, but they do not define what the tenant bought.
- A tenant can access a feature only when the tenant has the module entitlement, the plan/custom contract includes that feature, the runtime flag status permits access, and the user has the required permission.
- Removing features from a tenant's runtime access does not change the module price; pricing changes must go through Subscription Manager or Tenant Console subscription override.
- Phase 2 modules are always saved with `is_active = false` regardless of submitted value.
- Sellable modules require at least one price bracket.
- Permission codes are seeded/version-controlled by the backend permission catalog. Module Catalog assigns ownership of existing permissions; it does not create or rename permission codes.
- A permission belongs to exactly one module through `module_permission_ownership`. Adding it to another module requires removing it from the current owner first.
- Permission namespaces do not need to match module keys. Example: `core_hr` may own `employees:read`, `employees:write`, and `employees:delete`.
- The permission picker always shows all seeded tenant-facing permissions. Permissions owned by another module are visible but disabled.
- Default permissions must always be a subset of permissions owned by the same module.
- Default permission ownership changes apply to future tenant activations only. Existing Owner roles in live tenants are not retroactively modified.
- Catalog price updates do not retroactively reprice existing tenant subscription snapshots.
- Integration catalog is fully operator-managed; no hardcoded integration entries in ONEVO application code.
- Changing an integration's `required_module_keys` immediately affects tenant integration access.

## Related

- [[developer-platform/modules/module-catalog-manager/end-to-end-logic|Module Catalog Manager End-to-End Logic]]
- [[developer-platform/modules/subscription-manager/overview|Subscription Manager]] - plans reference module catalog for pricing
- [[developer-platform/modules/feature-flag-manager/overview|Feature Flag Manager]] - runtime rollout only after commercial inclusion is valid
- [[developer-platform/modules/tenant-console/overview|Tenant Console]] - tenant entitlements read from module catalog
- [[developer-platform/modules/role-template-manager/overview|Role Template Manager]] - permission catalog filtered by module ownership
- [[developer-platform/modules/system-config/overview|System Config]] - Platform OAuth Apps used by Customer OAuth integrations

