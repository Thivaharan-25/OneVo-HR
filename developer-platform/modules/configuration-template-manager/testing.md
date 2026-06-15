# Configuration Template Manager â€” Testing

**Module:** Developer Platform â†’ Configuration Template Manager
**Phase:** Phase 1

---

## Test Fixtures Required

- One active tenant with `core_hr`, `leave`, `monitoring`, `configuration` modules entitled
- One active tenant with no modules entitled (for entitlement guard tests)
- One global role template with `template_key = "team-lead"` available for position template linkage
- One global role template with `template_key = "engineer"` available for position template linkage and materialized during position template apply
- Platform operator account with `platform.templates.manage`
- Platform read-only account with `platform.templates.read` only

---

## Template Creation

### TC-CT-001: Create configuration template â€” happy path
**Input:** `{ template_key: "uk-office-defaults", template_type: "configuration", name: "UK Office Defaults", payload_json: { "timezone": "Europe/London", "currency_code": "GBP", "work_week_days": [1,2,3,4,5] } }`
**Action:** `POST /admin/v1/configuration-templates`
**Expected:** HTTP 201 â€” template created with `version = 1`, `is_active = true`, `is_system = false`

### TC-CT-002: Duplicate template_key rejected
**Input:** Same `template_key` as an existing template
**Action:** `POST /admin/v1/configuration-templates`
**Expected:** HTTP 409, error code `template_key_taken`

### TC-CT-003: Invalid payload JSON rejected
**Input:** `template_type = "configuration"`, `payload_json = { "timezone": 123 }` (wrong type for timezone)
**Action:** `POST /admin/v1/configuration-templates`
**Expected:** HTTP 400, error code `payload_invalid`, field error on `timezone`

### TC-CT-004: Read-only account cannot create templates
**Actor:** Read-only operator
**Action:** `POST /admin/v1/configuration-templates`
**Expected:** HTTP 403

### TC-CT-005: Editing template increments version
**Input:** PATCH with updated `description`
**Action:** `PATCH /admin/v1/configuration-templates/{id}`
**Expected:** HTTP 200, `version` incremented by 1, `updated_at` updated

### TC-CT-006: System template cannot be edited directly
**Input:** Template with `is_system = true`
**Action:** `PATCH /admin/v1/configuration-templates/{id}`
**Expected:** HTTP 400, error code `system_template_not_editable`

### TC-CT-007: Clone system template creates editable copy
**Input:** System template
**Action:** `POST /admin/v1/configuration-templates/{id}/clone`
**Expected:** HTTP 201 â€” new template with `is_system = false`, `version = 1`, new unique `template_key` (appended `-copy`)

---

## Apply â€” Configuration Template

### TC-CT-008: Apply configuration template writes tenant_settings
**Input:** Configuration template with `timezone = "Europe/London"`, `currency_code = "GBP"`
**Action:** `POST /admin/v1/tenants/{id}/configuration-templates/{templateId}/apply`
**Expected:** HTTP 200, `tenant_settings.timezone = "Europe/London"`, `tenant_settings.currency_code = "GBP"`, audit row written

### TC-CT-009: Partial payload only writes non-null fields
**Input:** Configuration template with only `timezone` set (all other fields null)
**Action:** Apply
**Expected:** Only `timezone` updated in `tenant_settings`; existing values for other fields unchanged

### TC-CT-010: Apply creates audit row
**Action:** Apply any template to a tenant
**Expected:** Row in `tenant_configuration_template_applications` with correct `template_id`, `applied_version`, `status = "applied"`, `applied_by_id`, `applied_at`

---

## Apply - Position Template Pack

### TC-CT-011: Apply position template pack - creates departments and positions
**Input:** Position template pack with Leadership and Engineering departments and three positions
**Action:** Apply
**Expected:** Tenant departments are created if missing; tenant `positions` rows are created with matching `position_key`, `position_name`, department, and reports-to links

