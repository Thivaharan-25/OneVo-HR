# Module Catalog Manager End-to-End Logic

## Create Product Module

1. Operator opens Platform Management -> Feature Management / Module Catalog.
2. Frontend loads current modules, permission catalog, setup-service links, and pricing units.
3. Operator fills in the create form (see field spec below).
4. Frontend calls `POST /admin/v1/modules/catalog`.
5. Backend verifies `platform.module_catalog.manage`.
6. Backend validates permission ownership (no claimed permission can be owned by two modules) and price bracket shape.
7. Backend writes `module_catalog`, `module_features`, `module_permission_ownership`, and price history where applicable.
8. Backend writes an audit event.

### Create Module - Full Field Specification

**Trigger:** `+ Add Module` button (requires `platform.module_catalog.manage`)

| Field | Label | Type | Required | Validation | Notes |
|---|---|---|---|---|---|
| Module Key | "Module Key (Slug)" | Text input | Yes | Lowercase, underscores only, unique, max 80 chars | Permanent - cannot change after any tenant is entitled. e.g. `time_off`, `core_hr`, `activity_monitoring` |
| Display Name | "Display Name" | Text input | Yes | 2-100 chars | Shown to operators in catalog lists and tenant provisioning. |
| Description | "Description" | Textarea | No | Max 500 chars | Shown in module detail and tenant-facing module summaries. |
| Pillar | "Pillar" | Dropdown | Yes | | `HR Management`, `Monitoring`, `WorkSync`, `Shared` - maps to `hr_management \| monitoring \| worksync \| shared` |
| Pricing Unit | "Pricing Unit" | Dropdown | Yes | | `Per Employee`, `Per Device`, `Per User`, `Per Seat`, `Flat Rate`, `Per Event` |
| Sellable | "Sellable" | Toggle | Yes | Default: On | Off = always-included module (Foundation). Non-sellable modules are auto-included in every plan and cannot be individually priced. |
| Phase | "Phase" | Dropdown | Yes | | `Phase 1` or `Phase 2`. Phase 2 modules are saved with `is_active = false` and are hidden from all plan builders and tenant provisioning until promoted. |
| Has AI Capability | "Includes AI Capability" | Toggle | No | Default: Off | When On, tenants entitled to this module require an `ai_token_limit_per_month` set on their subscription. |
| Requires Storage | "Requires Tenant Storage" | Toggle | No | Default: Off | When On, this module draws from the tenant's storage pool allocation. |
| Setup Service Keys | "Setup Services" | Multi-select from setup service registry | No | | Services that must run during tenant provisioning when this module is entitled (e.g. schema seeds, default config writes). |
| Commercial Features | "Module Features" | Repeatable rows | Yes if Sellable = On | Feature keys must use `{module_key}.{feature_key}` format and be unique within the module | Features that can be included or excluded in subscription plans/custom contracts. Example: `work_management.projects`, `work_management.ai_task_suggestions`. |
| Permission Ownership | "Module Permissions" | Permission picker (see rules below) | No | | Permission codes this module owns. See **Permission Picker Behaviour** section below. |
| Default Permissions | "Default Owner Permissions" | Multi-select from owned permissions | No | Must be a subset of Permission Ownership | Permissions auto-granted to the tenant Owner role when this module is entitled. Only permissions selected in Permission Ownership appear here. |
| Price Brackets | "Pricing Brackets" | Repeatable bracket rows | Yes if Sellable = On | At least one bracket required for sellable modules | Each bracket: `from_units` (int), `to_units` (int or unlimited), `unit_price` (decimal). Brackets must be contiguous and non-overlapping. |
| Is Active | "Active" | Toggle | Yes | Default: On for Phase 1; Off for Phase 2 | Inactive modules are hidden from all plan builders and tenant provisioning. |

**API:** `POST /admin/v1/modules/catalog`

