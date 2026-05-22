# Module Catalog Manager End-to-End Logic

## Create Product Module

1. Operator opens Platform Management -> Feature Management / Module Catalog.
2. Frontend loads current modules, permission catalog, setup-service links, and pricing units.
3. Operator fills in the create form (see field spec below).
4. Frontend calls `POST /admin/v1/modules/catalog`.
5. Backend verifies `platform.module_catalog.manage`.
6. Backend validates permission ownership (no claimed permission can be owned by two modules) and price bracket shape.
7. Backend writes `module_catalog` and price history where applicable.
8. Backend writes an audit event.

### Create Module — Full Field Specification

**Trigger:** `+ Add Module` button (requires `platform.module_catalog.manage`)

| Field | Label | Type | Required | Validation | Notes |
|---|---|---|---|---|---|
| Module Key | "Module Key (Slug)" | Text input | Yes | Lowercase, underscores only, unique, max 80 chars | Permanent — cannot change after any tenant is entitled. e.g. `leave`, `core_hr`, `activity_monitoring` |
| Display Name | "Display Name" | Text input | Yes | 2–100 chars | Shown to operators in catalog lists and tenant provisioning. |
| Description | "Description" | Textarea | No | Max 500 chars | Shown in module detail and tenant-facing module summaries. |
| Pillar | "Pillar" | Dropdown | Yes | | `HR Management`, `Workforce Intelligence`, `WorkSync`, `Shared` — maps to `hr_management \| workforce_intelligence \| worksync \| shared` |
| Pricing Unit | "Pricing Unit" | Dropdown | Yes | | `Per Employee`, `Per Device`, `Per User`, `Per Seat`, `Flat Rate`, `Per Event` |
| Sellable | "Sellable" | Toggle | Yes | Default: On | Off = always-included module (Foundation). Non-sellable modules are auto-included in every plan and cannot be individually priced. |
| Phase | "Phase" | Dropdown | Yes | | `Phase 1` or `Phase 2`. Phase 2 modules are saved with `is_active = false` and are hidden from all plan builders and tenant provisioning until promoted. |
| Has AI Capability | "Includes AI Capability" | Toggle | No | Default: Off | When On, tenants entitled to this module require an `ai_token_limit_per_month` set on their subscription. |
| Requires Storage | "Requires Tenant Storage" | Toggle | No | Default: Off | When On, this module draws from the tenant's storage pool allocation. |
| Setup Service Keys | "Setup Services" | Multi-select from setup service registry | No | | Services that must run during tenant provisioning when this module is entitled (e.g. schema seeds, default config writes). |
| Permission Ownership | "Module Permissions" | Permission picker (see rules below) | No | | Permission codes this module owns. See **Permission Picker Behaviour** section below. |
| Default Permissions | "Default Owner Permissions" | Multi-select from owned permissions | No | Must be a subset of Permission Ownership | Permissions auto-granted to the tenant Owner role when this module is entitled. Only permissions selected in Permission Ownership appear here. |
| Price Brackets | "Pricing Brackets" | Repeatable bracket rows | Yes if Sellable = On | At least one bracket required for sellable modules | Each bracket: `from_units` (int), `to_units` (int or unlimited), `unit_price` (decimal). Brackets must be contiguous and non-overlapping. |
| Is Active | "Active" | Toggle | Yes | Default: On for Phase 1; Off for Phase 2 | Inactive modules are hidden from all plan builders and tenant provisioning. |

**API:** `POST /admin/v1/modules/catalog`

```json
{
  "module_key": "leave",
  "name": "Leave Management",
  "description": "Employee leave requests, approvals, balances, and accrual policies.",
  "pillar": "hr_management",
  "pricing_unit": "per_employee",
  "is_sellable": true,
  "phase": 1,
  "has_ai_capability": false,
  "requires_storage": false,
  "setup_service_keys": ["leave_default_types_seed"],
  "permission_codes": ["leave:read", "leave:apply", "leave:approve", "leave:manage"],
  "default_permission_codes": ["leave:read", "leave:apply"],
  "price_brackets": [
    { "from_units": 1, "to_units": 50, "unit_price": 2.50 },
    { "from_units": 51, "to_units": null, "unit_price": 2.00 }
  ],
  "is_active": true
}
```