### TC-CT-012: Apply position template pack - linked role template materializes role
**Setup:** Tenant is entitled to the modules used by the linked role template
**Input:** Position template pack with `linked_role_template_id = "engineer-role-template-id"`
**Action:** Apply
**Expected:** Linked role template is applied for the tenant; created position links to the materialized tenant role; no permission-exclusion warnings returned

### TC-CT-013: Apply position template pack - role permissions filtered by subscription
**Setup:** Linked role template includes Work Management permissions, but tenant is not entitled to Work Management
**Input:** Position template pack with `linked_role_template_id = "engineering-manager-role-template-id"`
**Action:** Apply
**Expected:** Tenant role is created with only entitled permissions; warning returned listing excluded permission count/module

### TC-CT-014: Apply position template pack - no linked role template
**Input:** Position template pack with a position that has `linked_role_template_id = null`
**Action:** Apply
**Expected:** Position is created without a linked role; no warnings

### TC-CT-015: Reapply position template pack (force_update=false) - skips existing positions
**Setup:** Tenant already has positions from this pack
**Action:** Apply same template, `force_update = false`
**Expected:** No duplicate position rows created; existing position rows are skipped; skip count is returned

### TC-CT-016: Reapply position template pack (force_update=true) - updates non-destructive fields
**Setup:** Existing position has old display name and assigned employees
**Input:** Template now has updated `position_name`
**Action:** Apply, `force_update = true`
**Expected:** Position name and safe references are updated; assigned employees are not removed or reassigned

---

## Apply - Leave Policy Template

### TC-CT-017: Apply leave policy - tenant scope
**Input:** Leave policy template with `assignment_scope = "tenant"`
**Action:** Apply
**Expected:** Leave types and policies are created; assignment row targets the full tenant

### TC-CT-018: Apply leave policy - department scope
**Setup:** Department "Engineering" exists for tenant
**Input:** Leave policy template with `assignment_scope = "department"` and `department_names = ["Engineering"]`
**Action:** Apply
**Expected:** Leave types and policies are created; assignment row targets the Engineering department

### TC-CT-019: Apply leave policy - position scope target missing
**Setup:** No position exists with `position_key = "software-engineer"`
**Input:** Leave policy template with `assignment_scope = "position"` and `position_keys = ["software-engineer"]`
**Action:** Apply
**Expected:** HTTP 422, error code `assignment_target_not_found`; no policy assignment rows written

### TC-CT-020: Apply leave policy - leave type already exists - reuses existing type
**Setup:** `leave_types` row with `name = "Annual Leave"` already exists for tenant
**Input:** Leave rule with `leave_type_name = "Annual Leave"`
**Action:** Apply
**Expected:** No new `leave_types` row created; new `leave_policies` row linked to existing type

---

## Apply â€” Module Entitlement Guard

### TC-CT-021: Apply position_template - tenant not entitled to core_hr - blocked
**Setup:** Tenant with no `core_hr` entitlement
**Input:** Position template pack
**Action:** Apply
**Expected:** HTTP 400, error code `module_not_entitled`, message includes `"core_hr"`, no rows written

### TC-CT-022: Apply leave_policy template â€” tenant not entitled to leave â€” blocked
**Setup:** Tenant with no `leave` entitlement
**Expected:** HTTP 400, error code `module_not_entitled`

### TC-CT-023: Apply configuration template â€” no module required â€” always allowed
**Setup:** Tenant with no modules entitled
**Input:** Configuration template
**Action:** Apply
**Expected:** HTTP 200 â€” applies successfully

---

## Apply â€” Monitoring Policy Template

### TC-CT-024: Apply monitoring policy template â€” seeds monitoring_feature_toggles
**Input:** Monitoring policy template with `activity_monitoring = true`, `screenshot_capture = false`
**Action:** Apply
**Expected:** `monitoring_feature_toggles.activity_monitoring = true`, `screenshot_capture = false`; upsert (not insert) if row already exists