```json
{
  "module_key": "time_off",
  "name": "Time Off Management",
  "description": "Employee Time Off requests, approvals, balances, and accrual policies.",
  "pillar": "hr_management",
  "pricing_unit": "per_employee",
  "is_sellable": true,
  "phase": 1,
  "has_ai_capability": false,
  "requires_storage": false,
  "setup_service_keys": ["time_off_default_types_seed"],
  "features": [
    { "feature_key": "time_off.requests", "name": "Time Off Requests", "is_default_included": true },
    { "feature_key": "time_off.approvals", "name": "Time Off Approvals", "is_default_included": true },
    { "feature_key": "time_off.advanced_accruals", "name": "Advanced Accrual Rules", "is_default_included": false }
  ],
  "permissions": [
    { "permission_code": "time_off:read", "is_default_permission": true },
    { "permission_code": "time_off:create", "is_default_permission": true },
    { "permission_code": "time_off:approve", "is_default_permission": false },
    { "permission_code": "time_off:manage", "is_default_permission": false }
  ],
  "price_brackets": [
    { "from_units": 1, "to_units": 50, "unit_price": 2.50 },
    { "from_units": 51, "to_units": null, "unit_price": 2.00 }
  ],
  "is_active": true
}
```

---

### Phase 1 Commercial Feature Registry

Each sellable Phase 1 module has a feature list managed in Module Catalog. These are commercial packaging units, not rollout flags. Seed only the Phase 1 modules below. Do not seed Phase 2 modules as selectable commercial features in Phase 1.

#### Foundation Modules

Foundation modules are always included and not separately sellable. They do not participate in partial commercial feature packaging in Phase 1.

| Module Key | Feature Key | Display Name | Default Included | Notes |
|---|---|---|---|---|
| `auth` | `auth.optional_google_oauth` | Optional Google OAuth Setup | Yes | Operational flag candidate only, not sellable |
| `auth` | `auth.mfa_enforcement` | MFA Enforcement | Yes | Operational flag candidate only, not sellable |
| `configuration` | `configuration.tenant_settings` | Tenant Settings | Yes | Foundation capability |
| `roles` | `roles.permission_management` | Permission Management | Yes | Foundation capability |
| `notifications` | `notifications.email_delivery` | Email Delivery | Yes | Operational flag candidate only, not sellable |
| `notifications` | `notifications.in_app_delivery` | In-App Delivery | Yes | Operational flag candidate only, not sellable |
| `org` | `org.structure_management` | Organisation Structure Management | Yes | Foundation capability |

#### HR Core Module Group

| Module Key | Feature Key | Display Name | Default Included | Runtime Flag Candidate |
|---|---|---|---|---|
| `core_hr` | `core_hr.employee_profiles` | Employee Profiles | Yes | No |
| `core_hr` | `core_hr.employee_lifecycle` | Employee Lifecycle | Yes | No |
| `core_hr` | `core_hr.onboarding` | Onboarding | Yes | No |
| `core_hr` | `core_hr.offboarding` | Offboarding | Yes | No |
| `core_hr` | `core_hr.dependents_contacts` | Dependents and Emergency Contacts | Yes | No |
| `core_hr` | `core_hr.qualifications` | Qualifications | Yes | No |
| `core_hr` | `core_hr.compensation` | Compensation | Yes | No |
| `time_off` | `time_off.requests` | Time Off Requests | Yes | No |
| `time_off` | `time_off.approvals` | Time Off Approvals | Yes | No |
| `time_off` | `time_off.balances` | Time Off Balances | Yes | No |
| `time_off` | `time_off.accrual_rules` | Accrual Rules | Yes | Yes |
| `time_off` | `time_off.types` | Time Off Types | Yes | No |
| `time_off` | `time_off.calendar_integration` | Calendar Integration | Yes | No |
| `calendar` | `calendar.company_calendar` | Company Calendar | Yes | No |
| `calendar` | `calendar.holidays` | Holidays | Yes | No |
| `time_attendance` | `time_attendance.work_schedules` | Work Schedules | Yes | No |
| `calendar` | `calendar.time_off_visibility` | Time Off Visibility | Yes | No |
| `calendar` | `calendar.event_sync` | Event Sync | Yes | No |

#### Monitoring Module Group

