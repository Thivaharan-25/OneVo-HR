# Template Management — End-to-End Logic

## Purpose

Template Management is the single sidebar module for all reusable provisioning and configuration presets. It is organized into eight tabs. This document covers the Role Templates tab in detail and links to the Configuration Template Manager logic for the non-role tabs.

**Route:** `/platform/templates`
**Permission:** `platform.templates.read`

> **Phase 1 scope:** App Allowlist templates and Monitoring Policy templates are provisioning presets managed by Template Management.

---

## Screen Layout

Left tab navigation:
- Role Templates (default)
- Configuration
- Position Templates
- Time Off Policy
- Monitoring Policy
- App Allowlist
- Onboarding
- Data Import

---

## Role Templates Tab

### Page Header

| Element | Value |
|---|---|
| Title | "Template Management" |
| Subtitle | "Manage reusable role blueprints for tenant provisioning." |
| Create Template button | `+ Create Template` — requires `platform.templates.manage` |

### Templates Table

**API:** `GET /admin/v1/role-templates?search={q}&is_system={true|false}&module_key={key}`

| Column | Description | Sortable |
|---|---|---|
| Template Name | Display name | Yes |
| Description | Short description | No |
| Type | System (blue badge) / Custom (gray badge) | Yes |
| Module Scope | Module keys this template scopes to — shown as badges | No |
| Permission Count | Number of permission codes in this template | No |
| Applied To | Count of tenants that have applied this template | No |
| Version | Integer version number — increments on every edit | Yes |
| Last Modified | Date | Yes |
| Actions | Edit, Clone, Apply to Tenant, Deactivate |

**System templates** are pre-seeded by ONEVO and cannot be deleted or directly edited — only cloned. Clone creates a new editable custom template starting from the system template's permissions.

---

## Create Role Template — Full Field Specification

**Trigger:** `+ Create Template` button

### Section 1: Identity

| Field | Label | Type | Required | Validation | Notes |
|---|---|---|---|---|---|
| Template Name | "Template Name" | Text input | Yes | 2–80 chars, unique among active templates | e.g. "HR Admin", "Monitoring Supervisor", "Time Off Manager" |
| Description | "Description" | Textarea | Yes | 10–300 chars | Explains who this role is for and what they can do |
| Is Global Template | "Save as Reusable Global Template" | Toggle | Yes | Default: On | Off = this template is created only for a specific tenant (only available when creating from the Apply to Tenant screen) |

### Section 2: Module Scope Filter

**This section determines the permission boundary.** Permissions are owned by modules. The operator first selects which modules this template draws permissions from — only permissions owned by selected modules appear in the permission picker below.

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| Module Scope | "Include Permissions From Modules" | Multi-select from module catalog (Phase 1 modules only) | Yes | At least one module required. Foundation modules (`auth`, `configuration`, `roles`, `notifications`, `org`) are always included and cannot be deselected — their permissions appear regardless. |

**Foundation module permissions are always shown** in the permission picker because they apply to every tenant. Additional permissions appear only for selected modules.

**Important rule:** The module scope here is the template's design scope — it limits which permissions are shown when building the template. When the template is applied to a specific tenant, the system ADDITIONALLY filters to only permissions from modules the tenant is entitled to. A template scoped to `time_off + monitoring` applied to a tenant with only `time_off` will only grant Time Off permissions — monitoring permissions are silently skipped.

### Section 3: Permission Picker

After selecting module scope, the full permission picker appears. Permissions are grouped by module.

**Layout per module group:**

```
▼ Core HR (core_hr)                    [Select All] [Clear]
  ☑ employees:read          View employee profiles
  ☑ employees:manage        Create and edit employee profiles
  ☐ employees:delete        Delete employee records (irreversible)
  ☑ org:read                View org structure
  ☐ org:manage              Edit org structure
  ...

▼ Time Off Management (time_off)             [Select All] [Clear]
  ☑ time_off:read              View Time Off requests
  ☑ time_off:create             Submit Time Off requests
  ☑ time_off:approve           Approve/reject Time Off
  ☐ time_off:policy:manage     Edit Time Off policies (usually admin only)
  ...
```

**Each permission row shows:**
- Checkbox — selected/unselected
- Permission code — machine-readable, e.g. `time_off:approve`
- Display name — human-readable
- Risk indicator — `⚠ High Risk` badge on permissions that grant irreversible or sensitive access (deletion, financial, impersonation)

**Select All / Clear** per module group.

**Search within permissions:** text input filters the displayed permission list across all module groups.

### Section 4: Template Summary

Read-only summary at the bottom of the form showing:
- Module groups included
- Total permission count
- High-risk permission count (if any) — shown in orange with a warning

### Save Template

**API:** `POST /admin/v1/role-templates`

