# Template Manager

## Purpose

Template Manager is the single operator-facing module for all reusable provisioning and configuration presets. Operators use it to define, version, and apply templates to tenants during provisioning or post-activation. All template types are managed here — organized into tabs.

Customers do not access this module. All interactions are operator-only via the Developer Console at `/platform/templates`.

## Tab Structure

| Tab | What it manages |
|---|---|
| **Role Templates** | Role blueprints — materialized into tenant-scoped Auth roles and permissions |
| **Configuration** | Tenant settings presets (timezone, currency, work week, privacy mode, data retention defaults) |
| **Job Family** | Org hierarchy presets — job families, levels, and titles |
| **Leave Policy** | Leave type and policy presets |

> **App Allowlist** and **Monitoring Policy** templates are **not** managed here. They are monitoring agent policy artifacts owned by the Device Management / Agent Version Manager operator role.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `role_templates` | Read + write — role blueprint definitions with versioning |
| `role_template_permissions` | Read + write — permission codes per template version |
| `tenant_role_template_applications` | Write — history of which role template version was applied to which tenant |
| `configuration_templates` | Read + write — configuration, job family, and leave policy template definitions |
| `tenant_configuration_template_applications` | Write — history of configuration template applications |
| `roles` (Auth module) | Write through `ITenantRoleService` — materialized tenant roles |
| `role_permissions` (Auth module) | Write through Auth interfaces — tenant role permission sets |
| `permissions` (Auth module) | Read — permission catalog with module ownership |
| `job_families`, `job_levels` | Write on job family template apply |
| `leave_types`, `leave_policies` | Write on leave policy template apply |
| `tenant_settings` | Write on configuration template apply |
| Audit log | Write every template create/apply/edit action |

## Capabilities

### Role Templates tab
- Create global reusable role blueprints with a name, description, module scope filter, and selected permission codes
- Permission picker groups codes by owning module; only codes from selected modules (plus always-available foundation modules) appear
- System templates (`is_system = true`) are pre-seeded by ONEVO and cannot be directly edited — only cloned
- Clone any template (system or custom) to create an editable copy
- Version every edit — each PATCH increments `version`; previous permissions preserved for audit
- Apply to tenant: preview effective permissions filtered by tenant's entitled modules; excluded permissions listed in response
- Idempotency: if same name already exists for tenant, choose Update or Create New (version suffix)

### Configuration tab
- Create and manage configuration presets that pre-fill `tenant_settings` during provisioning
- Create and manage job family templates that seed `job_families` + `job_levels`; role links resolved immediately if matching role template already applied, otherwise stored as `pending_role_template_id`
- Create and manage leave policy templates that seed `leave_types` + `leave_policies`
- Applying any configuration template creates a `tenant_configuration_template_applications` row; tenant customization does not mutate the global template

### Owner Role Validation
- Activation guard checks that at least one materialized role for the tenant has: `roles:manage`, `users:invite`, `settings:manage`, `billing:read`
- Activation is blocked until this condition is satisfied

## Permission Boundary Rule (Role Templates)

The template's `module_scope` controls which permissions appear in the editor. When applied to a tenant, the system intersects the template's permissions with the tenant's entitled module set. A template scoped to `[leave, monitoring]` applied to a tenant with only `leave` entitled grants only leave permissions — monitoring permissions are excluded, not silently granted.

## Navigation

| Route | Permission |
|---|---|
| `/platform/templates` | `platform.role_templates.read` |
| Role template write operations | `platform.role_templates.manage` |
| Apply role template to tenant | `platform.tenants.manage` |
| Configuration template write operations | `platform.configuration_templates.manage` |

## Key Rules

- System role templates cannot be edited — clone them first
- Editing a role template (new version) does NOT update previously materialized tenant roles — re-apply is required
- Applying the same role template twice without specifying `on_duplicate` returns HTTP 409
- App Allowlist and Monitoring Policy templates are out of scope — managed by Device Management / Agent Version Manager
- All permissions excluded from a role template application are listed in the response

## Related

- [[developer-platform/modules/role-template-manager/end-to-end-logic|Template Manager End-to-End Logic]]
- [[developer-platform/modules/module-catalog-manager/overview|Module Catalog Manager]] — permission ownership determines what appears in the picker
- [[developer-platform/modules/tenant-console/overview|Tenant Console]] — provisioning wizard applies templates during Setup
- [[modules/auth/overview|Auth & Security]] — materialized roles stored in Auth module
