# Configuration Template Manager — End-to-End Logic

**Module:** Developer Platform → Configuration Template Manager
**Phase:** Phase 1

---

## Purpose

Full field specifications, payload schemas, apply behaviour, reapply rules, and API catalog for the Configuration Template Manager. Read [[developer-platform/modules/configuration-template-manager/overview|overview.md]] first for orientation.

---

## Screen Layout

```
Developer Platform
└── Template Manager  (/platform/templates)
    ├── Role Templates     ← Role Template Manager (separate module)
    ├── Configuration      ← This module
    ├── Job Family         ← This module
    └── Leave Policy       ← This module
        (each tab: Template Library → list + create + template detail)
```

> **App Allowlist** and **Monitoring Policy** template types are managed by the Device Management / Agent Version Manager — they do not appear in this module.

---

## Templates Library Screen

### Page Header

| Element | Value |
|---|---|
| Title | "Configuration Templates" |
| Subtitle | "Reusable setup presets applied to tenants during provisioning or ongoing configuration." |
| Primary action | "New Template" button |
| Tab strip | All \| Configuration \| Job Family \| Leave Policy \| Onboarding \| Data Import |

### Templates Table

| Column | Notes |
|---|---|
| Name | Template display name + `template_key` in small text below |
| Type | Badge: colour-coded by `template_type` |
| Version | Current version number |
| System | Lock icon if `is_system = true` |
| Active | Toggle — deactivating is blocked if pending role links exist |
| Last Updated | `updated_at` |
| Actions | View / Edit / Clone / Apply to Tenant / Deactivate |

**Rule:** System templates show "Clone" instead of "Edit". Inactive templates are greyed out and show "Reactivate" instead of "Deactivate".

---

## Create / Edit Template — Full Field Specification

### Section 1: Identity

| Field | Label | Type | Required | Validation | Notes |
|---|---|---|---|---|---|
| Name | "Template Name" | Text | Yes | Max 150 chars | Display name shown in dropdowns |
| Template Key | "Template Key" | Text | Yes | Max 100 chars, lowercase, hyphens only, globally unique | Machine-readable stable ID — cannot be changed after creation |
| Description | "Description" | Textarea | No | Max 500 chars | Shown in the provisioning wizard template picker |
| Template Type | "Template Type" | Select | Yes | See type enum | Cannot be changed after creation |
| Industry Profile Tag | "Industry Profile Tag" | Select | No | Applies to `monitoring_policy` type only | Used for auto-selection during provisioning based on tenant industry |
| System Template | "System Template" | Toggle | Yes | Default off | Only ONEVO operators with elevated permission can set this |

### Section 2: Module Scope

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| Module Keys | "Required Modules" | Multi-select from module catalog | Yes | At least one module required (except `configuration` type which requires none). Tenant must have all listed modules entitled for apply to be allowed |

### Section 3: Payload Editor

The payload editor is a structured form — not a raw JSON editor for operators. Each `template_type` has its own form sections below. The form serialises to `payload_json` on save.

---

## Payload Schemas — Per Template Type

### `configuration` — Configuration Template

Seeds `tenant_settings`. All fields are optional — partial application is allowed (only non-null fields are written).

```json
{
  "timezone": "Europe/London",
  "date_format": "DD/MM/YYYY",
  "currency_code": "GBP",
  "work_week_days": [1, 2, 3, 4, 5],
  "work_hours_start": "09:00",
  "work_hours_end": "17:30",
  "privacy_mode": "full_transparency",
  "quiet_hours_start": "22:00",
  "quiet_hours_end": "07:00",
  "data_retention_days": {
    "raw_activity_buffer": 7,
    "daily_activity_summaries": 90,
    "audit_logs": 2555,
    "payroll_records": 2555
  }
}
```

| Field | Type | Allowed Values | Notes |
|---|---|---|---|
| `timezone` | string | IANA timezone e.g. `"Europe/London"` | Null = skip |
| `date_format` | string | `"DD/MM/YYYY"`, `"MM/DD/YYYY"`, `"YYYY-MM-DD"` | Null = skip |
| `currency_code` | string | ISO 4217 3-letter code | Null = skip |
| `work_week_days` | int[] | 1=Mon … 7=Sun | Null = skip |
| `work_hours_start` | string | `"HH:MM"` 24h | Null = skip |
| `work_hours_end` | string | `"HH:MM"` 24h | Null = skip |
| `privacy_mode` | string | `"full_transparency"`, `"summary_only"`, `"covert"` | Null = skip |
| `quiet_hours_start` | string | `"HH:MM"` 24h | Null = skip |
| `quiet_hours_end` | string | `"HH:MM"` 24h | Null = skip |
| `data_retention_days` | object | Each key is a retention category, value is integer days | Null = skip entire block |