---

### Permission Picker Behaviour

The permission picker is used both when **creating** a module and when **editing permission ownership** on an existing module. The same rules apply in both contexts.

**What is loaded:**
Frontend calls `GET /admin/v1/modules/catalog/{moduleKey}/permissions/available` (or `GET /admin/v1/permission-catalog` on create) to load all known permission codes across the platform.

**Display rules:**

| Permission state | How it appears in the picker |
|---|---|
| Unclaimed — not owned by any module | Selectable checkbox, normal style |
| Owned by this module (edit mode) | Already checked, selectable (can deselect to release) |
| Owned by another module | Visible but **disabled** — greyed out, checkbox non-interactive. Tooltip: `"Owned by '{module_name}' — release it there first"` |

**Key rules:**
- All permissions are always shown — the picker never hides already-claimed ones. Operators must be able to see the full permission landscape.
- An operator cannot claim a permission owned by another module without first going to that module and releasing it.
- Backend enforces this as a hard validation error on `POST /admin/v1/modules/catalog` and `PUT /admin/v1/modules/catalog/{moduleKey}/permissions`: any submitted permission code already present in another module's `permission_codes_json` is rejected with a 422 listing the conflicting module key(s).
- Permissions not yet registered in the platform permission catalog (new codes) can be freely claimed.

---

## Update Permission Ownership

1. Operator opens a module detail page → **Permissions** tab.
2. Frontend loads the permission picker pre-populated with this module's currently owned permissions checked. All other permissions are shown — unclaimed ones are selectable, already-owned-by-other-module ones are disabled (see **Permission Picker Behaviour** above).
3. Operator checks or unchecks permission codes.
4. Operator clicks Save.
5. Backend rejects any submitted permission code already owned by another module (422 with conflicting module key listed).
6. Backend updates `module_catalog.permission_codes_json`.
7. Backend recomputes `default_permission_codes` — any default permissions that were deselected are removed from the default set automatically.
8. Backend invalidates affected tenant permission catalog caches.

## Change Pricing

1. Operator updates price brackets or full-license/maintenance rates.
2. Backend stores new catalog values.
3. Backend writes `module_catalog_price_history`.
4. Existing tenant subscription snapshots remain unchanged.
5. Tenant impact page may show stale-price warnings, but does not auto-reprice.

