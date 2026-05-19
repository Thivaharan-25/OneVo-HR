# Module Catalog Manager

## Purpose

Module Catalog Manager maintains the ONEVO product module catalog — the global registry that defines what ONEVO sells, what it costs, what permissions it owns, and what integrations it enables. Every tenant provisioning decision, subscription plan, role template, and integration availability flows from this catalog.

It manages ONEVO product modules only. Developer Platform sidebar access is owned by [[developer-platform/modules/platform-access/overview|Platform Access]].

## Phase 1 Modules in Catalog

**Foundation (always included — not separately sellable):**
`auth`, `configuration`, `roles`, `notifications`, `org`

**Package 1 — HR Core:** `core_hr`, `leave`, `calendar`

**Package 1 — Intelligence:** `monitoring`, `workforce`, `verification`, `exceptions`, `analytics`

**Package 2 — Work Management:** `work_management`, `chat`, `chat_ai`, `documents`, `reports`, `integrations`

**Phase 2 (catalog entries exist but `is_active = false`, `phase = 2`):**
`payroll`, `performance`, `skills`, `learning`, `recruitment`, `hr_docs`, `grievance`, `expense`

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `module_catalog` | Read + write — module metadata, pricing brackets, permission ownership, limits |
| `module_catalog_price_history` | Write — immutable price change history |
| `integration_catalog` | Read + write — integration entries, their category, auth type, required modules |
| `module_integration_links` | Read + write — which integrations are linked to which modules |
| `tenant_module_entitlements` | Read — tenant impact queries only; writes go through Tenant Console |
| Auth permission catalog | Read — available permissions for ownership assignment |
| Audit log | Write every catalog change |

## Capabilities

### Product Module Catalog
- Create and update product module entries (metadata, pillar, phase, sellable state, pricing unit)
- Maintain pricing brackets by company-size range — changes create immutable price history entries
- Maintain full-license price and annual maintenance rate
- Assign permission codes to exactly one module — permission ownership is exclusive
- Preview tenant impact before any catalog change (how many tenants/plans would be affected)
- View per-module integration links

### Integration Catalog
- Create operator-managed integration entries — nothing hardcoded. Every integration tenants can connect is created here (GitHub, Teams, Slack, etc.)
- Set integration category: **Customer OAuth** (tenant users log in with their own account) or **Platform-Managed** (ONEVO configures it)
- Set auth type: OAuth2, API Key, Webhook, SAML, Platform-Managed
- Link to a Platform OAuth App registration (from System Config) for OAuth2 integrations
- Upload integration logo (PNG/SVG/JPEG, max 500KB)
- Set required module entitlement condition (ANY of / ALL of selected module keys)

### Module-Integration Linking
- Link any integration to any module via the module detail page → Integrations tab
- When a tenant is entitled to a module, all integrations linked to that module become available to them
- Unlink with impact warning showing how many tenants would lose integration access

## Navigation

| Route | Permission |
|---|---|
| `/platform/feature-management` | `platform.module_catalog.read` |
| Write operations | `platform.module_catalog.manage` |

## Key Rules

- Module key is permanent — cannot change after creation
- Phase 2 modules cannot be added to Phase 1 subscription plans or tenant entitlements
- A permission belongs to exactly one module — adding it to another requires removing it first
- Catalog price updates do NOT retroactively reprice existing tenant subscription snapshots
- Integration catalog is fully operator-managed — no hardcoded entries in ONEVO application code
- Changing an integration's `required_module_keys` immediately affects tenant integration access

## Related

- [[developer-platform/modules/module-catalog-manager/end-to-end-logic|Module Catalog Manager End-to-End Logic]]
- [[developer-platform/modules/subscription-manager/overview|Subscription Manager]] — plans reference module catalog for pricing
- [[developer-platform/modules/tenant-console/overview|Tenant Console]] — tenant entitlements read from module catalog
- [[developer-platform/modules/role-template-manager/overview|Role Template Manager]] — permission catalog filtered by module ownership
- [[developer-platform/modules/system-config/overview|System Config]] — Platform OAuth Apps used by Customer OAuth integrations