---

### `job_family` — Job Family Template

Seeds one `job_families` row and its `job_levels`. Each level optionally references a role template — this drives the deferred role-linking mechanism.

```json
{
  "family_name": "Engineering",
  "description": "Software engineering roles from junior to principal",
  "levels": [
    {
      "name": "Junior Engineer",
      "rank": 1,
      "role_template_id": "uuid-of-global-role-template",
      "salary_minimum": 35000,
      "salary_maximum": 45000
    },
    {
      "name": "Engineer",
      "rank": 2,
      "role_template_id": "uuid-of-global-role-template",
      "salary_minimum": 45000,
      "salary_maximum": 65000
    },
    {
      "name": "Senior Engineer",
      "rank": 3,
      "role_template_id": "uuid-of-global-role-template",
      "salary_minimum": 65000,
      "salary_maximum": 90000
    }
  ]
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `family_name` | string | Yes | Max 100 chars. Must be unique per tenant |
| `description` | string | No | Max 500 chars |
| `levels[].name` | string | Yes | Max 50 chars |
| `levels[].rank` | int | Yes | Must be unique within this family. Used as the stable match key on reapply |
| `levels[].role_template_id` | uuid | No | References `role_templates.id`. If the role template has been applied to this tenant, `job_levels.default_role_id` is set immediately. If not, `job_levels.pending_role_template_id` is set |
| `levels[].salary_minimum` | decimal | No | Indicative band in tenant currency |
| `levels[].salary_maximum` | decimal | No | Indicative band in tenant currency |

**Deferred Role-Linking Behaviour:**

When apply runs for a level with `role_template_id`:
1. Check `roles WHERE tenant_id = X AND source_template_id = level.role_template_id`
2. Found → set `job_levels.default_role_id = role.id`, `pending_role_template_id = null`
3. Not found → set `job_levels.pending_role_template_id = level.role_template_id`, `default_role_id = null`
4. Warning returned: `"Level '{name}' role link is pending — apply role template '{key}' to resolve."`

When a role template is later applied to this tenant (via Role Template Manager), the apply handler scans `job_levels WHERE tenant_id = X AND pending_role_template_id = template.id`, sets `default_role_id`, and clears `pending_role_template_id`.

---

### `leave_policy` — Leave Policy Template

Seeds `leave_types` and `leave_policies`. One rule = one leave type + one policy row.

```json
{
  "rules": [
    {
      "leave_type_name": "Annual Leave",
      "is_paid": true,
      "requires_approval": true,
      "requires_document": false,
      "max_consecutive_days": null,
      "annual_entitlement_days": 25,
      "carry_forward_max_days": 5,
      "carry_forward_expiry_months": 3,
      "accrual_method": "annual",
      "proration_method": "calendar_days",
      "minimum_notice_days": 1,
      "negative_balance_allowed": false,
      "job_level_rank": null
    },
    {
      "leave_type_name": "Sick Leave",
      "is_paid": true,
      "requires_approval": false,
      "requires_document": true,
      "max_consecutive_days": 5,
      "annual_entitlement_days": 10,
      "carry_forward_max_days": 0,
      "carry_forward_expiry_months": 0,
      "accrual_method": "annual",
      "proration_method": "calendar_days",
      "minimum_notice_days": 0,
      "negative_balance_allowed": false,
      "job_level_rank": null
    }
  ]
}
```

| Field | Type | Required | Allowed Values | Notes |
|---|---|---|---|---|
| `leave_type_name` | string | Yes | Max 50 chars | If a leave type with this name already exists for the tenant, it is reused (upsert by name) |
| `is_paid` | bool | Yes | | |
| `requires_approval` | bool | Yes | | |
| `requires_document` | bool | Yes | | |
| `max_consecutive_days` | int | No | | Null = no limit |
| `annual_entitlement_days` | decimal | Yes | | |
| `carry_forward_max_days` | decimal | Yes | | 0 = no carry forward |
| `carry_forward_expiry_months` | int | Yes | | 0 = never expires |
| `accrual_method` | string | Yes | `"annual"`, `"monthly"`, `"daily"` | |
| `proration_method` | string | Yes | `"calendar_days"`, `"working_days"` | |
| `minimum_notice_days` | int | Yes | | |
| `negative_balance_allowed` | bool | Yes | | |
| `job_level_rank` | int | No | | Null = policy applies to all levels. Integer = matched to `job_levels.rank` for this tenant. If no match found → `job_level_id = null` + warning |

**Job Level Rank Matching:**
- `null` → `leave_policies.job_level_id = null` (all levels)
- Integer N → `SELECT id FROM job_levels WHERE tenant_id = X AND rank = N LIMIT 1`
  - Found → `leave_policies.job_level_id = matched_id`
  - Not found → `leave_policies.job_level_id = null` + warning: `"Leave rule for '{leave_type_name}' could not be linked — no job level with rank {N} exists for this tenant. Policy applied to all levels."`

---

### `monitoring_policy` — Monitoring Policy Template

> **Out of scope for this module.** Monitoring Policy templates are managed by the Device Management / Agent Version Manager operator role. The payload schema and apply logic are documented in [[developer-platform/modules/device-management/end-to-end-logic|Device Management End-to-End Logic]].

Seeds one `monitoring_feature_toggles` row for the tenant (upsert — one row per tenant).

```json
{
  "activity_monitoring": true,
  "application_tracking": true,
  "document_tracking": false,
  "communication_tracking": true,
  "screenshot_capture": false,
  "meeting_detection": true,
  "device_tracking": true,
  "work_location_verification": false,
  "identity_verification": false,
  "biometric": false
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `activity_monitoring` | bool | Yes | Keyboard/mouse event counting |
| `application_tracking` | bool | Yes | App usage tracking |
| `document_tracking` | bool | Yes | Document tool time tracking |
| `communication_tracking` | bool | Yes | Communication tool active time |
| `screenshot_capture` | bool | Yes | Screenshot command eligibility — never scheduled in Phase 1 |
| `meeting_detection` | bool | Yes | Meeting time tracking |
| `device_tracking` | bool | Yes | Device online/offline tracking |
| `work_location_verification` | bool | Yes | Network-based work-location compliance |
| `identity_verification` | bool | Yes | Photo verification via tray app |
| `biometric` | bool | Yes | Fingerprint terminal events |

**Auto-selection rule:** During provisioning Step 4, if a tenant has an `industry_profile_tag` set, the system automatically pre-selects the monitoring policy template whose `industry_profile_tag` matches. The operator can override.

---

### `app_allowlist` — App Allowlist Template

> **Out of scope for this module.** App Allowlist templates are managed by the Device Management / Agent Version Manager operator role. The payload schema and apply logic are documented in [[developer-platform/modules/device-management/end-to-end-logic|Device Management End-to-End Logic]].

Seeds `app_allowlists` rows at tenant scope. Upsert by `(tenant_id, scope_type='tenant', process_name)`.

```json
{
  "mode": "allowlist",
  "entries": [
    {
      "process_name": "chrome.exe",
      "application_display_name": "Google Chrome",
      "category": "browser",
      "is_allowed": true
    },
    {
      "process_name": "slack.exe",
      "application_display_name": "Slack",
      "category": "communication",
      "is_allowed": true
    },
    {
      "process_name": "spotify.exe",
      "application_display_name": "Spotify",
      "category": "other",
      "is_allowed": false
    }
  ]
}
```

| Field | Type | Required | Allowed Values | Notes |
|---|---|---|---|---|
| `mode` | string | Yes | `"allowlist"`, `"blocklist"` | Stored on tenant settings for agent policy |
| `entries[].process_name` | string | Yes | Max 100 chars | Authoritative matching key — case-insensitive on agent side |
| `entries[].application_display_name` | string | Yes | Max 200 chars | Metadata only — not used for matching |
| `entries[].category` | string | Yes | `"browser"`, `"communication"`, `"development"`, `"office"`, `"design"`, `"productivity"`, `"other"` | |
| `entries[].is_allowed` | bool | Yes | | |

All entries are seeded at `scope_type = 'tenant'`, `scope_id = null`. Tenant admins can add role-scoped or employee-scoped overrides after apply.

---

### `onboarding` — Onboarding Template

Seeds `onboarding_templates` and `onboarding_template_tasks`. Does **not** create live tasks — task instances are created per new hire at onboarding time using this template.

```json
{
  "target_role_template_key": "employee",
  "target_job_family_template_key": "engineering",
  "target_job_level_rank": 2,
  "target_department": null,
  "tasks": [
    {
      "title": "Complete IT Setup",
      "description": "Collect laptop and configure accounts with IT Admin.",
      "due_days_offset": 1,
      "assigned_to": "it_admin",
      "required_document_key": null,
      "order_index": 0
    },
    {
      "title": "Sign NDA",
      "description": "Read and acknowledge the NDA document.",
      "due_days_offset": 3,
      "assigned_to": "employee",
      "required_document_key": "nda",
      "order_index": 1
    },
    {
      "title": "Complete Compliance Training",
      "description": "Complete the mandatory compliance training module.",
      "due_days_offset": 7,
      "assigned_to": "employee",
      "required_document_key": null,
      "order_index": 2
    }
  ]
}
```

| Field | Type | Required | Allowed Values | Notes |
|---|---|---|---|---|
| `target_role_template_key` | string | No | `role_templates.template_key` or null | Null = applies to all new hires regardless of role |
| `target_job_family_template_key` | string | No | `configuration_templates.template_key` where `template_type = "job_family"`, or null | Null = applies to all job families. If set, onboarding applies only when the new hire is assigned to a job family seeded from this template |
| `target_job_level_rank` | int | No | Existing level rank within the selected job family template, or null | Null = applies to all levels. If set, `target_job_family_template_key` is required so the level can be resolved unambiguously |
| `target_department` | string | No | Department name or null | Null = all departments |
| `tasks[].title` | string | Yes | Max 200 chars | |
| `tasks[].description` | string | No | Max 1000 chars | |
| `tasks[].due_days_offset` | int | Yes | 1–365 | Days from hire date |
| `tasks[].assigned_to` | string | Yes | `"employee"`, `"hr_admin"`, `"it_admin"`, `"manager"` | Who the task is created for |
| `tasks[].required_document_key` | string | No | Document key or null | If set, task includes a document acknowledgement step |
| `tasks[].order_index` | int | Yes | 0-based | Display and dependency ordering |

**Targeting rule:** Onboarding template targeting is additive. A new hire must match all non-null targeting fields (`target_role_template_key`, `target_job_family_template_key`, `target_job_level_rank`, and `target_department`) before this template is selected. If `target_job_level_rank` is provided without `target_job_family_template_key`, return validation error `target_job_family_required`.

---

### `data_import_mapping` — Data Import Mapping Template

Seeds `data_import_mapping_templates` and `data_import_field_mappings`.

```json
{
  "source_type": "csv",
  "field_mappings": [
    {
      "source_column_name": "First Name",
      "canonical_field": "employees.first_name",
      "is_required": true,
      "default_value": null,
      "validation_rule": null,
      "transform_rule": "trim"
    },
    {
      "source_column_name": "Last Name",
      "canonical_field": "employees.last_name",
      "is_required": true,
      "default_value": null,
      "validation_rule": null,
      "transform_rule": "trim"
    },
    {
      "source_column_name": "DOB",
      "canonical_field": "employees.date_of_birth",
      "is_required": false,
      "default_value": null,
      "validation_rule": "date:DD/MM/YYYY",
      "transform_rule": null
    },
    {
      "source_column_name": "Department",
      "canonical_field": "departments.name",
      "is_required": false,
      "default_value": null,
      "validation_rule": null,
      "transform_rule": null
    }
  ]
}
```

| Field | Type | Required | Allowed Values | Notes |
|---|---|---|---|---|
| `source_type` | string | Yes | `"csv"`, `"excel"`, `"people_hr"` | |
| `field_mappings[].source_column_name` | string | Yes | | Header from the source file |
| `field_mappings[].canonical_field` | string | Yes | Dot-notation ONEVO field e.g. `"employees.first_name"` | |
| `field_mappings[].is_required` | bool | Yes | | If true and column is missing or empty, row is invalid |
| `field_mappings[].default_value` | string | No | | Used when source column is empty |
| `field_mappings[].validation_rule` | string | No | e.g. `"date:DD/MM/YYYY"`, `"max_length:100"` | Applied per-cell before import commit |
| `field_mappings[].transform_rule` | string | No | `"trim"`, `"uppercase"`, `"lowercase"` | Applied before validation |

---

## Apply Flow — Step by Step

**Entry points:**
- Provisioning wizard Step 4 (bulk apply of multiple templates in sequence)
- Template detail → "Apply to Tenant" button
- Tenant card → Configuration tab → "Apply Template" action

**Apply sequence:**

```
1. Validate tenant exists and is not cancelled
2. Validate template exists and is_active = true
3. Check module entitlement (see entitlement table in overview)
   → If not entitled: return 400, write nothing
4. Deserialise payload_json into the typed payload record
   → If deserialisation fails: return 400 with field-level errors
5. Run type-specific apply handler:
   → configuration     → ApplyConfigurationPayloadHandler
   → job_family        → ApplyJobFamilyPayloadHandler
   → leave_policy      → ApplyLeavePolicyPayloadHandler
   → monitoring_policy → ApplyMonitoringPolicyPayloadHandler
   → app_allowlist     → ApplyAppAllowlistPayloadHandler
   → onboarding        → ApplyOnboardingPayloadHandler
   → data_import_mapping → ApplyDataImportMappingPayloadHandler
6. Collect warnings (non-blocking)
7. Write audit row to tenant_configuration_template_applications
8. SaveChanges (all writes in one transaction)
9. Return { application_id, applied_version, warnings[] }
```

---

## Reapply Rules

| Scenario | `force_update = false` | `force_update = true` |
|---|---|---|
| **Configuration** | Writes only null/missing tenant_settings fields | Overwrites all fields in payload |
| **Job Family — family does not exist** | Creates family + all levels | Creates family + all levels |
| **Job Family — family already exists** | Skips family creation. Re-evaluates `pending_role_template_id` on existing levels. Adds new levels (by rank) that don't exist yet | Updates family description. Upserts levels by rank — updates name and salary bands. Re-evaluates all pending links. Warns if level has employees (updates name only, does not delete) |
| **Leave Policy** | Creates new leave_type (if name not found) and new policy row | Creates new leave_type (if name not found). If leave_type exists, creates new policy row (does not overwrite — policies are versioned) |
| **Monitoring Policy** | Upserts the single tenant row | Upserts the single tenant row |
| **App Allowlist** | Upserts by `(tenant_id, 'tenant', process_name)` — skips exact duplicates | Upserts by `(tenant_id, 'tenant', process_name)` — updates all matching entries |
| **Onboarding** | Creates new onboarding template (allows multiple templates per tenant/role) | Creates new onboarding template — does not overwrite existing ones |
| **Data Import Mapping** | Creates new mapping template | Creates new mapping template — does not overwrite existing ones |

---

## Module Entitlement Guard

Checked before any writes. If the tenant lacks the required module, the apply is blocked entirely — no partial writes.

| Template type | Required module key |
|---|---|
| `configuration` | _(none — always allowed)_ |
| `job_family` | `core_hr` |
| `leave_policy` | `leave` |
| `monitoring_policy` | `monitoring` |
| `app_allowlist` | `configuration` |
| `onboarding` | `core_hr` |
| `data_import_mapping` | `core_hr` |

Error response when blocked: `400 "Module '{key}' is not entitled for this tenant. Apply template is blocked."`

---

## APIs — Full Catalog

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/configuration-templates` | List templates; filter by `?type=`, `?active_only=`, `?industry_tag=` | `platform.config_templates.read` |
| `GET` | `/admin/v1/configuration-templates/{id}` | Template detail + version history | `platform.config_templates.read` |
| `POST` | `/admin/v1/configuration-templates` | Create new template | `platform.config_templates.manage` |
| `PATCH` | `/admin/v1/configuration-templates/{id}` | Update name / description / payload — increments version | `platform.config_templates.manage` |
| `DELETE` | `/admin/v1/configuration-templates/{id}` | Deactivate — blocked if pending role links exist | `platform.config_templates.manage` |
| `POST` | `/admin/v1/configuration-templates/{id}/clone` | Clone into new editable template | `platform.config_templates.manage` |
| `POST` | `/admin/v1/tenants/{id}/configuration-templates/{templateId}/apply` | Apply to tenant — body: `{ force_update: bool }` | `platform.config_templates.manage` |
| `GET` | `/admin/v1/tenants/{id}/configuration-template-applications` | Apply history for this tenant | `platform.tenants.read` |

---

## Error Taxonomy

| Error Code | HTTP | Condition |
|---|---|---|
| `template_not_found` | 404 | `{id}` does not exist |
| `template_inactive` | 400 | Template `is_active = false` |
| `system_template_not_editable` | 400 | Attempt to edit a system template directly |
| `template_key_taken` | 409 | `template_key` already exists |
| `module_not_entitled` | 400 | Tenant lacks required module for this template type |
| `payload_invalid` | 400 | Payload JSON fails schema validation — returns field-level errors |
| `deactivation_blocked` | 400 | Template has unresolved `pending_role_template_id` references on job levels |
| `tenant_not_found` | 404 | Tenant ID not found on apply |
