# Template Manager — End-to-End Logic

## Purpose

Template Manager is the single operator-facing module for all reusable provisioning and configuration presets. It is organized into four tabs. This document covers the full end-to-end logic for each tab.

**Route:** `/platform/templates`
**Permission:** `platform.role_templates.read`

> **Out of scope:** App Allowlist templates and Monitoring Policy templates are managed by the Device Management / Agent Version Manager operator role — they are monitoring agent policy artifacts, not provisioning presets.

---

## Screen Layout

Left tab navigation:
- Role Templates (default)
- Configuration
- Job Family
- Leave Policy

---

## Role Templates Tab

### Page Header

| Element | Value |
|---|---|
| Title | "Template Manager" |
| Subtitle | "Manage reusable role blueprints for tenant provisioning." |
| Create Template button | `+ Create Template` — requires `platform.role_templates.manage` |

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
| Template Name | "Template Name" | Text input | Yes | 2–80 chars, unique among active templates | e.g. "HR Admin", "Workforce Supervisor", "Leave Manager" |
| Description | "Description" | Textarea | Yes | 10–300 chars | Explains who this role is for and what they can do |
| Is Global Template | "Save as Reusable Global Template" | Toggle | Yes | Default: On | Off = this template is created only for a specific tenant (only available when creating from the Apply to Tenant screen) |

### Section 2: Module Scope Filter

**This section determines the permission boundary.** Permissions are owned by modules. The operator first selects which modules this template draws permissions from — only permissions owned by selected modules appear in the permission picker below.

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| Module Scope | "Include Permissions From Modules" | Multi-select from module catalog (Phase 1 modules only) | Yes | At least one module required. Foundation modules (`auth`, `configuration`, `roles`, `notifications`, `org`) are always included and cannot be deselected — their permissions appear regardless. |

**Foundation module permissions are always shown** in the permission picker because they apply to every tenant. Additional permissions appear only for selected modules.

**Important rule:** The module scope here is the template's design scope — it limits which permissions are shown when building the template. When the template is applied to a specific tenant, the system ADDITIONALLY filters to only permissions from modules the tenant is entitled to. A template scoped to `leave + monitoring` applied to a tenant with only `leave` will only grant leave permissions — monitoring permissions are silently skipped.

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

▼ Leave Management (leave)             [Select All] [Clear]
  ☑ leave:read              View leave requests
  ☑ leave:apply             Submit leave requests
  ☑ leave:approve           Approve/reject leave
  ☐ leave:policy:manage     Edit leave policies (usually admin only)
  ...
```

**Each permission row shows:**
- Checkbox — selected/unselected
- Permission code — machine-readable, e.g. `leave:approve`
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
  "description": "Full HR management access. Can manage all employee records, org structure, leave, and HR documents. Cannot access payroll or workforce monitoring.",
  "is_global": true,
  "module_scope": ["core_hr", "leave", "org_structure", "calendar"],
  "permission_codes": [
    "employees:read",
    "employees:manage",
    "org:read",
    "org:manage",
    "leave:read",
    "leave:apply",
    "leave:approve",
    "leave:policy:manage",
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

**State written:** `role_templates` row created with `version = 1`, `is_system = false`. `role_template_permissions` rows created for each permission code. Audit log: `action = 'role_template.created'`.

---

## Edit Template — Versioning Behaviour

Editing a template creates a new version. Previous version is preserved for audit.

**API:** `PATCH /admin/v1/role-templates/{id}`

**What can change:** name, description, permission_codes, module_scope.
**What cannot change:** `is_system` (system templates cannot become custom), `is_global` after first tenant application.

**Version increment rule:** every successful PATCH increments `role_templates.version`. The `role_template_permissions` rows are replaced (delete all, re-insert new set).

**Effect on tenants that previously applied this template:**
- Applying a template materializes **independent** tenant-scoped roles in the Auth module. Those materialized roles are NOT updated when the template is edited.
- The template version at time of application is recorded in `tenant_role_template_applications.template_version`.
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
2. Tenant Console → Tenant Detail → Subscriptions tab → "Manage Roles" → Apply Template

### Permission Boundary Filtering

Before showing the permission picker or confirming an apply, the system filters the template's permissions against the tenant's entitled modules:

```
template.permission_codes
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