```json
{
  "name": "HR Admin",
  "description": "Full HR management access. Can manage all employee records, org structure, Time Off, and HR documents. Cannot access payroll or monitoring monitoring.",
  "is_global": true,
  "module_scope": ["core_hr", "time_off", "org_structure", "calendar"],
  "permission_codes": [
    "employees:read",
    "employees:manage",
    "org:read",
    "org:manage",
    "time_off:read",
    "time_off:create",
    "time_off:approve",
    "time_off:policy:manage",
    "calendar:read",
    "calendar:manage"
  ]
}
```

**Validation — server-side:**
- All `permission_codes` must exist in `permissions` table
- All `permission_codes` must be owned by a module in `module_scope` OR owned by a foundation module
- Unknown permission codes → HTTP 422 with list of invalid codes
- Permissions from modules not in `module_scope` and not foundation → HTTP 422

**Response (201 Created):**
```json
{
  "template_id": "tmpl-uuid",
  "name": "HR Admin",
  "version": 1,
  "permission_count": 10,
  "created_at": "2026-05-17T09:00:00Z"
}
```

**API-to-storage mapping:** request `module_scope` is stored as `role_templates.module_keys_json`; request `permission_codes` is stored as `role_templates.permission_codes_json`. Template permissions are stored on the template row, not in a canonical join table.

**State written:** `role_templates` row created with `version = 1`, `is_system = false`, `module_keys_json`, and `permission_codes_json`. Audit log: `action = 'role_template.created'`.

---

## Edit Template — Versioning Behaviour

Editing a template creates a new version. Previous version is preserved for audit.

**API:** `PATCH /admin/v1/role-templates/{id}`

**What can change:** name, description, permission_codes, module_scope.
**What cannot change:** `is_system` (system templates cannot become custom), `is_global` after first tenant application.

**Version increment rule:** every successful PATCH increments `role_templates.version`. The `role_templates.permission_codes_json` and `role_templates.module_keys_json` values are replaced with the submitted canonical set.

**Effect on tenants that previously applied this template:**
- Applying a template materializes **independent** tenant-scoped roles in the Auth module. Those materialized roles are NOT updated when the template is edited.
- The template version at time of application is recorded in the `role_template.applied` audit event and returned through role-template application history projections.
- If a template has been updated, the Apply to Tenant screen shows a "Template updated — re-apply to get latest permissions" warning on tenants still using an older version.

---

## Clone System Template

**Trigger:** "Clone" action on any system template row.

System templates (`is_system = true`) cannot be edited directly. Clone creates a new custom template starting from the system template's current permissions.

**Dialog:**

| Field | Label | Type | Required |
|---|---|---|---|
| New Template Name | "New Template Name" | Text input | Yes |
| Description | "Description" | Textarea — pre-filled from source | Yes |

**API:** `POST /admin/v1/role-templates/{sourceId}/clone`

```json
{
  "name": "HR Admin — Custom",
  "description": "Cloned from system HR Admin template. Customised for enterprise clients."
}
```

**Response:** New template ID with `version = 1`, `is_system = false`, `cloned_from_id` set to source.

---

## Apply Template to Tenant — Full Flow

### Entry Points

1. Role Template Manager → Apply to Tenant tab → select tenant → select template
2. Tenant Management → Tenant Detail → Subscriptions tab → "Manage Roles" → Apply Template

### Permission Boundary Filtering

Before showing the permission picker or confirming an apply, the system filters the template's permissions against the tenant's entitled modules:

```
role_templates.permission_codes_json
    ↓ filter: keep only permissions owned by modules in tenant.entitled_module_keys
tenant_filtered_permissions
```

Permissions from modules the tenant is NOT entitled to are silently excluded. The operator sees a warning showing which permissions were excluded and why.

**Example:** Template "HR Admin" includes `monitoring:read` (owned by `monitoring` module). Tenant is not entitled to `monitoring`. Result: role is applied without `monitoring:read`. Warning shown: "2 permissions excluded — tenant not entitled to: monitoring (monitoring:read, monitoring:sessions:read)."

### Apply Flow — Step by Step

**Screen: Apply Template to Tenant**

**Step 1: Select Tenant**
- Autocomplete search for tenant name/domain
- Shows: tenant name, plan, status, module entitlements summary
- Only active tenants shown

**Step 2: Select Template**
- Dropdown of all active global templates
- Each option shows: template name, permission count, module scope badges

**Step 3: Preview**

System shows:
- **Effective permissions** — template permissions filtered to tenant's entitled modules
- **Excluded permissions** — permissions from modules the tenant doesn't have (grayed out with reason)
- **Role name** — pre-filled as template name, editable
- **Existing role check** — if a role with the same name already exists for this tenant, shows the idempotency warning (see below)

