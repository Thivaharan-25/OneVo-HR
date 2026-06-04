# 2026-05-17 — Configuration Template Manager KB

## What changed

Added full documentation for the Configuration Template Manager module in the Developer Platform, and updated related schema and provisioning docs.

## Files created

- `developer-platform/modules/configuration-template-manager/overview.md` — purpose, capabilities, table ownership, permission boundary, template type table, navigation, key rules
- `developer-platform/modules/configuration-template-manager/end-to-end-logic.md` — screen layout, full field specs for create/edit, payload schemas for all 7 template types, apply flow, reapply rules, entitlement guard table, full API catalog, error taxonomy
- `developer-platform/modules/configuration-template-manager/testing.md` — 36 test cases covering creation, payload validation, all 7 apply handlers, deferred suggested role linking, entitlement guard, reapply behaviour, deactivation guard, audit
- `developer-platform/userflow/configuration-template-management.md` — global template journey and tenant apply journey userflows

## Files updated

- `database/schemas/shared-platform.md`
  - `configuration_templates` table: added `description`, `industry_profile_tag` columns; removed `org_structure` from `template_type` enum; clarified `template_key` usage; added note that role templates live in `role_templates`, not here
  - `tenant_configuration_template_applications` table: added `applied_payload_json` and `warnings_json` columns; clarified `custom_payload_json` purpose; added supersede rule; added FK documentation

- `database/schemas/org-structure.md`
  - `job_levels` table: added `job_family_id`, `salary_minimum`, `salary_maximum`, `suggested_role_id`, `pending_role_template_id` columns; added unique constraint; documented deferred role-linking rule in full

- `developer-platform/backend/api-contracts.md`
  - Replaced the 3-line config template stub with a full "Configuration Template Manager" section: 8 endpoints with correct paths, descriptions, permission codes (`platform.config_templates.read/manage`), query parameters, and apply response warnings documentation

- `developer-platform/userflow/provisioning-flow.md`
  - Step 4: added Configuration Template, Monitoring Policy Template, Job Family Template, Leave Policy Template, and Onboarding Template sections
  - Replaced "Org Structure Defaults" section with "Org Defaults" (individual fields, pre-filled by Configuration Template)
  - Updated Step 4 API call body to include all template IDs and document apply order and response shape

## Key design decisions recorded

- `template_key` is the stable machine-readable identifier; `name` is display-only
- `org_structure` removed from `template_type` enum — not in scope
- Role templates remain separate (`role_templates` table, Role Template Manager module); `job_family` payload references them by ID for deferred linking
- Deferred role-linking: `job_levels.pending_role_template_id` stores an unresolved reference; cleared when the role template is applied to the tenant
- Deactivation of a template is blocked if any `job_levels.pending_role_template_id` references a role template in its payload
- Reapplying supersedes the previous `tenant_configuration_template_applications` row
- `applied_payload_json` is immutable (snapshot); `custom_payload_json` holds post-apply tenant edits