**API:** `POST /admin/v1/tenants/{tenantId}/role-templates/{templateId}/apply`

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
- `tenant_role_template_applications` row created: `(tenant_id, template_id, template_version, role_id, applied_by_id, applied_at, permissions_excluded_json)`
- Audit log: `action = 'role_template.applied'`, actor, tenant, template, role_name, permissions_excluded count

---

## Create Tenant-Specific Role (Without Template)

When a tenant needs a role that is unique to them and should NOT become a global template, operators create it directly.

**Entry:** Apply to Tenant tab → "Create Custom Role" option instead of selecting a template.

**Fields:** Same as Create Template but `is_global = false` and forced to the selected tenant.

**API:** `POST /admin/v1/tenants/{tenantId}/roles`

```json
{
  "name": "Regional HR Manager — APAC",
  "description": "Custom role for TechNova's APAC HR team with leave approval for APAC org units only.",
  "permission_codes": ["leave:approve", "employees:read", "org:read"]
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
| GET | `/admin/v1/role-templates` | List templates | `platform.role_templates.read` |
| POST | `/admin/v1/role-templates` | Create template | `platform.role_templates.manage` |
| GET | `/admin/v1/role-templates/{id}` | Template detail with permissions | `platform.role_templates.read` |
| PATCH | `/admin/v1/role-templates/{id}` | Update template (creates new version) | `platform.role_templates.manage` |
| POST | `/admin/v1/role-templates/{id}/clone` | Clone system or custom template | `platform.role_templates.manage` |
| DELETE | `/admin/v1/role-templates/{id}` | Deactivate template | `platform.role_templates.manage` |
| GET | `/admin/v1/tenants/{id}/permissions/catalog` | Module-filtered permission catalog for this tenant | `platform.tenants.read` |
| GET | `/admin/v1/tenants/{id}/roles` | All materialized roles for this tenant | `platform.tenants.read` |
| POST | `/admin/v1/tenants/{id}/roles` | Create tenant-specific role | `platform.tenants.manage` |
| PUT | `/admin/v1/tenants/{id}/roles/{roleId}/permissions` | Replace role permission set | `platform.tenants.manage` |
| DELETE | `/admin/v1/tenants/{id}/roles/{roleId}` | Delete tenant role | `platform.tenants.manage` |
| POST | `/admin/v1/tenants/{id}/role-templates/{templateId}/apply` | Apply template to tenant | `platform.tenants.manage` |
| GET | `/admin/v1/tenants/{id}/role-template-applications` | History of template applications | `platform.tenants.read` |

---

## Configuration, Job Family, and Leave Policy Tabs

> Full end-to-end logic for these three tabs — field specs, payload schemas, apply flows, reapply rules, module entitlement guards, and API catalog — is documented in the authoritative spec:
> **[[developer-platform/modules/configuration-template-manager/end-to-end-logic|Configuration Template Manager End-to-End Logic]]**

The sections below are a summary only.

## Configuration Tab

Manages reusable `configuration` type templates that pre-fill `tenant_settings` during provisioning.

### Page Header

| Element | Value |
|---|---|
| Title | "Configuration Templates" |
| Subtitle | "Reusable tenant settings presets applied during provisioning." |
| Create button | `+ New Configuration Template` — requires `platform.configuration_templates.manage` |

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

**What cannot change:** `type` — a configuration template cannot become a job_family template.

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
- `tenant_configuration_template_applications` row created: `(tenant_id, template_id, template_version, type, applied_by_id, applied_at, reason)`
- Audit log: `action = 'configuration_template.applied'`, actor, tenant, template name, version

**Re-apply rule:** A configuration template can be re-applied to the same tenant at any time — it overwrites `tenant_settings` fields with the template's current payload. No idempotency conflict check; each apply creates a new `tenant_configuration_template_applications` row.

---

### Deactivate Configuration Template

**Trigger:** "Deactivate" action on a template row.

Deactivation sets `is_active = false`. The template no longer appears in provisioning wizard dropdowns. Tenants that previously applied it are unaffected — their `tenant_settings` values remain.

**Blocked if:** The template is referenced in any in-progress provisioning wizard (`wizard_state.step4.configuration_template_id`). Operator must either complete or cancel those wizards first.

**API:** `DELETE /admin/v1/configuration-templates/{id}`

---

## Job Family Tab

Manages reusable `job_family` type templates that seed org hierarchy during provisioning.

### Page Header

| Element | Value |
|---|---|
| Title | "Job Family Templates" |
| Subtitle | "Reusable org hierarchy presets — job families, levels, and titles." |
| Create button | `+ New Job Family Template` — requires `platform.configuration_templates.manage` |

### Job Family Templates Table

**API:** `GET /admin/v1/configuration-templates?type=job_family&search={q}`

| Column | Description | Sortable |
|---|---|---|
| Template Name | Display name | Yes |
| Families | Count of job families defined in this template | No |
| Levels | Total count of job levels across all families | No |
| Pending Role Links | Count of job levels with `pending_role_template_id` across all tenants that applied this template | No |
| Applied To | Count of tenants that have applied this template | Yes |
| Last Modified | Date | Yes |
| Actions | Edit, Duplicate, Deactivate | — |

---

### Create Job Family Template — Full Field Specification

**Trigger:** `+ New Job Family Template` button

A template is a named container holding one or more **job families**. Each family holds one or more **job levels** in ranked order.

#### Section 1: Template Identity

| Field | Label | Type | Required | Validation |
|---|---|---|---|---|
| Template Name | "Template Name" | Text input | Yes | 2–80 chars, unique among active `job_family` templates |
| Description | "Description" | Textarea | Yes | 10–300 chars |

#### Section 2: Job Family Builder

The operator builds families interactively. UI shows a collapsible card per family.

**Per Family:**

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| Family Name | "Family Name" | Text | Yes | e.g. "Engineering", "HR", "Finance", "Operations" |
| Family Code | "Family Code" | Text | Yes | Slug, e.g. `engineering` — must be unique within the template |

**Per Level within family** (ordered list, drag to reorder):

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| Level Name | "Level Name" | Text | Yes | e.g. "Junior Engineer", "Mid Engineer", "Senior Engineer" |
| Rank | Auto-assigned | Integer | — | 1 = lowest, increments per level in display order. Operator reorders by dragging; ranks update automatically |
| Level Code | "Level Code" | Text | Yes | Slug, unique within the family, e.g. `junior`, `mid`, `senior` |
| Default Role Template | "Default Role Template" | Dropdown — global role templates | No | If set: when this job family template is applied to a tenant, the system tries to link this level to the named materialized role. If the role doesn't exist yet for the tenant, stored as `pending_role_template_id` until resolved |

**Visual layout:**

```
▼ Engineering                                       [+ Add Level] [Remove Family]
  ┌─────────────────────────────────────────────────────────────────┐
  │ ≡  Junior Engineer   rank: 1   code: junior   Role: IC Contributor  │
  │ ≡  Mid Engineer      rank: 2   code: mid       Role: IC Contributor  │
  │ ≡  Senior Engineer   rank: 3   code: senior    Role: Senior IC       │
  │ ≡  Staff Engineer    rank: 4   code: staff     Role: Lead            │
  └─────────────────────────────────────────────────────────────────┘