| Module Key | Feature Key | Display Name | Default Included | Runtime Flag Candidate |
|---|---|---|---|---|
| `monitoring` | `monitoring.activity_tracking` | Activity Tracking | Yes | No |
| `monitoring` | `monitoring.app_usage` | App Usage | Yes | No |
| `monitoring` | `monitoring.website_usage` | Website Usage | No | Yes |
| `monitoring` | `monitoring.idle_detection` | Idle Detection | Yes | No |
| `monitoring` | `monitoring.screenshot_on_demand` | On-Demand Screenshots | No | Yes |
| `monitoring` | `monitoring.app_allowlist` | App Allowlist | Yes | Yes |
| `monitoring` | `monitoring.productivity_classification` | Productivity Classification | Yes | Yes |
| `monitoring` | `monitoring.raw_data_processing` | Raw Data Processing | Yes | No |
| `monitoring` | `monitoring.presence_sessions` | Presence Sessions | Yes | No |
| `monitoring` | `monitoring.shift_schedules` | Shift Schedules | Yes | No |
| `monitoring` | `monitoring.break_tracking` | Break Tracking | Yes | No |
| `monitoring` | `monitoring.overtime` | Overtime | Yes | Yes |
| `monitoring` | `monitoring.attendance_corrections` | Attendance Corrections | Yes | Yes |
| `monitoring` | `monitoring.device_sessions` | Device Sessions | Yes | No |
| `monitoring` | `monitoring.biometric_devices` | Biometric Devices | No | Yes |
| `verification` | `verification.identity_checks` | Identity Checks | Yes | No |
| `verification` | `verification.face_match` | Face Match | No | Yes |
| `verification` | `verification.verification_policies` | Verification Policies | Yes | No |
| `verification` | `verification.manual_review` | Manual Review | Yes | Yes |
| `verification` | `verification.photo_challenge` | Photo Challenge | No | Yes |
| `analytics` | `analytics.daily_reports` | Daily Reports | Yes | No |
| `analytics` | `analytics.monthly_reports` | Monthly Reports | Yes | No |
| `analytics` | `analytics.monitoring_snapshots` | Monitoring Snapshots | Yes | No |
| `analytics` | `analytics.productivity_dashboard` | Productivity Dashboard | Yes | Yes |
| `analytics` | `analytics.data_export` | Data Export | No | Yes |
| `analytics` | `analytics.scheduled_reports` | Scheduled Reports | No | Yes |

#### Work Management Module Group

| Module Key | Feature Key | Display Name | Default Included | Runtime Flag Candidate |
|---|---|---|---|---|
| `work_management` | `work_management.projects` | Projects | Yes | No |
| `work_management` | `work_management.tasks` | Tasks | Yes | No |
| `work_management` | `work_management.sprints` | Sprints | Yes | No |
| `work_management` | `work_management.boards` | Boards | Yes | No |
| `work_management` | `work_management.okrs` | OKRs | Yes | No |
| `work_management` | `work_management.roadmaps` | Roadmaps | Yes | No |
| `work_management` | `work_management.time_tracking` | Time Tracking | Yes | No |
| `work_management` | `work_management.resource_planning` | Resource Planning | No | Yes |
| `work_management` | `work_management.work_analytics` | Work Analytics | No | Yes |
| `work_management` | `work_management.github_integration` | GitHub Integration | No | Yes |
| `integrations` | `integrations.microsoft_teams` | Microsoft Teams | No | Yes |
| `integrations` | `integrations.github` | GitHub | No | Yes |
| `integrations` | `integrations.google_workspace` | Google Workspace | No | No |
| `integrations` | `integrations.webhooks` | Webhooks | No | Yes |
| `integrations` | `integrations.api_access` | API Access | No | Yes |

**Implementation rule:** `Runtime Flag Candidate = Yes` means it is acceptable to seed a matching `feature_flags` row. `Runtime Flag Candidate = No` means the feature should normally be controlled only by module entitlement, plan inclusion, permissions, or tenant configuration.

Plans and custom tenant contracts select from this list. Tenant Runtime Overrides can control runtime access to feature keys marked as runtime flag candidates, but only after the feature is commercially included.

**Runtime availability rule:**

```text
module entitlement active
AND feature included in subscription/custom contract
AND feature flag enabled
```

---

### Permission Picker Behaviour

The permission picker is used both when **creating** a module and when **editing permission ownership** on an existing module. The same rules apply in both contexts.

**What is loaded:**
Frontend calls `GET /admin/v1/modules/catalog/{moduleKey}/permissions/available` (or `GET /admin/v1/permission-catalog` on create) to load all known permission codes across the platform.

**Display rules:**

