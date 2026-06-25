# Configuration Template Manager - End-to-End Logic

**Module:** Developer Platform -> Configuration Template Manager
**Phase:** Phase 1

---

## Purpose

Full field specifications, payload schemas, apply behaviour, reapply rules, and API catalog for the Configuration Template Manager. Read [[developer-platform/modules/configuration-template-manager/overview|overview.md]] first for orientation.

---

## Screen Layout

```
Developer Platform
+-- Templates / Template Manager  (/platform/templates)
    +-- Role Templates      ? Role Template Manager (separate module)
    +-- Configuration       ? This module
    +-- Position          ? This module
    +-- Time Off Policy        ? This module
    +-- Monitoring Policy   ? This module
    +-- App Allowlist       ? This module
    +-- Onboarding          ? This module
    +-- Data Import         ? This module
        (each tab: Template Library -> list + create + template detail)
```

> **App Allowlist** and **Monitoring Policy** template types are Phase 1 provisioning artifacts and appear in the Template Manager.

---

## Templates Library Screen

### Page Header

| Element | Value |
|---|---|
| Title | "Template Manager" |
| Subtitle | "Reusable setup presets applied to tenants during provisioning or ongoing configuration." |
| Primary action | "New Template" button |
| Tab strip | Role Templates \| Configuration \| Position Templates \| Time Off Policy \| Monitoring Policy \| App Allowlist \| Onboarding \| Data Import |

### Templates Table

| Column | Notes |
|---|---|
| Name | Template display name + `template_key` in small text below |
| Type | Badge: colour-coded by `template_type` |
| Version | Current version number |
| System | Lock icon if `is_system = true` |
| Active | Toggle - deactivating is blocked if active tenant positions or assignment rows still reference the template |
| Last Updated | `updated_at` |
| Actions | View / Edit / Clone / Apply to Tenant / Deactivate |

**Rule:** System templates show "Clone" instead of "Edit". Inactive templates are greyed out and show "Reactivate" instead of "Deactivate".

---

## Create / Edit Template - Full Field Specification

### Section 1: Identity

| Field | Label | Type | Required | Validation | Notes |
|---|---|---|---|---|---|
| Name | "Template Name" | Text | Yes | Max 150 chars | Display name shown in dropdowns |
| Template Key | "Template Key" | Text | Yes | Max 100 chars, lowercase, hyphens only, globally unique | Machine-readable stable ID - cannot be changed after creation |
| Description | "Description" | Textarea | No | Max 500 chars | Shown in the provisioning wizard template picker |
| Template Type | "Template Type" | Select | Yes | See type enum | Cannot be changed after creation |
| Industry Profile Tag | "Industry Profile Tag" | Select | No | Applies to `monitoring_policy` type only | Used for auto-selection during provisioning based on tenant industry |
| Country Codes | "Recommended Countries" | Multi-select | No | ISO country codes | Used for country/legal-entity based recommendation during provisioning |
| Legal Entity Scope | "Legal Entity Scope" | Select | No | `any`, `company`, `branch`, `subsidiary` | Used with country to recommend configuration and statutory-aware templates |
| System Template | "System Template" | Toggle | Yes | Default off | Only ONEVO operators with elevated permission can set this |

### Section 2: Module Scope

| Field | Label | Type | Required | Notes |
|---|---|---|---|---|
| Module Keys | "Required Modules" | Multi-select from module catalog | Yes | At least one module required (except `configuration` type which requires none). Tenant must have all listed modules entitled for apply to be allowed |

### Section 3: Payload Editor

The payload editor is a structured form - not a raw JSON editor for operators. Each `template_type` has its own form sections below. The form serialises to `payload_json` on save.

---

## Payload Schemas - Per Template Type

### `configuration` - Configuration Template

Seeds `tenant_settings`. Configuration templates are recommended by tenant country and legal-entity scope. All fields are optional - partial application is allowed (only non-null fields are written).

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
| `work_week_days` | int[] | 1=Mon ... 7=Sun | Null = skip |
| `work_hours_start` | string | `"HH:MM"` 24h | Null = skip |
| `work_hours_end` | string | `"HH:MM"` 24h | Null = skip |
| `privacy_mode` | string | `"full_transparency"`, `"summary_only"`, `"covert"` | Null = skip |
| `quiet_hours_start` | string | `"HH:MM"` 24h | Null = skip |
| `quiet_hours_end` | string | `"HH:MM"` 24h | Null = skip |
| `data_retention_days` | object | Each key is a retention category, value is integer days | Null = skip entire block |