## APIs

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/modules/catalog` | List product modules | `platform.module_catalog.read` |
| POST | `/admin/v1/modules/catalog` | Create product module | `platform.module_catalog.manage` |
| GET | `/admin/v1/modules/catalog/{moduleKey}` | Module detail | `platform.module_catalog.read` |
| PATCH | `/admin/v1/modules/catalog/{moduleKey}` | Update metadata/pricing/limits | `platform.module_catalog.manage` |
| GET | `/admin/v1/modules/catalog/{moduleKey}/permissions` | Module permission ownership | `platform.module_catalog.read` |
| PUT | `/admin/v1/modules/catalog/{moduleKey}/permissions` | Replace permission ownership | `platform.module_catalog.manage` |
| GET | `/admin/v1/modules/catalog/{moduleKey}/pricing` | Pricing detail/history | `platform.module_catalog.read` |
| PATCH | `/admin/v1/modules/catalog/{moduleKey}/pricing` | Update pricing | `platform.module_catalog.manage` |
| GET | `/admin/v1/modules/catalog/{moduleKey}/tenant-impact` | Tenants/plans affected by change | `platform.module_catalog.read` |

## Integration Linking — Connecting Integrations to Modules

Every integration available to tenants is gated by one or more module entitlements. Module Catalog Manager is where the operator defines and manages this link. This is separate from the OAuth app credentials (managed in System Config → Platform OAuth Apps).

### How Integration Gating Works

When a tenant is entitled to a module, the integrations linked to that module become available in the tenant's Integrations section. When the module is disabled, those integrations are disconnected.

**Rule:** A tenant sees an integration only if ALL of its `required_module_keys` are in `active` or `trial` state in `tenant_module_entitlements`.

### Integration Catalog Screen

**Route:** `/platform/feature-management/integrations`

**API:** `GET /admin/v1/integrations/catalog`

The integration catalog is fully **operator-managed**. Operators create entries for every third-party service tenants can connect. Nothing is hardcoded. When a new integration needs to be added, an operator creates a new entry here — no ONEVO deployment required.

> **Important — what belongs here vs elsewhere:**
>
> | Type | Example | Managed In |
> |---|---|---|
> | Customer OAuth — tenant's users log in with their own account | GitHub, Microsoft Teams, Google Calendar, Slack | Integration Catalog (here) — `category = 'customer_oauth'` |
> | Platform-Managed — ONEVO configures; tenants don't act | Biometric terminal webhook, MDM agent distribution | Integration Catalog (here) — `category = 'platform_managed'` |
> | ONEVO's own platform service keys — used for all tenants | Resend (email), Cloudflare, Azure Blob Storage | System Config → Platform Service Keys — NOT here |
> | Payment gateways — ONEVO charges tenants using these | Paddle, PayHere | Subscription Manager → Payment Gateways — NOT here |
>
> Resend and payment gateways are **never** in the integration catalog. The integration catalog is only for integrations that are part of a tenant's feature set.

| Column | Description |
|---|---|
| Logo | Uploaded image — shown in tenant's Integrations tab |
| Integration Name | Operator-set display name |
| Integration Key | Unique slug — operator-set, e.g. `github`, `ms_teams` |
| Category | **Customer OAuth** (tenant's users connect their own account) / **Platform-Managed** (ONEVO configures it — no customer action) |
| Required Modules | Module entitlement condition — shown as badges |
| Auth Type | OAuth2 / Webhook / API Key / SAML / Platform-Managed |
| OAuth App | Which platform OAuth app registration handles the OAuth flow — links to System Config → OAuth Apps |
| Active Connections | Count of tenants with this integration currently connected |
| Is Active | Global on/off — inactive = hidden from all tenants |
| Actions | Edit, View Connected Tenants, Deactivate |

---

### Create Integration Entry — Full Field Specification

**Trigger:** `+ Add Integration` button (requires `platform.module_catalog.manage`)

| Field | Label | Type | Required | Validation | Notes |
|---|---|---|---|---|---|
| Integration Key | "Integration Key (Slug)" | Text input | Yes | Lowercase, hyphens only, unique, max 50 chars | Permanent — cannot change after tenants connect. e.g. `github`, `ms_teams`, `google_cal` |
| Logo | "Integration Logo" | File upload | No | PNG, SVG, or JPEG. Max 500KB. Recommended: 256×256px transparent PNG or SVG | Uploaded to platform file storage. Displayed in tenant's Integrations tab, module detail view, and the integration catalog list. Upload sends a multipart `POST /admin/v1/uploads/integration-logo` first; returns a `logo_url`. That URL is then submitted with the create form. Alternatively paste an external URL if not uploading. |
| Display Name | "Display Name" | Text input | Yes | 2–80 chars | Shown to operators and tenants. e.g. "GitHub", "Microsoft Teams" |
| Description | "Description" | Textarea | No | Max 300 chars | Shown in tenant's Integrations section as a short explanation of what this integration does |
| Category | "Category" | Radio | Yes | | **Customer OAuth** — the tenant's own users log in with their own third-party account to connect (GitHub org, Microsoft workspace, Google account, Slack workspace). **Platform-Managed** — ONEVO configures the connection; no customer action required (biometric terminal webhook, MDM distribution). This determines whether tenants see a "Connect" button or not. |
| Auth Type | "Authentication Type" | Dropdown | Yes | | OAuth2, API Key (customer enters their own key), Webhook (inbound only — customer configures their system to send), SAML, Platform-Managed (no customer action) |
| OAuth App | "OAuth App Registration" | Dropdown | Yes if Auth Type = OAuth2 | | Select from OAuth apps configured in System Config → OAuth Apps. This is ONEVO's registered developer app with the provider. The customer authorises ONEVO's app during the OAuth flow. |
| Required Modules Condition | "Module Requirement Condition" | Radio: Any of / All of | Yes | | Any of = at least one of the listed modules must be entitled. All of = every listed module must be entitled. |
| Required Module Keys | "Required Modules" | Multi-select from module catalog | Yes | At least one | Tenant must satisfy this condition to see the integration |
| Is Active | "Active" | Toggle | Yes | Default: On | Inactive = integration hidden from all tenants globally regardless of entitlements |

**API:** `POST /admin/v1/integrations/catalog`

**Logo upload (before save):**

```http
POST /admin/v1/uploads/integration-logo
Content-Type: multipart/form-data