| Permission state | How it appears in the picker |
|---|---|
| Unclaimed - not owned by any module | Selectable checkbox, normal style |
| Owned by this module (edit mode) | Already checked, selectable (can deselect to release) |
| Owned by another module | Visible but **disabled** - greyed out, checkbox non-interactive. Tooltip: `"Owned by '{module_name}' - release it there first"` |

**Key rules:**
- All permissions are always shown - the picker never hides already-claimed ones. Operators must be able to see the full permission landscape.
- An operator cannot claim a permission owned by another module without first going to that module and releasing it.
- Backend enforces this as a hard validation error on `POST /admin/v1/modules/catalog` and `PUT /admin/v1/modules/catalog/{moduleKey}/permissions`: any submitted permission code already present in `module_permission_ownership` for another module is rejected with a 422 listing the conflicting module key(s).
- Permissions must be registered in the seeded permission catalog before they can be claimed. Module Catalog does not create new permission codes.

---

## Update Permission Ownership

1. Operator opens a module detail page -> **Permissions** tab.
2. Frontend loads the permission picker pre-populated with this module's currently owned permissions checked. All other permissions are shown - unclaimed ones are selectable, already-owned-by-other-module ones are disabled (see **Permission Picker Behaviour** above).
3. Operator checks or unchecks permission codes.
4. Operator clicks Save.
5. Backend rejects any submitted permission code already owned by another module (422 with conflicting module key listed).
6. Backend replaces this module's rows in `module_permission_ownership`.
7. Backend clears `is_default_permission` for any default permissions that were deselected.
8. Backend invalidates affected tenant permission catalog caches.

## Change Pricing

1. Operator updates pricing, storage, or AI token reference values.
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
| GET | `/admin/v1/modules/catalog/{moduleKey}/features` | Module commercial feature list | `platform.module_catalog.read` |
| PUT | `/admin/v1/modules/catalog/{moduleKey}/features` | Replace module commercial feature list | `platform.module_catalog.manage` |
| GET | `/admin/v1/modules/catalog/{moduleKey}/pricing` | Pricing detail/history | `platform.module_catalog.read` |
| PATCH | `/admin/v1/modules/catalog/{moduleKey}/pricing` | Update pricing | `platform.module_catalog.manage` |
| GET | `/admin/v1/modules/catalog/{moduleKey}/tenant-impact` | Tenants/plans affected by change | `platform.module_catalog.read` |

## Integration Linking - Connecting Integrations to Modules

Every integration available to tenants is gated by one or more module entitlements. Module Catalog Manager is where the operator defines and manages this link. This is separate from the OAuth app credentials (managed in System Config -> Platform OAuth Apps).

### How Integration Gating Works

When a tenant is entitled to a module, the integrations linked to that module become available in the tenant's Integrations section. When the module is disabled, those integrations are disconnected.

**Rule:** A tenant sees an integration only if at least one module linked to it via `module_integration_links` is in active/entitled state in `tenant_module_entitlements`. Integration visibility is controlled exclusively by `module_integration_links`, not by fields on `integration_catalog`.

### Integration Catalog Screen

**Route:** `/platform/module-catalog/integrations`

**API:** `GET /admin/v1/integrations/catalog`

The integration catalog is fully **operator-managed**. Operators create entries for every third-party service tenants can connect. Nothing is hardcoded. When a new integration needs to be added, an operator creates a new entry here - no ONEVO deployment required.

> **Important - what belongs here vs elsewhere:**
>
> | Type | Example | Managed In | Connected Token Storage |
> |---|---|---|---|
> | Tenant-scope integrations (`connection_scope = 'tenant'`) | GitHub, Zoom, Microsoft Teams | Integration Catalog (here); tokens stored in `tenant_integration_credentials` | `tenant_integration_credentials` |
> | Employee-scope integrations (`connection_scope = 'employee'`) | Google Calendar, Outlook Calendar | Integration Catalog (here); tokens stored in `external_calendar_connections` | `external_calendar_connections` |
> | ONEVO's own OAuth app credentials | GitHub app, Microsoft app, Google app, Zoom app | System Config -> OAuth Apps (`platform_oauth_apps`, `platform_oauth_app_credentials`) - NOT here | N/A - these are ONEVO's developer credentials |
> | ONEVO's own platform service keys | Resend (email), Cloudflare DNS/WAF, Cloudflare R2 object storage | System Config -> Platform Service Keys (`platform_service_keys`) - NOT here | N/A |
> | Payment gateways | Stripe, Paddle, PayHere | System Config -> Payment Gateways (`payment_gateway_configs`) - NOT here | N/A |
> | Biometric terminals | Face, fingerprint, RFID/card, PIN devices | Time & Attendance / Identity Verification -> Biometric Devices (`biometric_devices`) - NOT here | N/A |
>
> The Integration Catalog stores metadata only for connectable software integrations. It does not store provider secrets, tenant tokens, or employee tokens. Resend, Cloudflare, Stripe, Paddle, PayHere, and biometric terminals are **never** in the Integration Catalog. Slack is Phase 2.