**Step 4: Idempotency Decision**

If a role with the same name already exists for this tenant from a previous template application:

| Option | Label | What Happens |
|---|---|---|
| Update existing | "Update existing role with latest permissions" | Replaces the role's permission codes with the new effective set. Role name unchanged. Users already assigned to this role keep their assignment. |
| Create new | "Create new role with version suffix" | Creates a new role named `{template_name} v2` (or next available suffix). Original role preserved as-is. |
| Cancel | "Cancel" | No changes made |

**Rule:** Applying the same template twice NEVER silently creates duplicate roles. The operator must explicitly choose Update or Create New.

**Step 5: Confirm**

| Field | Label | Type | Required |
|---|---|---|---|
| Reason | "Reason for applying" | Textarea | No — optional for apply |

**API:** `POST /admin/v1/tenants/{tenantId}/templates/{templateId}/apply`

```json
{
  "role_name_override": null,
  "on_duplicate": "update",
  "reason": "Initial provisioning — applying standard HR Admin role."
}
```

**Response (200 OK):**
```json
{
  "tenant_role_id": "role-uuid",
  "role_name": "HR Admin",
  "permissions_applied": 10,
  "permissions_excluded": 2,
  "excluded_reason": "Tenant not entitled to: monitoring",
  "action": "updated",
  "template_version_applied": 3
}
```

**State written:**
- `roles` row created or updated for this tenant (in Auth module, via `ITenantRoleService`)
- `role_permissions` rows replaced with effective permission set
- Audit log: `action = 'role_template.applied'`, actor, tenant, template_id, template_version, role_id, role_name, permissions_excluded_json, and permissions_excluded count

---

## Create Tenant-Specific Role (Without Template)

When a tenant needs a role that is unique to them and should NOT become a global template, operators create it directly.

**Entry:** Apply to Tenant tab → "Create Custom Role" option instead of selecting a template.

**Fields:** Same as Create Template but `is_global = false` and forced to the selected tenant.

**API:** `POST /admin/v1/tenants/{tenantId}/roles`

```json
{
  "name": "Regional HR Manager — APAC",
  "description": "Custom role for TechNova's APAC people-operations group with Time Off approval for APAC org units only.",
  "permission_codes": ["time_off:approve", "employees:read", "org:read"]
}
```

Permission validation is still applied: all codes must exist and be entitled to this tenant.

---

## Owner Role Validation Before Invite

Before the tenant activation guard allows the "Send Owner Invite" action, it checks:
1. At least one materialized role for this tenant has `has_owner_permissions = true`
2. `has_owner_permissions = true` when the role includes ALL of: `roles:manage`, `users:invite`, `settings:manage`, `billing:read`

If no role satisfies this, activation fails with:
```
blocker: "no_owner_role" — No tenant role has the minimum owner permissions required.
Apply the "Tenant Owner" role template or create a role with roles:manage, users:invite, settings:manage, and billing:read.
```

---

