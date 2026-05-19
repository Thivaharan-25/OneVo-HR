# Configuration Template Manager

**Module:** Developer Platform → Configuration Template Manager
**Phase:** Phase 1
**Actor:** Platform operator (dev_platform_account with `platform.config_templates.manage`)

---

## Purpose

The Configuration Template Manager is the **Configuration, Job Family, and Leave Policy tabs** of the unified **Template Manager** (`/platform/templates`). It lets platform operators create, version, and apply reusable setup presets to tenants. Each template encodes the full payload for a specific configuration domain — job hierarchy, leave rules, or tenant settings. Applying a template seeds the corresponding module tables without requiring the operator to fill every field manually for each new tenant.

Templates are global (not tenant-scoped). Applying a template creates tenant-specific records; the global template is never mutated by tenant customisations.

> **App Allowlist** and **Monitoring Policy** templates are **not** managed here. They are monitoring agent policy artifacts owned by the Device Management / Agent Version Manager operator role.

---

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `configuration_templates` | Read + write — template definitions with payload JSON and versioning |
| `tenant_configuration_template_applications` | Write — one audit row per apply action per tenant |
| `tenant_settings` (Configuration module) | Write on apply — configuration template payload |
| `monitoring_feature_toggles` (Configuration module) | Write on apply — monitoring policy template payload |
| `job_families` (Org Structure module) | Write on apply — job family template payload |
| `job_levels` (Org Structure module) | Write on apply — including `pending_role_template_id` deferred linking |
| `leave_types` (Leave module) | Write on apply — leave policy template payload |
| `leave_policies` (Leave module) | Write on apply — leave policy template payload |
| `app_allowlists` (Configuration module) | Write on apply — app allowlist template payload |
| `onboarding_templates` (Core HR module) | Write on apply — onboarding template payload |
| `onboarding_template_tasks` (Core HR module) | Write on apply — onboarding template payload |
| `data_import_mapping_templates` (Core HR module) | Write on apply — data import mapping template payload |
| `data_import_field_mappings` (Core HR module) | Write on apply — data import mapping template payload |
| Audit log | Write every template create / edit / apply / deactivate action |

**Note:** Role templates are managed separately in the [[developer-platform/modules/role-template-manager/overview|Role Template Manager]]. The `job_family` template type references `role_templates.id` per level for the deferred role-linking mechanism; this module does not write to `role_templates` directly.

---

## Capabilities

### Template Library

- List all global configuration templates, filterable by `template_type` and `industry_profile_tag`
- View full template detail including payload JSON, version, module scope, and apply history
- Create new templates for any supported type with a validated payload
- Edit templates — increments `version`; system templates (`is_system = true`) cannot be edited, only cloned
- Clone any template (system or custom) into a new editable copy
- Deactivate a template — blocked if any `job_levels` row for any tenant has `pending_role_template_id` pointing to a role template referenced in this template's payload

### Apply to Tenant

- Apply any active template to a specific tenant from the tenant card or directly from the template detail
- Module entitlement guard: each template type requires the corresponding module to be entitled on the tenant before apply is allowed (see entitlement table in end-to-end-logic)
- `force_update` flag controls reapply behaviour — see Reapply Rules in end-to-end-logic
- Warnings returned for unresolved job level rank references (leave policy) and unresolved role template links (job family)
- Full audit row written to `tenant_configuration_template_applications` on every apply

### Provisioning Wizard Integration

- Step 4 of the tenant provisioning wizard loads templates per type via `GET /admin/v1/configuration-templates?type=`
- Template selections are applied server-side in a fixed order before `step_4_complete` is set
- Monitoring policy templates auto-matched to tenant `industry_profile_tag` if a match exists

---

## Permission Boundary Rule

| Action | Required Permission |
|---|---|
| List / view templates | `platform.config_templates.read` |
| Create / edit / clone / deactivate templates | `platform.config_templates.manage` |
| Apply template to tenant | `platform.config_templates.manage` |
| View tenant application history | `platform.tenants.read` |

Read-only operator accounts (`platform.config_templates.read` only) can browse templates and view apply history but cannot create, edit, clone, apply, or deactivate.

---

## Template Types

**Managed in this module (Configuration, Job Family, Leave Policy tabs of Template Manager):**

| `template_type` | Seeds into | Required module entitlement |
|---|---|---|
| `configuration` | `tenant_settings` | None — always allowed |
| `job_family` | `job_families`, `job_levels` | `core_hr` |
| `leave_policy` | `leave_types`, `leave_policies` | `leave` |
| `onboarding` | `onboarding_templates`, `onboarding_template_tasks`; optional targeting by role template, job family template, job level, and department | `core_hr` |
| `data_import_mapping` | `data_import_mapping_templates`, `data_import_field_mappings` | `core_hr` |

**Managed elsewhere:**

| `template_type` | Seeds into | Managed by |
|---|---|---|
| `monitoring_policy` | `monitoring_feature_toggles` | Device Management / Agent Version Manager |
| `app_allowlist` | `app_allowlists` | Device Management / Agent Version Manager |

---

## Navigation

Developer Platform → **Template Manager** (`/platform/templates`)

The Template Manager has six tabs. This module covers the last five:
- **Role Templates** — managed by [[developer-platform/modules/role-template-manager/overview|Role Template Manager]]
- **Configuration** — managed here
- **Job Family** — managed here
- **Leave Policy** — managed here
- **Onboarding** — managed here
- **Data Import** — managed here

---

## Key Rules

- A template's `payload_json` structure is fully defined per `template_type` — see the Payload Schemas section in end-to-end-logic.
- `template_key` is the stable machine-readable identifier (e.g. `uk-standard-leave`). The `name` is the display label. Both must be unique globally.
- System templates (`is_system = true`) are seeded by ONEVO; operators can clone them but not edit them directly.
- Applying a template never mutates the global template. The applied version is snapshotted in `tenant_configuration_template_applications.applied_version` and `applied_payload_json`.
- Reapplying with `force_update = false`: upserts only new records, skips existing ones, re-evaluates pending role links.
- Reapplying with `force_update = true`: updates existing records in place. Never deletes records that are in use (e.g. job levels with assigned employees return a warning and are skipped, not deleted).
- Deactivating a template is blocked if any tenant `job_levels` row has `pending_role_template_id` referencing a role template that is part of this template's payload.

---

## Related

- [[developer-platform/modules/configuration-template-manager/end-to-end-logic|Configuration Template Manager End-to-End Logic]]
- [[developer-platform/modules/configuration-template-manager/testing|Configuration Template Manager Testing]]
- [[developer-platform/modules/role-template-manager/overview|Role Template Manager]] — role templates apply separately; job family templates reference them
- [[developer-platform/modules/tenant-console/overview|Tenant Console]] — provisioning wizard Step 4 applies templates
- [[developer-platform/userflow/configuration-template-management|Configuration Template Management Userflow]]
- [[database/schemas/shared-platform#configuration_templates|configuration_templates schema]]
- [[database/schemas/org-structure#job_levels|job_levels schema]] — deferred role linking columns