| Column | Description |
|---|---|
| Logo | Uploaded image - shown in tenant's Integrations tab |
| Integration Name | Operator-set display name |
| Integration Key | Unique slug - operator-set, e.g. `github`, `zoom` |
| Connection Scope | **Tenant** (tenant-wide connected token in `tenant_integration_credentials`) / **Employee** (per-employee connected token in `external_calendar_connections`) |
| ONEVO App Provider | Which platform OAuth app registration handles the consent flow - links to System Config -> OAuth Apps |
| Linked Modules | Module entitlement condition (read from `module_integration_links`) - shown as badges |
| Active Connections | Count of tenants/employees with this integration currently connected |
| Is Active | Global on/off - inactive = hidden from all tenants |
| Actions | Edit, View Connected Tenants, Deactivate |

---

### Create Integration Entry - Full Field Specification

**Trigger:** `+ Add Integration` button (requires `platform.module_catalog.manage`)

| Field | Label | Type | Required | Validation | Notes |
|---|---|---|---|---|---|
| Integration Key | "Integration Key (Slug)" | Text input | Yes | Lowercase, underscores only, unique, max 50 chars | Permanent - cannot change after tenants connect. e.g. `github`, `zoom`, `google_calendar` |
| Logo | "Integration Logo" | File upload | No | PNG, SVG, or JPEG. Max 500KB. Recommended: 256x256px transparent PNG or SVG | Uploaded to platform file storage. Displayed in tenant's Integrations tab, module detail view, and the integration catalog list. Upload sends a multipart `POST /admin/v1/uploads/integration-logo` first; returns a `logo_url`. That URL is then submitted with the create form. Alternatively paste an external URL if not uploading. |
| Display Name | "Display Name" | Text input | Yes | 2-80 chars | Shown to operators and tenants. e.g. "GitHub", "Zoom", "Google Calendar" |
| Description | "Description" | Textarea | No | Max 300 chars | Shown in tenant's Integrations section as a short explanation of what this integration does |
| Connection Scope | "Connection Scope" | Radio | Yes | | **Tenant** - tenant-wide connected integration; connected token stored in `tenant_integration_credentials`. Examples: GitHub, Zoom, Microsoft Teams. **Employee** - employee/user-level connected integration; connected token stored in `external_calendar_connections`. Examples: Google Calendar, Outlook Calendar. |
| ONEVO App Provider | "ONEVO App Provider" | Dropdown | Yes | | Select from OAuth apps configured in System Config -> OAuth Apps. This is ONEVO's registered developer app with the provider. The tenant/employee authorises ONEVO's app during the consent flow. e.g. `github`, `zoom`, `microsoft`, `google` |
| Is Active | "Active" | Toggle | Yes | Default: On | Inactive = integration hidden from all tenants globally regardless of entitlements |