file: <binary PNG/SVG/JPEG, max 500KB>
```

Response: `{ "logo_url": "https://storage.onevo.io/integration-logos/ms_teams_abc123.png" }`

**Create integration entry (with logo_url from upload):**

```json
{
  "integration_key": "ms_teams",
  "display_name": "Microsoft Teams",
  "description": "Connect your Microsoft Teams workspace for notifications and chat.",
  "category": "customer_oauth",
  "auth_type": "oauth2",
  "oauth_app_provider": "microsoft",
  "required_module_condition": "any",
  "required_module_keys": ["chat", "chat_ai", "integrations"],
  "is_active": true,
  "logo_url": "https://storage.onevo.io/integration-logos/ms_teams_abc123.png"
}
```

**State written:** `integration_catalog` row created. Audit log entry.

---

### Integrations Section Inside Module Detail View

In the Module Catalog Manager, every module has an **Integrations** tab on its detail page. This is where integrations are linked to that module — it is part of the module's catalog definition, exactly like pricing and permissions.

**Route:** `/platform/feature-management/modules/{moduleKey}/integrations`

**What it shows:**

| Column | Description |
|---|---|
| Integration Name | Name from `integration_catalog` |
| Integration Key | Slug, e.g. `github` |
| Category | Customer OAuth / Platform-Managed |
| Auth Type | OAuth2, Webhook, API Key, SAML |
| Active Connections | How many tenants with this module have connected this integration |
| Actions | Unlink (removes the integration from this module), View Connected Tenants |

**How to link an integration to a module:**

1. Open Module Catalog Manager → select the module (e.g., "Work Management")
2. Click the **Integrations** tab
3. Click **Link Integration**
4. Dropdown shows all active entries in `integration_catalog` that are not already linked to this module
5. Select the integration (e.g., "GitHub")
6. Set condition: **Required** (module must be entitled for this integration to be available) or **Optional** (integration is available when module is entitled but not required to use the module)
7. Click Save

**API:** `POST /admin/v1/modules/catalog/{moduleKey}/integrations`

```json
{
  "integration_key": "github",
  "link_type": "required"
}
```

**State written:** `module_integration_links` row: `(module_key, integration_key, link_type)`. The `integration_catalog.required_module_keys` is updated to include this module key.

**What this controls:** When a tenant is entitled to the "Work Management" module, every integration linked to it with `link_type = 'required'` becomes available in that tenant's Integrations section in the main ONEVO app. The tenant's users can then connect those integrations themselves (for Customer OAuth types) or the operator configures them (for Platform-Managed types).

**Unlinking an integration:**

`DELETE /admin/v1/modules/catalog/{moduleKey}/integrations/{integrationKey}`

Requires `reason` (min 10 chars). Side effect: any tenant entitled to this module but NOT entitled to any other module that still links this integration will have that integration disconnected. Warning confirmation shown before delete:

```
⚠ Unlinking "GitHub" from "Work Management" will disconnect GitHub for:
  14 tenants who have Work Management entitled but no other module linking GitHub.