---

### `position_template` - Position Template Pack

Seeds a reusable pack of tenant positions. Each pack is matched from the tenant's real `estimated_employee_count` into an employee count range. Each position may link to one global role template. The position template does not own monitoring, app allowlist, onboarding, or Time Off policy assignment; those templates assign themselves to tenant, department, or position scopes from their dedicated screens.

```json
{
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
      "position_key": "engineering-manager",
      "position_name": "Engineering Manager",
      "department_name": "Engineering",
      "reports_to_position_key": "managing-director",
      "linked_role_template_id": "uuid-of-manager-role-template"
    },
    {
      "position_key": "software-engineer",
      "position_name": "Software Engineer",
      "department_name": "Engineering",
      "reports_to_position_key": "engineering-manager",
      "linked_role_template_id": "uuid-of-employee-self-service-role-template"
    }
  ]
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `pack_name` | string | Yes | Display name for the position template pack |
| `employee_count_range_key` | string | Yes | One of `1-10`, `11-50`, `51-100`, `101-500`, `501-1000`, `1001+` |
| `employee_count_min` | int | Yes | Lower bound used for backend matching |
| `employee_count_max` | int? | No | Upper bound used for backend matching; null for `1001+` |
| `industry` | string | No | e.g. `software`, `professional_services`; used for recommendations |
| `positions[].position_key` | string | Yes | Stable key within the pack. Used for reports-to linking and reapply matching |
| `positions[].position_name` | string | Yes | Concrete position name, e.g. `Software Engineer`; do not use generic labels like `Employee` |
| `positions[].department_name` | string | Yes | Department to create or link under the tenant |
| `positions[].reports_to_position_key` | string | No | References another `position_key` in the same pack |
| `positions[].linked_role_template_id` | uuid | No | References `role_templates.id`. When applied, the linked role template is materialized for the tenant and filtered by tenant module entitlements |

**Auto-selection behaviour:**

When a tenant enters `estimated_employee_count`, the system maps the number to the matching employee count range and suggests the active position template pack with the same range and closest industry match. Example: `150` maps to `101-500`. Operators can override the suggested pack before applying Step 4.

Employee count range options:
- `1-10`
- `11-50`
- `51-100`
- `101-500`
- `501-1000`
- `1001+`

**Role Link Behaviour:**

When a position template with `linked_role_template_id` is applied:
1. Materialize the linked role template for the tenant if it has not already been materialized.
2. Filter the role permissions by the tenant's subscribed module entitlements.
3. Link the tenant position to the resulting tenant role.
4. Return included and excluded permission counts. Excluded permissions must include the reason, e.g. module not entitled.

The position screen owns role linkage only. Monitoring policy, app allowlist, onboarding, and Time Off policy assignments are configured from their own template screens.

---

### `time_off_policy` - Time Off Policy Template

Seeds `time_off_types` and `time_off_policies`. One rule = one Time Off type + one policy row. Admin enters policy entitlement in hours/minutes. The system converts and stores entitlement balances in minutes. The UI displays hours/minutes.

```json
{
  "rules": [
    {
      "time_off_type_name": "Annual Time Off",
      "is_paid": true,
      "requires_approval": true,
      "requires_document": false,

      "entitlement_minutes": 12000,
      "max_consecutive_minutes": null,
      "carry_forward_allowed": true,
      "carry_forward_limit_minutes": 2400,
      "carry_forward_expiry": "P3M",
      "accrual_method": "annual",
      "proration_method": "calendar_days",
      "minimum_notice_days": 1,
      "negative_balance_allowed": false
    },
    {
      "time_off_type_name": "Sick Time Off",
      "is_paid": true,
      "requires_approval": false,
      "requires_document": true,

      "entitlement_minutes": 4800,
      "max_consecutive_minutes": 2400,
      "carry_forward_allowed": false,
      "carry_forward_limit_minutes": 0,
      "carry_forward_expiry": null,
      "accrual_method": "annual",
      "proration_method": "calendar_days",
      "minimum_notice_days": 0,
      "negative_balance_allowed": false
    }
  ]
}
```

| Field | Type | Required | Allowed Values | Notes |
|---|---|---|---|---|
| `time_off_type_name` | string | Yes | Max 50 chars | If a Time Off type with this name already exists for the tenant, it is reused (upsert by name) |
| `is_paid` | bool | Yes | | |
| `requires_approval` | bool | Yes | | |
| `requires_document` | bool | Yes | | |
| `entitlement_minutes` | int | Yes | | Annual entitlement in minutes. Admin enters hours/minutes in UI. Phase 1 Time Off templates create duration-based behavior by default; templates do not configure request modes |
| `max_consecutive_minutes` | int | No | | Null = no limit |
| `carry_forward_allowed` | bool | Yes | | |
| `carry_forward_limit_minutes` | int | Required if carry-forward allowed | | 0 = no carry forward |
| `carry_forward_expiry` | string | No | ISO-8601 duration or null | Null = never expires |
| `accrual_method` | string | Yes | `"annual"`, `"monthly"`, `"daily"` | |
| `proration_method` | string | Yes | `"calendar_days"`, `"working_days"`, `"schedule_hours"` | |
| `minimum_notice_days` | int | Yes | | |
| `negative_balance_allowed` | bool | Yes | | |

**Assignment scope:** Time Off policy templates are assigned from the Time Off Policy screen to the entire tenant, selected departments, or selected positions. Time Off policy resolution must never reduce an employee below the statutory country/legal-entity baseline.

---

### `monitoring_policy` - Monitoring Policy Template

> **Phase 1.** Monitoring Policy templates are managed by the Template Manager and can be selected during provisioning Step 4.

Seeds one `monitoring_feature_toggles` row for the tenant (upsert - one row per tenant).

```json
{
  "activity_monitoring": true,
  "application_tracking": true,
  "document_tracking": false,
  "communication_tracking": true,
  "screenshot_capture": false,
  "auto_screenshot_capture": false,
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
| `screenshot_capture` | bool | Yes | Allows authorized on-demand screenshot capture |
| `auto_screenshot_capture` | bool | Yes | Allows automatic screenshot capture when monitoring detects a deviation |
| `meeting_detection` | bool | Yes | Meeting time tracking |
| `device_tracking` | bool | Yes | Device online/offline tracking |
| `work_location_verification` | bool | Yes | Network-based work-location compliance |
| `identity_verification` | bool | Yes | Photo verification via tray app |
| `biometric` | bool | Yes | Biometric/attendance terminal events |

**Auto-selection rule:** During provisioning Step 4, if a tenant has an `industry_profile_tag` set, the system automatically pre-selects the monitoring policy template whose `industry_profile_tag` matches. The operator can override.

**Assignment scope:** Monitoring policies can be assigned to the entire tenant, selected departments, or selected positions. If multiple policies match an employee, resolve in this order: position-specific, department-specific, tenant-global, system default.

---

### `app_allowlist` - App Allowlist Template

> **Phase 1.** App Allowlist templates are managed by the Template Manager and can be selected during provisioning Step 4.

Seeds `app_allowlists` rows and app allowlist assignment rows.

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
| `entries[].process_name` | string | Yes | Max 100 chars | Authoritative matching key - case-insensitive on agent side |
| `entries[].application_display_name` | string | Yes | Max 200 chars | Metadata only - not used for matching |
| `entries[].category` | string | Yes | `"browser"`, `"communication"`, `"development"`, `"office"`, `"design"`, `"productivity"`, `"other"` | |
| `entries[].is_allowed` | bool | Yes | | |

**Assignment scope:** App allowlists can be assigned to the entire tenant, selected departments, or selected positions. If multiple allowlists match an employee, resolve in this order: position-specific, department-specific, tenant-global, system default.

---

### `onboarding` - Onboarding Template

Seeds `checklist_templates` with `template_type = onboarding`. Does **not** create live `employee_checklist_tasks` - task instances are created per new hire at onboarding time using this template.

```json
{
  "assignment_scope": "department",
  "department_names": ["Engineering"],
  "position_keys": [],
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
| `assignment_scope` | string | Yes | `"tenant"`, `"department"`, `"position"` | Determines where this onboarding template applies |
| `department_names[]` | string[] | Required if scope = `department` | Department names created by tenant setup or position template packs |
| `position_keys[]` | string[] | Required if scope = `position` | Position keys created by position template packs |
| `tasks[].title` | string | Yes | Max 200 chars | |
| `tasks[].description` | string | No | Max 1000 chars | |
| `tasks[].due_days_offset` | int | Yes | 1-365 | Days from hire date |
| `tasks[].assigned_to` | string | Yes | `"employee"`, `"hr_admin"`, `"it_admin"`, `"manager"` | Who the task is created for |
| `tasks[].required_document_key` | string | No | Document key or null | If set, task includes a document acknowledgement step |
| `tasks[].order_index` | int | Yes | 0-based | Display and dependency ordering |

**Assignment scope:** Onboarding templates can be assigned to the entire tenant, selected departments, or selected positions. If multiple onboarding templates match a new hire, resolve in this order: position-specific, department-specific, tenant-global, system default.

---

### `data_import_mapping` - Data Import Mapping Template

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

## Apply Flow - Step by Step

**Entry points:**
- Provisioning wizard Step 4 (bulk apply of multiple templates in sequence)
- Template detail -> "Apply to Tenant" button
- Tenant card -> Configuration tab -> "Apply Template" action

**Apply sequence:**

```
1. Validate tenant exists and is not cancelled
2. Validate template exists and is_active = true
3. Check module entitlement (see entitlement table in overview)
   -> If not entitled: return 400, write nothing
4. Deserialise payload_json into the typed payload record
   -> If deserialisation fails: return 400 with field-level errors
5. Run type-specific apply handler:
   -> configuration     -> ApplyConfigurationPayloadHandler
   -> position_template        -> ApplyPositionTemplatePayloadHandler
   -> time_off_policy      -> ApplyTimeOffPolicyPayloadHandler
   -> monitoring_policy -> ApplyMonitoringPolicyPayloadHandler
   -> app_allowlist     -> ApplyAppAllowlistPayloadHandler
   -> onboarding        -> ApplyOnboardingPayloadHandler
   -> data_import_mapping -> ApplyDataImportMappingPayloadHandler
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
| **Position Template Pack** | Creates departments and positions that do not already exist. Materializes linked role templates with tenant-entitlement-filtered permissions | Updates position names, department links, reports-to links, and linked role template references where safe. Positions with assigned employees are updated only for non-destructive fields |
| **Time Off Policy** | Creates new time_off_type (if name not found) and new policy row | Creates new time_off_type (if name not found). If time_off_type exists, creates new policy row (does not overwrite - policies are versioned) |
| **Monitoring Policy** | Creates or updates policy and assignment rows | Creates or updates policy and assignment rows |
| **App Allowlist** | Creates or updates allowlist entries and assignment rows | Creates or updates allowlist entries and assignment rows |
| **Onboarding** | Creates new onboarding template (allows multiple templates per tenant/role) | Creates new onboarding template - does not overwrite existing ones |
| **Data Import Mapping** | Creates new mapping template | Creates new mapping template - does not overwrite existing ones |

---

## Module Entitlement Guard

Checked before any writes. If the tenant lacks the required module, the apply is blocked entirely - no partial writes.

| Template type | Required module key |
|---|---|
| `configuration` | _(none - always allowed)_ |
| `position_template` | `core_hr` |
| `time_off_policy` | `time_off` |
| `monitoring_policy` | `monitoring` |
| `app_allowlist` | `configuration` |
| `onboarding` | `core_hr` |
| `data_import_mapping` | `core_hr` |

Error response when blocked: `400 "Module '{key}' is not entitled for this tenant. Apply template is blocked."`

---

## APIs - Full Catalog

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/configuration-templates` | List templates; filter by `?type=`, `?active_only=`, `?industry_tag=` | `platform.templates.read` |
| `GET` | `/admin/v1/configuration-templates/{id}` | Template detail + version history | `platform.templates.read` |
| `POST` | `/admin/v1/configuration-templates` | Create new template | `platform.templates.manage` |
| `PATCH` | `/admin/v1/configuration-templates/{id}` | Update name / description / payload - increments version | `platform.templates.manage` |
| `DELETE` | `/admin/v1/configuration-templates/{id}` | Deactivate - blocked if active tenant positions or assignment rows still reference the template | `platform.templates.manage` |
| `POST` | `/admin/v1/configuration-templates/{id}/clone` | Clone into new editable template | `platform.templates.manage` |
| `POST` | `/admin/v1/tenants/{id}/configuration-templates/{templateId}/apply` | Apply to tenant - body: `{ force_update: bool }` | `platform.templates.manage` |
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
| `payload_invalid` | 400 | Payload JSON fails schema validation - returns field-level errors |
| `deactivation_blocked` | 400 | Active tenant positions or assignment rows still reference this template |
| `tenant_not_found` | 404 | Tenant ID not found on apply |