## APIs — Full Catalog

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/role-templates` | List templates | `platform.templates.read` |
| POST | `/admin/v1/role-templates` | Create template | `platform.templates.manage` |
| GET | `/admin/v1/role-templates/{id}` | Template detail with permissions | `platform.templates.read` |
| PATCH | `/admin/v1/role-templates/{id}` | Update template (creates new version) | `platform.templates.manage` |
| POST | `/admin/v1/role-templates/{id}/clone` | Clone system or custom template | `platform.templates.manage` |
| DELETE | `/admin/v1/role-templates/{id}` | Deactivate template | `platform.templates.manage` |
| GET | `/admin/v1/tenants/{id}/permissions/catalog` | Module-filtered permission catalog for this tenant | `platform.tenants.read` |
| GET | `/admin/v1/tenants/{id}/roles` | All materialized roles for this tenant | `platform.tenants.read` |
| POST | `/admin/v1/tenants/{id}/roles` | Create tenant-specific role | `platform.tenants.manage` |
| PUT | `/admin/v1/tenants/{id}/roles/{roleId}/permissions` | Replace role permission set | `platform.tenants.manage` |
| DELETE | `/admin/v1/tenants/{id}/roles/{roleId}` | Delete tenant role | `platform.tenants.manage` |
| POST | `/admin/v1/tenants/{id}/role-templates/{templateId}/apply` | Apply role template to tenant | `platform.tenants.manage` |
| GET | `/admin/v1/tenants/{id}/role-template-applications` | History of template applications | `platform.tenants.read` |

---

## Non-role Template Tabs

> Full end-to-end logic for these three tabs — field specs, payload schemas, apply flows, reapply rules, module entitlement guards, and API catalog — is documented in the authoritative spec:
> **[[developer-platform/modules/configuration-template-manager/end-to-end-logic|Configuration Template Manager End-to-End Logic]]** covers Configuration, Position Templates, Time Off Policy, Monitoring Policy, App Allowlist, Onboarding, and Data Import payloads, apply rules, and APIs.

The sections below are a summary only.

## Configuration Tab

Manages reusable `configuration` type templates that pre-fill `tenant_settings` during provisioning.

### Page Header

| Element | Value |
|---|---|
| Title | "Configuration Templates" |
| Subtitle | "Reusable tenant settings presets applied during provisioning." |
| Create button | `+ New Configuration Template` — requires `platform.templates.manage` |

### Configuration Templates Table

**API:** `GET /admin/v1/configuration-templates?type=configuration&search={q}`

| Column | Description | Sortable |
|---|---|---|
| Template Name | Display name | Yes |
| Description | Short description | No |
| Applied To | Count of tenants that have applied this template | Yes |
| Last Modified | Date | Yes |
| Actions | Edit, Duplicate, Deactivate | — |

Search filters by name. Inactive (deactivated) templates are hidden by default; toggle "Show inactive" to include them.

---

### Create Configuration Template — Full Field Specification

**Trigger:** `+ New Configuration Template` button

| Field | Label | Type | Required | Validation | Notes |
|---|---|---|---|---|---|
| Template Name | "Template Name" | Text input | Yes | 2–80 chars, unique among active `configuration` type templates | e.g. "Standard APAC", "Enterprise EU" |
| Description | "Description" | Textarea | Yes | 10–300 chars | Explain the target tenant profile for this preset |
| Timezone | "Default Timezone" | Dropdown (IANA tz list) | Yes | Must be a valid IANA tz string | e.g. `Asia/Colombo`, `Europe/London` |
| Currency | "Currency" | Dropdown (ISO 4217) | Yes | 3-letter code | e.g. `LKR`, `USD`, `EUR` |
| Work Week | "Work Week" | Multi-select (Mon–Sun) | Yes | At least 1 day selected | Defaults Mon–Fri |
| Work Day Start | "Work Day Start" | Time picker | Yes | HH:MM | e.g. `08:30` |
| Work Day End | "Work Day End" | Time picker | Yes | HH:MM, must be after start | e.g. `17:30` |
| Privacy Mode | "Privacy Mode" | Toggle | No | Default: off | When on: monitoring data blurred by default for this tenant |
| Data Retention Period | "Data Retention Period (days)" | Number input | Yes | Min 30, max 3650 | How long activity data is retained before the retention sweep deletes it |
| Date Format | "Date Format" | Dropdown | Yes | `DD/MM/YYYY`, `MM/DD/YYYY`, `YYYY-MM-DD` | Affects display across the tenant UI |
| First Day of Week | "First Day of Week" | Dropdown (Mon / Sun) | Yes | Default: Monday | Controls calendar and week-based report boundaries |

**Save API:** `POST /admin/v1/configuration-templates`

```json
{
  "name": "Standard APAC",
  "description": "Default settings for APAC region tenants. Colombo timezone, LKR currency, Monday work week start.",
  "type": "configuration",
  "payload": {
    "timezone": "Asia/Colombo",
    "currency": "LKR",
    "work_week": ["monday", "tuesday", "wednesday", "thursday", "friday"],
    "work_day_start": "08:30",
    "work_day_end": "17:30",
    "privacy_mode": false,
    "data_retention_days": 365,
    "date_format": "DD/MM/YYYY",
    "first_day_of_week": "monday"
  }
}
```

**Response (201 Created):**
```json
{
  "template_id": "ctmpl-uuid",
  "name": "Standard APAC",
  "type": "configuration",
  "version": 1,
  "created_at": "2026-05-18T09:00:00Z"
}
```

**State written:** `configuration_templates` row with `type = 'configuration'`, `payload` JSON, `version = 1`, `is_active = true`. Audit log: `action = 'configuration_template.created'`.

---

### Edit Configuration Template

**API:** `PATCH /admin/v1/configuration-templates/{id}`

All payload fields are replaceable. Every successful PATCH increments `version`. Previous payload is not preserved separately — version number is the audit trail (full payload is logged to audit at time of change).

**What cannot change:** `type` - a configuration template cannot change from one template type to another.

---

### Duplicate Configuration Template

**Trigger:** "Duplicate" action on any template row.

Creates a new template pre-filled from the source, with name `{original} — Copy`. Operator edits name and fields before saving.

**API:** `POST /admin/v1/configuration-templates/{sourceId}/duplicate`

```json
{ "name": "Standard APAC — Copy" }
```

---

### Apply Configuration Template to Tenant

**Entry points:**
1. Configuration tab → row Actions → "Apply to Tenant"
2. Provisioning wizard → Step 4 → Configuration Template dropdown

**Apply flow:**

**Step 1: Select Tenant** (when entering from Template Manager, not wizard)
- Autocomplete search for tenant name/domain
- Shows: tenant name, plan, status
- Only active tenants shown

**Step 2: Preview**
- Shows the full payload fields that will be written to `tenant_settings`
- If `tenant_settings` already has values (tenant previously configured), shows diff: fields that will change are highlighted in amber; unchanged fields shown in gray

**Step 3: Confirm**

| Field | Label | Required |
|---|---|---|
| Reason | "Reason for applying" | No |

**API:** `POST /admin/v1/tenants/{tenantId}/configuration-templates/{templateId}/apply`

```json
{ "reason": "Initial provisioning — APAC standard settings." }
```

**Response (200 OK):**
```json
{
  "application_id": "ctapp-uuid",
  "tenant_id": "tenant-uuid",
  "template_id": "ctmpl-uuid",
  "template_version": 1,
  "fields_written": ["timezone", "currency", "work_week", "work_day_start", "work_day_end", "data_retention_days", "date_format", "first_day_of_week"],
  "fields_skipped": [],
  "applied_at": "2026-05-18T09:15:00Z"
}
```

**State written:**
- `tenant_settings` rows updated/inserted for each payload field, scoped to `tenant_id`
- `tenant_configuration_template_applications` row created with `tenant_id`, `configuration_template_id`, `template_type`, `applied_version`, immutable `applied_payload_json`, nullable `warnings_json`, `status = "applied"`, `applied_by_id`, and `applied_at`.
- Audit log: `action = 'configuration_template.applied'`, actor, tenant, template name, version

**Re-apply rule:** Applying a configuration template again updates tenant settings according to the current payload.
---

### Deactivate Configuration Template

**Trigger:** "Deactivate" action on a template row.

Deactivation sets `is_active = false`. The template no longer appears in provisioning wizard dropdowns. Tenants that previously applied it are unaffected — their `tenant_settings` values remain.

**Blocked if:** active tenant positions or assignment rows still reference this template in a way that would orphan resolution.
**API:** `DELETE /admin/v1/configuration-templates/{id}`

---

## Position Templates Tab

Manages reusable `position_template` packs that seed tenant departments and concrete positions during provisioning. Each position may link to one global role template. Monitoring, app allowlist, onboarding, and Time Off assignment are managed from their own template screens, not from the position form.

### Page Header

| Element | Value |
|---|---|
| Title | "Position Templates" |
| Subtitle | "Reusable position packs by employee count range and industry." |
| Create button | `+ New Position Template Pack` - requires `platform.templates.manage` |

### Position Template Packs Table

**API:** `GET /admin/v1/configuration-templates?type=position_template&search={q}`

| Column | Description | Sortable |
|---|---|---|
| Template Name | Display name | Yes |
| Employee Count Range | `1-10`, `11-50`, `51-100`, `101-500`, `501-1000`, `1001+` | Yes |
| Industry | Optional recommendation tag | Yes |
| Positions | Count of positions in the pack | No |
| Applied To | Count of tenants that have applied this template | Yes |
| Last Modified | Date | Yes |
| Actions | Edit, Clone, Apply to Tenant, Deactivate | - |

### Payload Shape

```json
{
  "type": "position_template",
  "payload": {
    "pack_name": "Small Software Company Positions",
    "employee_count_range_key": "101-500",
    "employee_count_min": 101,
    "employee_count_max": 500,
    "industry": "software",
    "positions": [
      {
        "position_key": "managing-director",
        "position_name": "Managing Director",
        "department_name": "Leadership",
        "reports_to_position_key": null,
        "linked_role_template_id": "uuid-of-tenant-owner-role-template"
      },
      {
        "position_key": "software-engineer",
        "position_name": "Software Engineer",
        "department_name": "Engineering",
        "reports_to_position_key": "engineering-manager",
        "linked_role_template_id": "uuid-of-employee-role-template"
      }
    ]
  }
}
```

### Validation

- At least one position is required.
- `employee_count_range_key` must be one of `1-10`, `11-50`, `51-100`, `101-500`, `501-1000`, `1001+`.
- `employee_count_min` and `employee_count_max` must match the selected range; `employee_count_max` is null for `1001+`.
- `position_key` values must be unique within the pack.
- `reports_to_position_key` must reference another position in the same pack or be null.
- Reports-to links must not create cycles.
- `linked_role_template_id` is optional and must reference an active global role template when present.

### Apply To Tenant

**API:** `POST /admin/v1/tenants/{tenantId}/configuration-templates/{templateId}/apply`

Apply creates tenant departments and positions. For each position with `linked_role_template_id`, the linked role template is materialized for the tenant. Role permissions are filtered by tenant module entitlements before the tenant role is created or linked.

During provisioning, the tenant's real `estimated_employee_count` maps to one employee count range. Example: `150` maps to `101-500`. The wizard suggests the active position template pack with the same range and closest industry match, and the operator can override it.

**Response warnings include:**
- Permissions excluded because the tenant is not entitled to the owning module.
- Positions skipped because a position with the same key already exists and `force_update = false`.
- Non-destructive updates only for positions that already have assigned employees.

---
## Time Off Policy Tab

Manages reusable `time_off_policy` type templates that seed Time Off configuration during provisioning.

### Page Header

| Element | Value |
|---|---|
| Title | "Time Off Policy Templates" |
| Subtitle | "Reusable Time Off type and policy presets for tenant provisioning." |
| Create button | `+ New Time Off Policy Template` — requires `platform.templates.manage` |

### Time Off Policy Templates Table

**API:** `GET /admin/v1/configuration-templates?type=time_off_policy&search={q}`

| Column | Description | Sortable |
|---|---|---|
| Template Name | Display name | Yes |
| Time Off Types | Count of Time Off types defined | No |
| Policies | Count of Time Off policies defined | No |
| Applied To | Count of tenants that have applied this template | Yes |
| Last Modified | Date | Yes |
| Actions | Edit, Duplicate, Deactivate | — |

---

### Create Time Off Policy Template — Full Field Specification

**Trigger:** `+ New Time Off Policy Template` button

A template defines one or more **Time Off types** and the **Time Off policy** that governs each type (accrual, entitlement, eligibility rules).

#### Section 1: Template Identity

| Field | Label | Type | Required | Validation |
|---|---|---|---|---|
| Template Name | "Template Name" | Text input | Yes | 2–80 chars, unique among active `time_off_policy` templates |
| Description | "Description" | Textarea | Yes | 10–300 chars |

#### Section 2: Time Off Type Builder

One collapsible card per Time Off type. Operator adds as many types as needed.

**Per Time Off Type — Identity fields:**

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| Time Off Type Name | "Time Off Type Name" | Text | Yes | e.g. "Annual Time Off", "Sick Time Off", "Casual Time Off", "Maternity Time Off" |
| Time Off Type Code | "Code" | Text (slug) | Yes | Unique within template, e.g. `annual`, `sick`, `casual` |
| Is Paid | "Paid Time Off" | Toggle | Yes | Default: on |
| Requires Medical Certificate | "Requires Medical Certificate" | Toggle | No | Shown only if `Is Paid = off` (sick/unpaid) |
| Requires Approval | "Requires Approval" | Toggle | Yes | Default: on |
| Applicable Gender | "Applicable To" | Dropdown: All / Male / Female | No | Default: All. Use for maternity/paternity time_off |
| Color | "Calendar Color" | Color picker | No | Used in Time Off calendar display |

**Per Time Off Type — Entitlement fields:**

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| Entitlement Amount | "Entitlement Amount" | Number | Yes | Amount entered before normalization |
| Entitlement Input Unit | "Entitlement Unit" | Dropdown | Yes | `days` or `hours`; day input is converted to hours during entitlement generation |
| Standard Day Hours | "Standard Day Hours" | Number | Required for day input | Fallback when no effective schedule exists |
| Max Consecutive Hours | "Max Consecutive Hours" | Number | No | If set: a single Time Off request cannot exceed this many hours |
| Min Notice Days | "Minimum Notice (days)" | Number | No | Minimum advance notice required when applying |
| Carry Forward | "Carry Forward Unused Balance" | Toggle | No | Default: off |
| Carry Forward Cap Hours | "Carry Forward Cap (hours)" | Number | No | Required if Carry Forward = on. Max hours that can roll to next policy period |
| Carry Forward Expiry | "Carried Forward Balance Expires After" | Duration | No | If set: carried-forward balance expires after the configured duration |

**Per Time Off Type — Accrual Policy:**

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| Accrual Type | "Accrual Type" | Dropdown | Yes | `upfront` (full entitlement granted at start of year) / `accrual` (earned incrementally) |
| Accrual Frequency | "Accrual Frequency" | Dropdown | Yes if accrual | Monthly / Quarterly / Bi-Annual |
| Accrual Amount | "Accrual Amount" | Number | Yes if accrual | Amount added per accrual cycle, interpreted by the entitlement input unit |
| Accrual Start From | "Start Accruing From" | Dropdown | No | `joining_date` / `probation_end` / `time_off_year_start` |

**Per Time Off Type - Eligibility Rules:**

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| Exclude During Probation | "Exclude During Probation Period" | Toggle | No | Default: off. When on: employees on probation cannot apply for this Time Off type |
| Min Service Days | "Minimum Service (days)" | Number | No | Employee must have been active for at least N days before they can apply |
| Assignment Scope | "Applies To" | Radio | Yes | `tenant`, `department`, or `position`. Determines where this Time Off policy applies |

**Visual layout per Time Off type card:**

```
▼ Annual Time Off                                              [Remove]
  ┌──────────────────────────────────────────────────────┐
  │ Code: annual   Paid: Yes   Approval: Required         │
  │ Entitlement: 21 days -> hours   Carry forward: 40 hours │
  │ Accrual: monthly by normalized hours   Start: joining_date │
  │ Probation: excluded   Min service: 90 days            │
  └──────────────────────────────────────────────────────┘