Tenants entitled to both Work Management and [other module linking GitHub] are unaffected.
```

---

### Edit Integration Entry

**Trigger:** Click "Edit" on an integration row.

All fields editable except `integration_key` (permanent after first tenant connection) and `category` (structural).

Changing `required_module_keys` has immediate effect:
- Tenants who now qualify → integration becomes visible in their app on next load
- Tenants who no longer qualify → `tenant_integration_credentials.status = 'disconnected'`; Warning alert raised: `integration.access_revoked`

**API:** `PATCH /admin/v1/integrations/catalog/{integrationKey}`

Requires `reason` field (min 10 chars) when changing `required_module_keys` or `is_active` — because these changes affect live tenants.

### Module Disable Warning — Integration Impact

When an operator disables a module for a tenant (via Feature Flag Manager or Tenant Console → Subscriptions), the system checks:

1. Which integrations have `required_module_keys` containing this module key
2. Whether the tenant has any of those integrations connected (`tenant_integration_credentials.status = 'connected'`)
3. If yes: shows a confirmation warning before the disable action:

```
⚠ Disabling "Agentic Chat" for TechNova Solutions will also disconnect:
  • Microsoft Teams (connected — james@technova.com, connected May 12 2024)
  • Slack (connected — james@technova.com, connected Jun 1 2024)

Are you sure? This cannot be undone without re-entitling the module.
```

Operator must explicitly confirm before the module is disabled and integrations disconnected.

---

## APIs — Full Catalog

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/modules/catalog` | List all product modules | `platform.module_catalog.read` |
| POST | `/admin/v1/modules/catalog` | Create product module | `platform.module_catalog.manage` |
| GET | `/admin/v1/modules/catalog/{moduleKey}` | Module detail (pricing, permissions, integrations tabs) | `platform.module_catalog.read` |
| PATCH | `/admin/v1/modules/catalog/{moduleKey}` | Update module metadata/limits | `platform.module_catalog.manage` |
| GET | `/admin/v1/modules/catalog/{moduleKey}/permissions` | Permission codes owned by this module | `platform.module_catalog.read` |
| PUT | `/admin/v1/modules/catalog/{moduleKey}/permissions` | Replace permission ownership | `platform.module_catalog.manage` |
| GET | `/admin/v1/modules/catalog/{moduleKey}/pricing` | Pricing detail and price history | `platform.module_catalog.read` |
| PATCH | `/admin/v1/modules/catalog/{moduleKey}/pricing` | Update module pricing | `platform.module_catalog.manage` |
| GET | `/admin/v1/modules/catalog/{moduleKey}/tenant-impact` | Tenants and plans affected by a pending change | `platform.module_catalog.read` |
| GET | `/admin/v1/modules/catalog/{moduleKey}/integrations` | Integrations linked to this module | `platform.module_catalog.read` |
| POST | `/admin/v1/modules/catalog/{moduleKey}/integrations` | Link an integration to this module | `platform.module_catalog.manage` |
| DELETE | `/admin/v1/modules/catalog/{moduleKey}/integrations/{integrationKey}` | Unlink integration from module | `platform.module_catalog.manage` |
| GET | `/admin/v1/integrations/catalog` | Full integration catalog | `platform.module_catalog.read` |
| POST | `/admin/v1/integrations/catalog` | Create a new integration entry | `platform.module_catalog.manage` |
| GET | `/admin/v1/integrations/catalog/{integrationKey}` | Integration detail | `platform.module_catalog.read` |
| PATCH | `/admin/v1/integrations/catalog/{integrationKey}` | Edit integration entry | `platform.module_catalog.manage` |
| GET | `/admin/v1/integrations/catalog/{integrationKey}/tenant-connections` | Tenants with this integration connected | `platform.module_catalog.read` |

---

## Data Flow Summary

| Consumer | What It Reads From Module Catalog Manager |
|---|---|
| Subscription Manager | Module pricing brackets to calculate plan prices |
| Tenant Console (Step 3 wizard) | Module list + pricing to populate the module selector |
| Tenant Console (Subscriptions tab) | Module entitlement state per tenant |
| Role Template Manager | Permission codes per module to filter the permission catalog |
| Main ONEVO app (tenant-facing) | `module_integration_links` + `integration_catalog` to determine which integrations a tenant can access based on their entitled modules |
| Tenant Detail → Integrations tab (developer console) | Same integration link data for read-only operator view |