**Note:** Integration-to-module gating is not set here. After creating the integration entry, link it to one or more modules via the module detail -> Integrations tab (which writes to `module_integration_links`). A tenant sees this integration only if they are entitled to a module that links to it.

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
  "integration_key": "microsoft_teams",
  "display_name": "Microsoft Teams",
  "description": "Connect Microsoft Teams for workspace/member sync. Chat and message sync are Phase 2.",
  "connection_scope": "tenant",
  "onevo_app_provider": "microsoft",
  "is_active": true,
  "logo_url": "https://storage.onevo.io/integration-logos/ms_teams_abc123.png"
}
```

**State written:** `integration_catalog` row created. Audit log entry.

---

### Integrations Section Inside Module Detail View

In the Module Catalog Manager, every module has an **Integrations** tab on its detail page. This is where integrations are linked to that module - it is part of the module's catalog definition, exactly like pricing and permissions.

**Route:** `/platform/module-catalog/modules/{moduleKey}/integrations`

**What it shows:**

| Column | Description |
|---|---|
| Integration Name | Name from `integration_catalog` |
| Integration Key | Slug, e.g. `github` |
| Connection Scope | Tenant / Employee |
| ONEVO App Provider | Which platform OAuth app handles the consent flow |
| Active Connections | How many tenants/employees with this module have connected this integration |
| Actions | Unlink (removes the integration from this module), View Connected Tenants |

**How to link an integration to a module:**

1. Open Module Catalog Manager -> select the module (e.g., "Work Management")
2. Click the **Integrations** tab
3. Click **Link Integration**
4. Dropdown shows all active entries in `integration_catalog` that are not already linked to this module
5. Select the integration (e.g., "GitHub")
6. Click Save

**API:** `POST /admin/v1/modules/catalog/{moduleKey}/integrations`

```json
{
  "integration_key": "github"
}
```

**State written:** `module_integration_links` row: `(module_key, integration_key, linked_by_id, linked_at)`.

**What this controls:** When a tenant is entitled to the module, linked integrations become visible/connectable in that tenant's Integrations section in the main ONEVO app. Tenant-scope integrations (`connection_scope = 'tenant'`) store tokens in `tenant_integration_credentials`; employee-scope integrations (`connection_scope = 'employee'`) store per-user tokens in `external_calendar_connections`.

**Unlinking an integration:**

`DELETE /admin/v1/modules/catalog/{moduleKey}/integrations/{integrationKey}`

Requires `reason` (min 10 chars). Side effect: any tenant entitled to this module but NOT entitled to any other module that still links this integration will have that integration disconnected. Warning confirmation shown before delete:

```
WARNING: Unlinking "GitHub" from "Work Management" will disconnect GitHub for:
  14 tenants who have Work Management entitled but no other module linking GitHub.
Tenants entitled to both Work Management and [other module linking GitHub] are unaffected.
```

---

### Edit Integration Entry

**Trigger:** Click "Edit" on an integration row.

All fields editable except `integration_key` (permanent after first tenant connection) and `connection_scope` (structural - determines where connected tokens are stored).

Changing `is_active` has immediate effect:
- Deactivating -> all connected tenants/employees have this integration disconnected; Warning alert raised: `integration.access_revoked`
- Reactivating -> integration becomes visible again for tenants entitled to a linked module

**API:** `PATCH /admin/v1/integrations/catalog/{integrationKey}`

Requires `reason` field (min 10 chars) when changing `is_active` - because this change affects live tenants. Module-level gating is managed via `module_integration_links`, not on this entry.

### Module Disable Warning - Integration Impact

When an operator disables a module for a tenant (via Tenant Detail -> Runtime Overrides or Tenant Management -> Subscriptions), the system checks:

1. Which integrations are linked to this module via `module_integration_links`
2. Whether the tenant has any of those integrations connected (`tenant_integration_credentials.status = 'connected'`)
3. If yes: shows a confirmation warning before the disable action:

```
WARNING: Disabling "GitHub Integration" for TechNova Solutions will also disconnect:
  - GitHub repository sync (connected - james@technova.com, connected May 12 2024)
  - Microsoft Teams workspace sync (connected - james@technova.com, connected Jun 1 2024)

Are you sure? This cannot be undone without re-entitling the module.
```

Operator must explicitly confirm before the module is disabled and integrations disconnected.

---

## APIs - Full Catalog

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
| Subscription Plans | Module pricing brackets to calculate plan prices |
| Tenant Management (Step 3 wizard) | Module list + pricing to populate the module selector |
| Tenant Management (Subscriptions tab) | Module entitlement state per tenant |
| Role Template Manager | Permission codes per module to filter the permission catalog |
| Main ONEVO app (tenant-facing) | `module_integration_links` + `integration_catalog` to determine which integrations a tenant can access based on their entitled modules |
| Tenant Detail -> Integrations tab (developer console) | Same integration link data for read-only operator view |