▼ HR                                                [+ Add Level] [Remove Family]
  ┌─────────────────────────────────────────────────────────────────┐
  │ ≡  HR Coordinator    rank: 1   code: coordinator  Role: HR Staff     │
  │ ≡  HR Manager        rank: 2   code: manager      Role: HR Manager   │
  └─────────────────────────────────────────────────────────────────┘

[+ Add Family]
```

**Save API:** `POST /admin/v1/configuration-templates`

```json
{
  "name": "Standard 3-Tier Org",
  "description": "Standard org hierarchy for mid-size companies. 3 families (Engineering, HR, Operations) with 3-4 levels each.",
  "type": "job_family",
  "payload": {
    "families": [
      {
        "name": "Engineering",
        "code": "engineering",
        "levels": [
          { "name": "Junior Engineer", "code": "junior", "rank": 1, "default_role_template_name": "IC Contributor" },
          { "name": "Mid Engineer", "code": "mid", "rank": 2, "default_role_template_name": "IC Contributor" },
          { "name": "Senior Engineer", "code": "senior", "rank": 3, "default_role_template_name": "Senior IC" },
          { "name": "Staff Engineer", "code": "staff", "rank": 4, "default_role_template_name": "Lead" }
        ]
      },
      {
        "name": "HR",
        "code": "hr",
        "levels": [
          { "name": "HR Coordinator", "code": "coordinator", "rank": 1, "default_role_template_name": "HR Staff" },
          { "name": "HR Manager", "code": "manager", "rank": 2, "default_role_template_name": "HR Manager" }
        ]
      }
    ]
  }
}
```

**Response (201 Created):**
```json
{
  "template_id": "ctmpl-uuid",
  "name": "Standard 3-Tier Org",
  "type": "job_family",
  "family_count": 2,
  "level_count": 6,
  "version": 1,
  "created_at": "2026-05-18T09:00:00Z"
}
```

**Validation — server-side:**
- At least one family required
- At least one level per family required
- Family codes must be unique within the template
- Level codes must be unique within their family
- Ranks must be positive integers; duplicate ranks within a family → HTTP 422
- `default_role_template_name` values are not validated at create time — they are resolved lazily at apply time

**State written:** `configuration_templates` row with `type = 'job_family'`, `payload` JSON, `version = 1`. Audit log: `action = 'job_family_template.created'`.

---

### Edit Job Family Template

**API:** `PATCH /admin/v1/configuration-templates/{id}`

Full payload replacement — operator edits the family/level structure and saves. Every successful PATCH increments `version`.

**Blocked if:** Any tenant has applied this template AND `deactivate_blocked_if_pending_links = true` is set — because editing levels would invalidate pending role links. In this case, the operator must first resolve all pending role links on tenant job levels before editing.

Re-applying after an edit overwrites the tenant's job families and levels with the new payload.

---

### Apply Job Family Template to Tenant

**Entry points:**
1. Job Family tab → row Actions → "Apply to Tenant"
2. Provisioning wizard → Step 4 → Job Family Template multi-select

**Apply flow:**

**Step 1: Select Tenant** (when entering from Template Manager)
- Shows tenant name, plan, status, and whether job families already exist for this tenant
- If job families already exist: warning shown — "This tenant already has {N} job families. Applying will add families from this template; existing families are not removed."

**Step 2: Preview**
- Lists all families and levels that will be created
- For each level: shows the `default_role_template_name` and whether it will resolve immediately (green check — role exists for this tenant) or remain pending (amber — role not yet applied)

**Step 3: Confirm**

**API:** `POST /admin/v1/tenants/{tenantId}/configuration-templates/{templateId}/apply`

```json
{ "reason": "Initial provisioning — standard 3-tier org structure." }
```

**Response (200 OK):**
```json
{
  "application_id": "ctapp-uuid",
  "families_created": 2,
  "levels_created": 6,
  "role_links_resolved": 3,
  "role_links_pending": 3,
  "pending_details": [
    { "level": "Senior Engineer", "pending_role_template_name": "Senior IC" },
    { "level": "Staff Engineer", "pending_role_template_name": "Lead" },
    { "level": "HR Manager", "pending_role_template_name": "HR Manager" }
  ],
  "applied_at": "2026-05-18T09:15:00Z"
}
```

**State written:**
- `job_families` rows created for tenant (scoped to `tenant_id`)
- `job_levels` rows created; for each: if a `roles` row named `default_role_template_name` exists for this tenant → `default_role_id` set; otherwise `pending_role_template_id` set to the named global role template's ID
- `tenant_configuration_template_applications` row created
- Audit log: `action = 'job_family_template.applied'`, families/levels count, pending links count

**Pending role link resolution:** When the operator later applies a Role Template to this tenant (via Role Templates tab), the `ApplyRoleTemplateCommandHandler` scans `job_levels` for rows with `pending_role_template_id = this_template_id` and sets `default_role_id` on each, clearing the pending flag.

**Re-apply rule:** Applying the same job family template again to a tenant that already has those families is additive — families with the same `code` are skipped (not duplicated); new families/levels in the template are created. A warning is returned listing which families were skipped.

---

### Deactivate Job Family Template

**Blocked if:** Any active tenant has `job_levels.pending_role_template_id` referencing a role template that is linked to this job family template. Operator must resolve or nullify those pending links first.

**API:** `DELETE /admin/v1/configuration-templates/{id}`

Deactivation sets `is_active = false`. Existing tenant job families/levels are unaffected.

---

## Leave Policy Tab

Manages reusable `leave_policy` type templates that seed leave configuration during provisioning.

### Page Header

| Element | Value |
|---|---|
| Title | "Leave Policy Templates" |
| Subtitle | "Reusable leave type and policy presets for tenant provisioning." |
| Create button | `+ New Leave Policy Template` — requires `platform.configuration_templates.manage` |

### Leave Policy Templates Table

**API:** `GET /admin/v1/configuration-templates?type=leave_policy&search={q}`

| Column | Description | Sortable |
|---|---|---|
| Template Name | Display name | Yes |
| Leave Types | Count of leave types defined | No |
| Policies | Count of leave policies defined | No |
| Applied To | Count of tenants that have applied this template | Yes |
| Last Modified | Date | Yes |
| Actions | Edit, Duplicate, Deactivate | — |

---

### Create Leave Policy Template — Full Field Specification

**Trigger:** `+ New Leave Policy Template` button

A template defines one or more **leave types** and the **leave policy** that governs each type (accrual, entitlement, eligibility rules).

#### Section 1: Template Identity

| Field | Label | Type | Required | Validation |
|---|---|---|---|---|
| Template Name | "Template Name" | Text input | Yes | 2–80 chars, unique among active `leave_policy` templates |
| Description | "Description" | Textarea | Yes | 10–300 chars |

#### Section 2: Leave Type Builder

One collapsible card per leave type. Operator adds as many types as needed.

**Per Leave Type — Identity fields:**

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| Leave Type Name | "Leave Type Name" | Text | Yes | e.g. "Annual Leave", "Sick Leave", "Casual Leave", "Maternity Leave" |
| Leave Type Code | "Code" | Text (slug) | Yes | Unique within template, e.g. `annual`, `sick`, `casual` |
| Is Paid | "Paid Leave" | Toggle | Yes | Default: on |
| Requires Medical Certificate | "Requires Medical Certificate" | Toggle | No | Shown only if `Is Paid = off` (sick/unpaid) |
| Requires Approval | "Requires Approval" | Toggle | Yes | Default: on |
| Applicable Gender | "Applicable To" | Dropdown: All / Male / Female | No | Default: All. Use for maternity/paternity leave |
| Color | "Calendar Color" | Color picker | No | Used in leave calendar display |

**Per Leave Type — Entitlement fields:**

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| Max Days Per Year | "Max Days Per Year" | Number | Yes | Total entitlement per leave year |
| Max Consecutive Days | "Max Consecutive Days" | Number | No | If set: a single leave request cannot exceed this many days |
| Min Notice Days | "Minimum Notice (days)" | Number | No | Minimum advance notice required when applying |
| Carry Forward | "Carry Forward Unused Balance" | Toggle | No | Default: off |
| Carry Forward Cap | "Carry Forward Cap (days)" | Number | No | Required if Carry Forward = on. Max days that can roll to next year |
| Carry Forward Expiry (months) | "Carried Forward Balance Expires After (months)" | Number | No | If set: carried-forward balance expires N months into the new leave year |

**Per Leave Type — Accrual Policy:**

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| Accrual Type | "Accrual Type" | Dropdown | Yes | `upfront` (full entitlement granted at start of year) / `accrual` (earned incrementally) |
| Accrual Frequency | "Accrual Frequency" | Dropdown | Yes if accrual | Monthly / Quarterly / Bi-Annual |
| Accrual Amount | "Accrual Amount (days)" | Number | Yes if accrual | Days added per accrual cycle |
| Accrual Start From | "Start Accruing From" | Dropdown | No | `joining_date` / `probation_end` / `leave_year_start` |

**Per Leave Type — Eligibility Rules:**

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| Exclude During Probation | "Exclude During Probation Period" | Toggle | No | Default: off. When on: employees on probation cannot apply for this leave type |
| Min Service Days | "Minimum Service (days)" | Number | No | Employee must have been active for at least N days before they can apply |
| Eligible Min Job Level Rank | "Eligible From Job Level Rank" | Number | No | If set: only employees at or above this job level rank are eligible. Resolved against tenant's job levels at apply time |

**Visual layout per leave type card:**

```
▼ Annual Leave                                              [Remove]
  ┌──────────────────────────────────────────────────────┐
  │ Code: annual   Paid: Yes   Approval: Required         │
  │ Max 21 days/year   Carry forward: up to 5 days        │
  │ Accrual: monthly 1.75 days   Start: joining_date      │
  │ Probation: excluded   Min service: 90 days            │
  └──────────────────────────────────────────────────────┘

