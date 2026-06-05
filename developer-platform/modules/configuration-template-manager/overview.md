# Configuration Template Manager

**Module:** Developer Platform -> Template Management
**Phase:** Phase 1
**Actor:** Platform operator with `platform.templates.manage`

---

## Purpose

Configuration Templates are the non-role template tabs of **Template Management** (`/platform/templates`). They let platform operators create, version, and apply reusable setup presets to tenants. Each template encodes the full payload for a specific configuration domain: position template packs, leave rules, tenant settings, monitoring policy, app allowlist, onboarding, or import mapping. Applying a template seeds the corresponding module tables without requiring the operator to fill every field manually for each new tenant.

Templates are global (not tenant-scoped). Applying a template creates tenant-specific records; the global template is never mutated by tenant customisations.

> **App Allowlist** and **Monitoring Policy** templates are Phase 1 provisioning artifacts and are managed by Template Management.

---

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `configuration_templates` | Read + write — template definitions with payload JSON and versioning |
| `tenant_configuration_template_applications` | Write — one audit row per apply action per tenant |
| `tenant_settings` (Configuration module) | Write on apply — configuration template payload |
| `monitoring_feature_toggles` (Configuration module) | Write on apply — monitoring policy template payload |
| `position_template_packs`, `position_templates`, tenant `positions` (Org Structure module) | Write on apply - position template payload and linked role template references |
| `leave_types` (Leave module) | Write on apply — leave policy template payload |
| `leave_policies` (Leave module) | Write on apply — leave policy template payload |
| `app_allowlists` (Configuration module) | Write on apply — app allowlist template payload |
| `onboarding_templates` (Core HR module) | Write on apply — onboarding template payload |
| `onboarding_template_tasks` (Core HR module) | Write on apply — onboarding template payload |
| `data_import_mapping_templates` (Core HR module) | Write on apply — data import mapping template payload |
| `data_import_field_mappings` (Core HR module) | Write on apply — data import mapping template payload |
| Audit log | Write every template create / edit / apply / deactivate action |

**Note:** Role templates are managed separately in the [[developer-platform/modules/role-template-manager/overview|Role Template Manager]]. The `position_template` template type references `role_templates.id` per position for role linkage; this module does not write to `role_templates` directly.

---

## Capabilities

### Template Library

- List all global configuration templates, filterable by `template_type` and `industry_profile_tag`
- View full template detail including payload JSON, version, module scope, and apply history
- Create new templates for any supported type with a validated payload
- Edit templates — increments `version`; system templates (`is_system = true`) cannot be edited, only cloned
- Clone any template (system or custom) into a new editable copy
- Deactivate a template - blocked if active tenant positions or assignment rows still reference the template

### Apply to Tenant

- Apply any active template to a specific tenant from the tenant card or directly from the template detail
- Module entitlement guard: each template type requires the corresponding module to be entitled on the tenant before apply is allowed (see entitlement table in end-to-end-logic)
- `force_update` flag controls reapply behaviour — see Reapply Rules in end-to-end-logic
- Warnings returned for assignment-scope target issues and permissions excluded when a linked position role template contains modules the tenant has not bought
- Full audit row written to `tenant_configuration_template_applications` on every apply

### Provisioning Wizard Integration

- Step 4 of the tenant provisioning wizard loads templates per type via `GET /admin/v1/configuration-templates?type=`
- Template selections are applied server-side in a fixed order before `step_4_complete` is set
- Monitoring policy templates auto-matched to tenant `industry_profile_tag` if a match exists

---

## Permission Boundary Rule

| Action | Required Permission |
|---|---|
| List / view templates | `platform.templates.read` |
| Create / edit / clone / deactivate templates | `platform.templates.manage` |
| Apply template to tenant | `platform.templates.manage` |
| View tenant application history | `platform.tenants.read` |

Read-only operator accounts (`platform.templates.read` only) can browse templates and view apply history but cannot create, edit, clone, apply, or deactivate.

---

## Template Types

**Managed in this module (non-role tabs of Template Management):**

| `template_type` | Seeds into | Required module entitlement |
|---|---|---|
| `configuration` | `tenant_settings` | None — always allowed |
| `position_template` | `position_template_packs`, `position_templates`, tenant `positions` | `core_hr` |
| `leave_policy` | `leave_types`, `leave_policies` | `leave` |
| `monitoring_policy` | `monitoring_feature_toggles` | `monitoring` |
| `app_allowlist` | `app_allowlists` | `configuration` |
| `onboarding` | `onboarding_templates`, `onboarding_template_tasks`; optional assignment to tenant, departments, or positions | `core_hr` |
| `data_import_mapping` | `data_import_mapping_templates`, `data_import_field_mappings` | `core_hr` |


---

## Navigation

Platform Management sidebar group → **Templates** (`/platform/templates`)

The Templates page is a unified library. This module's template types (Configuration, Position, Leave Policy, Monitoring Policy, App Allowlist, Onboarding, Data Import) appear when their respective filter chip is selected. Role templates are managed by the same page under the Role filter chip — see [[developer-platform/modules/role-template-manager/overview|Template Management]].

Clicking `+ New Template` opens the Type Picker modal where the operator selects the type before the creation form appears.

---

## Key Rules

- A template's `payload_json` structure is fully defined per `template_type` — see the Payload Schemas section in end-to-end-logic.
- `template_key` is the stable machine-readable identifier (e.g. `uk-standard-leave`). The `name` is the display label. Both must be unique globally.
- System templates (`is_system = true`) are seeded by ONEVO; operators can clone them but not edit them directly.
- Applying a template never mutates the global template. The applied version is snapshotted in `tenant_configuration_template_applications.applied_version` and `applied_payload_json`.
- Reapplying with `force_update = false`: upserts only new records and skips existing records.
- Reapplying with `force_update = true`: updates existing records in place. Never deletes records that are in use (e.g. positions with assigned employees return a warning and are skipped, not deleted).
- Configuration templates are recommended by tenant country and legal-entity scope; the payload still writes tenant settings only.
- Position templates link positions to role templates only. Role permissions are filtered by tenant module entitlements when the role template is materialized for the tenant.
- Monitoring Policy, App Allowlist, Onboarding, and Leave Policy templates use assignment scopes: tenant, department, or position. Position-specific assignment wins over department-specific, which wins over tenant-global.

---

## Related

- [[developer-platform/modules/configuration-template-manager/end-to-end-logic|Configuration Template Manager End-to-End Logic]]
- [[developer-platform/modules/configuration-template-manager/testing|Configuration Template Manager Testing]]
- [[developer-platform/modules/role-template-manager/overview|Template Management]] — role templates apply separately; Position Templates reference them
- [[developer-platform/modules/tenant-console/overview|Tenant Management]] — provisioning wizard Step 4 applies templates
- [[developer-platform/userflow/configuration-template-management|Configuration Template Management Userflow]]
- [[database/schemas/shared-platform#configuration_templates|configuration_templates schema]]
- [[database/schemas/org-structure#positions|positions schema]] - tenant positions created from position template packs