### TC-CT-025: Reapply monitoring policy â€” overwrites all toggles
**Setup:** Existing `monitoring_feature_toggles` row
**Action:** Apply different monitoring policy template
**Expected:** All toggle values replaced with new template values

---

## Apply â€” App Allowlist Template

### TC-CT-026: Apply app allowlist template â€” seeds entries and assignment rows
**Input:** App allowlist template with 3 entries
**Action:** Apply
**Expected:** 3 `app_allowlists` rows plus assignment rows for the configured tenant, department, or position scope

### TC-CT-027: Reapply app allowlist â€” upserts by process_name
**Setup:** `app_allowlists` row for `chrome.exe` already exists for the same tenant
**Input:** Template includes `chrome.exe` with updated `is_allowed = false`
**Action:** Apply, `force_update = true`
**Expected:** Existing `chrome.exe` row updated, not duplicated

---

## Apply â€” Onboarding Template

### TC-CT-028: Apply onboarding template â€” seeds template definition only (no live tasks)
**Input:** Onboarding template with 3 tasks
**Action:** Apply
**Expected:** `onboarding_templates` row created, 3 `onboarding_template_tasks` rows created; no employee task records created

### TC-CT-029: Onboarding task order_index preserved
**Input:** Tasks with `order_index` 0, 1, 2
**Expected:** Tasks stored and returned in order_index order

### TC-CT-030: Onboarding template with department targeting
**Input:** Onboarding template with `assignment_scope = "department"` and `department_names = ["Engineering"]`
**Action:** Create/apply template
**Expected:** `onboarding_templates` row stores assignment scope and targets; generated onboarding task template applies only to new hires in the targeted department

### TC-CT-031: Onboarding scoped target without selected targets is rejected
**Input:** Onboarding template with `assignment_scope = "position"` and empty `position_keys`
**Action:** Create/update template
**Expected:** Validation fails with `assignment_scope_targets_required`; no template payload is saved

---

## Apply â€” Data Import Mapping Template

### TC-CT-032: Apply data import mapping â€” seeds template and field mappings
**Input:** Data import mapping template with `source_type = "csv"` and 4 field mappings
**Action:** Apply
**Expected:** 1 `data_import_mapping_templates` row, 4 `data_import_field_mappings` rows

### TC-CT-033: Required field mapping â€” validation_rule stored correctly
**Input:** Field mapping with `validation_rule = "date:DD/MM/YYYY"`
**Expected:** Stored verbatim; returned on GET

---

## Deactivation Guard

### TC-CT-034: Deactivate template - no active references - succeeds
**Setup:** No active tenant positions or assignment rows reference the template
**Action:** `DELETE /admin/v1/configuration-templates/{id}`
**Expected:** HTTP 200, `is_active = false`

### TC-CT-035: Deactivate position template - active tenant position exists - blocked
**Setup:** At least one active tenant position was created from this position template pack
**Action:** `DELETE /admin/v1/configuration-templates/{id}`
**Expected:** HTTP 400, error code `deactivation_blocked`, message lists the affected tenants/positions

---

## Audit

### TC-CT-036: Apply action creates audit row with correct fields
**Action:** Apply any template
**Expected:** `tenant_configuration_template_applications` row: `status = "applied"`, `applied_version = template.version`, `applied_payload_json = snapshot`, `applied_by_id = current_operator`

### TC-CT-037: Reapply supersedes previous application row
**Setup:** Existing application row with `status = "applied"`
**Action:** Apply same template again
**Expected:** Previous row updated to `status = "superseded"`; new row with `status = "applied"`

### TC-CT-038: Apply with warnings â€” warnings stored in audit row
**Action:** Apply leave policy template with unmatched rank reference
**Expected:** Warning text stored in `tenant_configuration_template_applications.warnings_json`