▼ Sick Time Off                                               [Remove]
  ┌──────────────────────────────────────────────────────┐
  │ Code: sick   Paid: Yes   Approval: Required           │
  │ Entitlement: 14 days -> hours   No carry forward       │
  │ Accrual: upfront                                      │
  │ Medical cert required after configured duration threshold │
  └──────────────────────────────────────────────────────┘

[+ Add Time Off Type]
```

**Save API:** `POST /admin/v1/configuration-templates`

```json
{
  "name": "Standard Time Off Pack — APAC",
  "description": "Standard Time Off types for APAC tenants: Annual, Sick, Casual, Maternity/Paternity.",
  "type": "time_off_policy",
  "payload": {
    "time_off_types": [
      {
        "name": "Annual Time Off",
        "code": "annual",
        "is_paid": true,
        "requires_approval": true,
        "applicable_gender": "all",

        "entitlement_minutes": 10080,
        "max_consecutive_minutes": null,
        "min_notice_days": 3,
        "carry_forward": true,
        "carry_forward_limit_minutes": 2400,
        "carry_forward_expiry": "P3M",
        "accrual_type": "accrual",
        "accrual_frequency": "monthly",
        "accrual_amount": 1.75,
        "accrual_start_from": "joining_date",
        "exclude_during_probation": true,
        "min_service_days": 90,
        "assignment_scope": "tenant"
      },
      {
        "name": "Sick Time Off",
        "code": "sick",
        "is_paid": true,
        "requires_approval": true,
        "requires_medical_certificate": true,
        "applicable_gender": "all",

        "entitlement_minutes": 6720,
        "carry_forward": false,
        "accrual_type": "upfront",
        "exclude_during_probation": false,
        "min_service_days": 0,
        "assignment_scope": "tenant"
      },
      {
        "name": "Casual Time Off",
        "code": "casual",
        "is_paid": true,
        "requires_approval": true,
        "applicable_gender": "all",

        "entitlement_minutes": 3360,
        "max_consecutive_minutes": 1440,
        "carry_forward": false,
        "accrual_type": "upfront",
        "exclude_during_probation": true,
        "min_service_days": 0,
        "assignment_scope": "tenant"
      }
    ]
  }
}
```

**Response (201 Created):**
```json
{
  "template_id": "ctmpl-uuid",
  "name": "Standard Time Off Pack — APAC",
  "type": "time_off_policy",
  "time_off_type_count": 3,
  "version": 1,
  "created_at": "2026-05-18T09:00:00Z"
}
```

**Validation — server-side:**
- At least one Time Off type required
- Time Off type codes must be unique within the template
- `carry_forward_limit_minutes` required if `carry_forward = true`
- `accrual_frequency` and `accrual_amount` required if `accrual_type = 'accrual'`
- `entitlement_minutes` must be a positive integer
- `carry_forward_limit_minutes` cannot exceed `entitlement_minutes` unless the policy intentionally allows over-carry
- `applicable_gender` must be `all`, `male`, or `female`

**State written:** `configuration_templates` row with `type = 'time_off_policy'`, `payload` JSON, `version = 1`. Audit log: `action = 'time_off_policy_template.created'`.

---

### Edit Time Off Policy Template

**API:** `PATCH /admin/v1/configuration-templates/{id}`

Full payload replacement. Every successful PATCH increments `version`. Editing a template does NOT update previously applied tenant Time Off types/policies — re-apply is required.

---

### Apply Time Off Policy Template to Tenant

**Entry points:**
1. Time Off Policy tab → row Actions → "Apply to Tenant"
2. Provisioning wizard → Step 4 → Time Off Policy Template dropdown

**Apply flow:**

**Step 1: Select Tenant** (when entering from Template Manager)
- Shows tenant name, plan, status
- If Time Off types already exist for this tenant: warning — "This tenant already has {N} Time Off types. Time Off types with matching codes will be skipped; new types will be added."
- If `assignment_scope` is `department` or `position`: checks that the selected departments or positions exist or were created by the selected position template pack.

**Step 2: Preview**
- Lists all Time Off types with their key entitlement fields
- Shows whether each Time Off type applies to the full tenant, selected departments, or selected positions.

**Step 3: Confirm**

**API:** `POST /admin/v1/tenants/{tenantId}/configuration-templates/{templateId}/apply`

```json
{ "reason": "Initial provisioning — standard APAC Time Off pack." }
```

**Response (200 OK):**
```json
{
  "application_id": "ctapp-uuid",
  "time_off_types_created": 3,
  "time_off_types_skipped": 0,
  "skipped_codes": [],
  "policies_created": 3,
  "assignment_warnings": [],
  "applied_at": "2026-05-18T09:15:00Z"
}
```

**State written:**
- `time_off_types` rows created scoped to `tenant_id` for each Time Off type in payload (skip if `code` already exists for tenant)
- `time_off_policies` rows created for each Time Off type: entitlement + accrual rules persisted; assignment rows target tenant, departments, or positions
- `tenant_configuration_template_applications` row created
- Audit log: `action = 'time_off_policy_template.applied'`, Time Off types count, skipped count

**Re-apply rule:** Applying the same Time Off policy template again upserts Time Off types and policies by code, and updates assignment rows according to the current payload.
---

### Deactivate Time Off Policy Template

Deactivation sets `is_active = false`. Template no longer appears in provisioning wizard dropdowns. Existing tenant Time Off types and policies are unaffected.

**API:** `DELETE /admin/v1/configuration-templates/{id}`

---

## APIs — Full Catalog

### Role Template APIs

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/role-templates` | List templates | `platform.templates.read` |
| POST | `/admin/v1/role-templates` | Create template | `platform.templates.manage` |
| GET | `/admin/v1/role-templates/{id}` | Template detail with permissions | `platform.templates.read` |
| PATCH | `/admin/v1/role-templates/{id}` | Update template (creates new version) | `platform.templates.manage` |
| POST | `/admin/v1/role-templates/{id}/clone` | Clone system or custom template | `platform.templates.manage` |
| DELETE | `/admin/v1/role-templates/{id}` | Deactivate template | `platform.templates.manage` |
| GET | `/admin/v1/tenants/{id}/permissions/catalog` | Module-filtered permission catalog for this tenant | `platform.tenants.read` |
| GET | `/admin/v1/tenants/{id}/roles` | All materialized roles for this tenant | `platform.tenants.read` |
| POST | `/admin/v1/tenants/{id}/roles` | Create tenant-specific role | `platform.tenants.manage` |
| PUT | `/admin/v1/tenants/{id}/roles/{roleId}/permissions` | Replace role permission set | `platform.tenants.manage` |
| DELETE | `/admin/v1/tenants/{id}/roles/{roleId}` | Delete tenant role | `platform.tenants.manage` |
| POST | `/admin/v1/tenants/{id}/role-templates/{templateId}/apply` | Apply role template to tenant | `platform.tenants.manage` |
| GET | `/admin/v1/tenants/{id}/role-template-applications` | History of template applications | `platform.tenants.read` |

