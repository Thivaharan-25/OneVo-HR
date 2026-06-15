# Template Management

## Purpose

Template Management is a sub-item under the Platform Management sidebar group (`/platform/templates`). Operators use it to define, version, and apply templates to tenants during provisioning or post-activation. All template types are managed in a single unified library, filtered by type using chips at the top of the page.

Customers do not access this module. All interactions are operator-only via the Developer Console at `/platform/templates`.

## Template Library

The Template Library page (`/platform/templates`) shows all templates in a single list. Type filter chips at the top narrow the view:

| Filter Chip | What it shows |
|---|---|
| **All** | All template types |
| **Role** | Role blueprints materialized into tenant-scoped Auth roles and permissions |
| **Configuration** | Tenant settings presets (timezone, currency, work week, privacy mode, data retention defaults) |
| **Position** | Concrete position presets with linked role templates |
| **Leave Policy** | Leave type and policy presets |
| **Monitoring Policy** | Monitoring feature toggle presets for Phase 1 agent/workforce policy setup |
| **App Allowlist** | Tenant app allowlist presets for Phase 1 app usage policy setup |
| **Onboarding** | Onboarding checklist and task presets |
| **Data Import** | Data import source mapping presets |

> **App Allowlist** and **Monitoring Policy** templates are Phase 1 provisioning artifacts and are managed by Template Management.

Clicking `+ New Template` opens a **Type Picker** modal. The operator selects a type, then the form advances to the creation form for that type.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `role_templates` | Read + write — role blueprint definitions with versioning |
| `role_template_permissions` | Read + write — permission codes per template version |
| `tenant_role_template_applications` | Write — history of which role template version was applied to which tenant |
| `configuration_templates` | Read + write - configuration, position, leave policy, monitoring policy, app allowlist, onboarding, and data import template definitions |
| `tenant_configuration_template_applications` | Write — history of configuration template applications |
| `roles` (Auth module) | Write through `ITenantRoleService` — materialized tenant roles |
| `role_permissions` (Auth module) | Write through Auth interfaces — tenant role permission sets |
| `permissions` (Auth module) | Read — permission catalog with module ownership |
| `position_template_packs`, `position_templates`, tenant `positions` | Write on position template apply |
| `leave_types`, `leave_policies` | Write on leave policy template apply |
| `monitoring_feature_toggles` | Write on monitoring policy template apply |
| `app_allowlists` | Write on app allowlist template apply |
| `onboarding_templates`, `onboarding_template_tasks` | Write on onboarding template apply |
| `data_import_mapping_templates`, `data_import_field_mappings` | Write on data import mapping template apply |
| `tenant_settings` | Write on configuration template apply |
| Audit log | Write every template create/apply/edit action |

## Capabilities

### Role Templates
- Create global reusable role blueprints with a name, description, module scope filter, and selected permission codes
- Permission picker groups codes by owning module; only codes from selected modules (plus always-available foundation modules) appear
- System templates (`is_system = true`) are pre-seeded by ONEVO and cannot be directly edited — only cloned
- Clone any template (system or custom) to create an editable copy
- Version every edit — each PATCH increments `version`; previous permissions preserved for audit
- Apply to tenant: preview effective permissions filtered by tenant's entitled modules; excluded permissions listed in response
- Idempotency: if same name already exists for tenant, choose Update or Create New (version suffix)

### Non-role templates (Configuration, Position, Leave Policy, Monitoring Policy, App Allowlist, Onboarding, Data Import)
- Create and manage configuration presets that pre-fill `tenant_settings` during provisioning
- Create and manage position template packs that seed departments and concrete positions. Each position may link to one role template; role permissions are filtered by tenant module entitlements when materialized.
- Create and manage leave policy templates that seed `leave_types` + `leave_policies`
- Create and manage monitoring policy templates that seed tenant `monitoring_feature_toggles`
- Create and manage app allowlist templates that seed `app_allowlists` and assignment rows for tenant, department, or position scope
- Create and manage onboarding templates that seed `onboarding_templates` + `onboarding_template_tasks`
- Create and manage data import templates that seed `data_import_mapping_templates` + `data_import_field_mappings`
- Applying any configuration template creates a `tenant_configuration_template_applications` row; tenant customization does not mutate the global template

### Owner Role Validation
- Activation guard checks that at least one materialized role for the tenant has: `roles:manage`, `users:invite`, `settings:manage`, `billing:read`
- Activation is blocked until this condition is satisfied

## Permission Boundary Rule (Role Templates)

The template's `module_scope` controls which permissions appear in the editor. When applied to a tenant, the system intersects the template's permissions with the tenant's entitled module set. A template scoped to `[leave, monitoring]` applied to a tenant with only `leave` entitled grants only leave permissions — monitoring permissions are excluded, not silently granted.

## Navigation

| Route | Permission |
|---|---|
| `/platform/templates` | `platform.templates.read` |
| Role template write operations | `platform.templates.manage` |
| Apply role template to tenant | `platform.tenants.manage` |
| Non-role template write operations | `platform.templates.manage` |

## Key Rules

- System role templates cannot be edited — clone them first
- Editing a role template (new version) does NOT update previously materialized tenant roles — re-apply is required
- Applying the same role template twice without specifying `on_duplicate` returns HTTP 409
- App Allowlist and Monitoring Policy templates are Phase 1 provisioning presets managed in Template Management
- All permissions excluded from a role template application are listed in the response

## Related

- [[developer-platform/modules/role-template-manager/end-to-end-logic|Template Management End-to-End Logic]]
- [[developer-platform/modules/module-catalog-manager/overview|Module Catalog Manager]] — permission ownership determines what appears in the picker
- [[developer-platform/modules/tenant-console/overview|Tenant Management]] — provisioning wizard applies templates during Setup
- [[modules/auth/overview|Auth & Security]] — materialized roles stored in Auth module