▼ Sick Leave                                               [Remove]
  ┌──────────────────────────────────────────────────────┐
  │ Code: sick   Paid: Yes   Approval: Required           │
  │ Max 14 days/year   No carry forward                   │
  │ Accrual: upfront                                      │
  │ Medical cert required after 3 consecutive days        │
  └──────────────────────────────────────────────────────┘

[+ Add Leave Type]
```

**Save API:** `POST /admin/v1/configuration-templates`

```json
{
  "name": "Standard Leave Pack — APAC",
  "description": "Standard leave types for APAC tenants: Annual, Sick, Casual, Maternity/Paternity.",
  "type": "leave_policy",
  "payload": {
    "leave_types": [
      {
        "name": "Annual Leave",
        "code": "annual",
        "is_paid": true,
        "requires_approval": true,
        "applicable_gender": "all",
        "max_days_per_year": 21,
        "max_consecutive_days": null,
        "min_notice_days": 3,
        "carry_forward": true,
        "carry_forward_cap": 5,
        "carry_forward_expiry_months": 3,
        "accrual_type": "accrual",
        "accrual_frequency": "monthly",
        "accrual_amount": 1.75,
        "accrual_start_from": "joining_date",
        "exclude_during_probation": true,
        "min_service_days": 90,
        "eligible_min_job_level_rank": null
      },
      {
        "name": "Sick Leave",
        "code": "sick",
        "is_paid": true,
        "requires_approval": true,
        "requires_medical_certificate": true,
        "applicable_gender": "all",
        "max_days_per_year": 14,
        "carry_forward": false,
        "accrual_type": "upfront",
        "exclude_during_probation": false,
        "min_service_days": 0,
        "eligible_min_job_level_rank": null
      },
      {
        "name": "Casual Leave",
        "code": "casual",
        "is_paid": true,
        "requires_approval": true,
        "applicable_gender": "all",
        "max_days_per_year": 7,
        "max_consecutive_days": 3,
        "carry_forward": false,
        "accrual_type": "upfront",
        "exclude_during_probation": true,
        "min_service_days": 0
      }
    ]
  }
}
```

**Response (201 Created):**
```json
{
  "template_id": "ctmpl-uuid",
  "name": "Standard Leave Pack — APAC",
  "type": "leave_policy",
  "leave_type_count": 3,
  "version": 1,
  "created_at": "2026-05-18T09:00:00Z"
}
```

**Validation — server-side:**
- At least one leave type required
- Leave type codes must be unique within the template
- `carry_forward_cap` required if `carry_forward = true`
- `accrual_frequency` and `accrual_amount` required if `accrual_type = 'accrual'`
- `max_days_per_year` must be ≥ `carry_forward_cap` if carry forward is on
- `applicable_gender` must be `all`, `male`, or `female`

**State written:** `configuration_templates` row with `type = 'leave_policy'`, `payload` JSON, `version = 1`. Audit log: `action = 'leave_policy_template.created'`.

---

### Edit Leave Policy Template

**API:** `PATCH /admin/v1/configuration-templates/{id}`

Full payload replacement. Every successful PATCH increments `version`. Editing a template does NOT update previously applied tenant leave types/policies — re-apply is required.

---

### Apply Leave Policy Template to Tenant

**Entry points:**
1. Leave Policy tab → row Actions → "Apply to Tenant"
2. Provisioning wizard → Step 4 → Leave Policy Template dropdown

**Apply flow:**

**Step 1: Select Tenant** (when entering from Template Manager)
- Shows tenant name, plan, status
- If leave types already exist for this tenant: warning — "This tenant already has {N} leave types. Leave types with matching codes will be skipped; new types will be added."
- If `eligible_min_job_level_rank` is set on any leave type: checks whether tenant has job levels. If not: info notice — "Job level eligibility rules will be stored but cannot be resolved until job families are applied."

**Step 2: Preview**
- Lists all leave types with their key entitlement fields
- For types with `eligible_min_job_level_rank` set: shows which job level rank the rule maps to (if job families exist for tenant) or shows "pending job level resolution" (amber)

**Step 3: Confirm**

**API:** `POST /admin/v1/tenants/{tenantId}/configuration-templates/{templateId}/apply`

```json
{ "reason": "Initial provisioning — standard APAC leave pack." }
```

**Response (200 OK):**
```json
{
  "application_id": "ctapp-uuid",
  "leave_types_created": 3,
  "leave_types_skipped": 0,
  "skipped_codes": [],
  "policies_created": 3,
  "job_level_rank_warnings": [],
  "applied_at": "2026-05-18T09:15:00Z"
}
```

**State written:**
- `leave_types` rows created scoped to `tenant_id` for each leave type in payload (skip if `code` already exists for tenant)
- `leave_policies` rows created for each leave type: entitlement + accrual rules persisted; `eligible_min_job_level_rank` stored as-is (resolved by Leave module at request time against live job levels)
- `tenant_configuration_template_applications` row created
- Audit log: `action = 'leave_policy_template.applied'`, leave types count, skipped count

**Re-apply rule:** Applying the same template again is additive — leave types with matching `code` are skipped (not overwritten); new types in the template are created. To update existing leave type settings, the operator must edit the tenant's leave types directly via Tenant Console → Leave Management tab.

---

### Deactivate Leave Policy Template

Deactivation sets `is_active = false`. Template no longer appears in provisioning wizard dropdowns. Existing tenant leave types and policies are unaffected.

**API:** `DELETE /admin/v1/configuration-templates/{id}`

---

## APIs — Full Catalog

### Role Template APIs

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/role-templates` | List templates | `platform.role_templates.read` |
| POST | `/admin/v1/role-templates` | Create template | `platform.role_templates.manage` |
| GET | `/admin/v1/role-templates/{id}` | Template detail with permissions | `platform.role_templates.read` |
| PATCH | `/admin/v1/role-templates/{id}` | Update template (creates new version) | `platform.role_templates.manage` |
| POST | `/admin/v1/role-templates/{id}/clone` | Clone system or custom template | `platform.role_templates.manage` |
| DELETE | `/admin/v1/role-templates/{id}` | Deactivate template | `platform.role_templates.manage` |
| GET | `/admin/v1/tenants/{id}/permissions/catalog` | Module-filtered permission catalog for this tenant | `platform.tenants.read` |
| GET | `/admin/v1/tenants/{id}/roles` | All materialized roles for this tenant | `platform.tenants.read` |
| POST | `/admin/v1/tenants/{id}/roles` | Create tenant-specific role | `platform.tenants.manage` |
| PUT | `/admin/v1/tenants/{id}/roles/{roleId}/permissions` | Replace role permission set | `platform.tenants.manage` |
| DELETE | `/admin/v1/tenants/{id}/roles/{roleId}` | Delete tenant role | `platform.tenants.manage` |
| POST | `/admin/v1/tenants/{id}/role-templates/{templateId}/apply` | Apply template to tenant | `platform.tenants.manage` |
| GET | `/admin/v1/tenants/{id}/role-template-applications` | History of template applications | `platform.tenants.read` |

### Configuration Template APIs

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/configuration-templates` | List templates (filter by `?type=`) | `platform.configuration_templates.read` |
| POST | `/admin/v1/configuration-templates` | Create template | `platform.configuration_templates.manage` |
| GET | `/admin/v1/configuration-templates/{id}` | Template detail | `platform.configuration_templates.read` |
| PATCH | `/admin/v1/configuration-templates/{id}` | Update template | `platform.configuration_templates.manage` |
| DELETE | `/admin/v1/configuration-templates/{id}` | Deactivate template | `platform.configuration_templates.manage` |
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
| 422 | `invalid_template_type` | `type` value not one of: `configuration`, `job_family`, `leave_policy` |
| 403 | `permission_denied` | Missing required platform permission |