### Configuration Template APIs

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/configuration-templates` | List templates (filter by `?type=`) | `platform.templates.read` |
| POST | `/admin/v1/configuration-templates` | Create template | `platform.templates.manage` |
| GET | `/admin/v1/configuration-templates/{id}` | Template detail | `platform.templates.read` |
| PATCH | `/admin/v1/configuration-templates/{id}` | Update template | `platform.templates.manage` |
| DELETE | `/admin/v1/configuration-templates/{id}` | Deactivate template | `platform.templates.manage` |
| POST | `/admin/v1/tenants/{id}/configuration-templates/{templateId}/apply` | Apply template to tenant | `platform.tenants.manage` |
| GET | `/admin/v1/tenants/{id}/configuration-template-applications` | History of configuration template applications | `platform.tenants.read` |

---

## Error Taxonomy

| HTTP | Code | Condition |
|---|---|---|
| 404 | `template_not_found` | Template ID does not exist |
| 409 | `template_name_taken` | Active template with same name exists |
| 409 | `role_name_duplicate` | Role with this name exists and `on_duplicate` not specified |
| 422 | `unknown_permission_codes` | One or more codes not in permissions table — lists the invalid codes |
| 422 | `permissions_not_in_module_scope` | Codes owned by modules not in template's module_scope |
| 422 | `all_permissions_excluded` | Every permission in template is excluded by tenant entitlement filter — nothing to apply |
| 422 | `system_template_not_editable` | Attempt to PATCH a system template directly — must clone |
| 422 | `invalid_template_type` | `type` value not one of the supported template types: `configuration`, `position_template`, `time_off_policy`, `monitoring_policy`, `app_allowlist`, `onboarding`, `data_import_mapping` |
| 403 | `permission_denied` | Missing required platform permission |










