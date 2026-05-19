# Configuration Template Manager — Testing

**Module:** Developer Platform → Configuration Template Manager
**Phase:** Phase 1

---

## Test Fixtures Required

- One active tenant with `core_hr`, `leave`, `monitoring`, `configuration` modules entitled
- One active tenant with no modules entitled (for entitlement guard tests)
- One global role template with `template_key = "team-lead"` and `source_template_id` applied to the first tenant (i.e. a matching role exists in `roles`)
- One global role template with `template_key = "engineer"` NOT yet applied to the first tenant
- Platform operator account with `platform.config_templates.manage`
- Platform read-only account with `platform.config_templates.read` only

---

## Template Creation

### TC-CT-001: Create configuration template — happy path
**Input:** `{ template_key: "uk-office-defaults", template_type: "configuration", name: "UK Office Defaults", payload_json: { "timezone": "Europe/London", "currency_code": "GBP", "work_week_days": [1,2,3,4,5] } }`
**Action:** `POST /admin/v1/configuration-templates`
**Expected:** HTTP 201 — template created with `version = 1`, `is_active = true`, `is_system = false`

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
**Expected:** HTTP 201 — new template with `is_system = false`, `version = 1`, new unique `template_key` (appended `-copy`)

---

## Apply — Configuration Template

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

## Apply — Job Family Template (Critical: Deferred Role Linking)

### TC-CT-011: Apply job family — role already applied — links immediately
**Setup:** Role with `source_template_id = "engineer-role-template-id"` already exists for the tenant
**Input:** Job family template with level `rank=1, role_template_id = "engineer-role-template-id"`
**Action:** Apply
**Expected:** `job_levels.default_role_id` = existing role ID; `job_levels.pending_role_template_id = null`; no warnings returned

### TC-CT-012: Apply job family — role not yet applied — stores pending link
**Setup:** No role with `source_template_id = "engineer-role-template-id"` exists for tenant
**Input:** Job family template with level `rank=1, role_template_id = "engineer-role-template-id"`
**Action:** Apply
**Expected:** `job_levels.default_role_id = null`; `job_levels.pending_role_template_id = "engineer-role-template-id"`; warning returned: `"Level 'Junior Engineer' role link is pending — apply role template 'engineer' to resolve."`

### TC-CT-013: Applying role template resolves pending job level links
**Setup:** `job_levels` row with `pending_role_template_id = "engineer-role-template-id"` exists for tenant
**Action:** Apply role template "engineer" to tenant (via Role Template Manager)
**Expected:** `job_levels.default_role_id` set to newly created role ID; `job_levels.pending_role_template_id = null`

### TC-CT-014: Apply job family — no role_template_id — creates level with null role
**Input:** Job family template with level that has no `role_template_id`
**Action:** Apply
**Expected:** `job_levels.default_role_id = null`, `pending_role_template_id = null`, no warnings

### TC-CT-015: Reapply job family (force_update=false) — family exists — skips existing levels
**Setup:** `job_families` and `job_levels` already exist for this tenant (from previous apply)
**Action:** Apply same template, `force_update = false`
**Expected:** No new family or level rows created; existing levels' pending links re-evaluated; no duplicate family error

### TC-CT-016: Reapply job family (force_update=true) — updates name and salary bands
**Setup:** Level rank=1 exists with old name "Junior"
**Input:** Template now has level rank=1 with name "Junior Engineer", new salary bands
**Action:** Apply, `force_update = true`
**Expected:** Existing level row updated with new name and salary bands; `default_role_id` preserved

---

## Apply — Leave Policy Template

### TC-CT-017: Apply leave policy — null job_level_rank — policy applies to all levels
**Input:** Leave rule with `job_level_rank = null`
**Action:** Apply
**Expected:** `leave_policies.job_level_id = null`; no warnings

### TC-CT-018: Apply leave policy — job_level_rank matches existing level — links correctly
**Setup:** `job_levels` row with `rank = 2` exists for tenant
**Input:** Leave rule with `job_level_rank = 2`
**Action:** Apply
**Expected:** `leave_policies.job_level_id` = matched job level ID; no warnings

### TC-CT-019: Apply leave policy — job_level_rank has no match — warns and applies globally
**Setup:** No `job_levels` row with `rank = 5` for tenant
**Input:** Leave rule with `job_level_rank = 5`
**Action:** Apply
**Expected:** `leave_policies.job_level_id = null`; warning: `"Leave rule for 'Senior Leave' could not be linked — no job level with rank 5 exists for this tenant. Policy applied to all levels."`; apply does NOT fail

### TC-CT-020: Apply leave policy — leave type already exists — reuses existing type
**Setup:** `leave_types` row with `name = "Annual Leave"` already exists for tenant
**Input:** Leave rule with `leave_type_name = "Annual Leave"`
**Action:** Apply
**Expected:** No new `leave_types` row created; new `leave_policies` row linked to existing type

---

## Apply — Module Entitlement Guard

### TC-CT-021: Apply job_family template — tenant not entitled to core_hr — blocked
**Setup:** Tenant with no `core_hr` entitlement
**Input:** Job family template
**Action:** Apply
**Expected:** HTTP 400, error code `module_not_entitled`, message includes `"core_hr"`, no rows written

### TC-CT-022: Apply leave_policy template — tenant not entitled to leave — blocked
**Setup:** Tenant with no `leave` entitlement
**Expected:** HTTP 400, error code `module_not_entitled`

### TC-CT-023: Apply configuration template — no module required — always allowed
**Setup:** Tenant with no modules entitled
**Input:** Configuration template
**Action:** Apply
**Expected:** HTTP 200 — applies successfully

---

## Apply — Monitoring Policy Template

### TC-CT-024: Apply monitoring policy template — seeds monitoring_feature_toggles
**Input:** Monitoring policy template with `activity_monitoring = true`, `screenshot_capture = false`
**Action:** Apply
**Expected:** `monitoring_feature_toggles.activity_monitoring = true`, `screenshot_capture = false`; upsert (not insert) if row already exists

### TC-CT-025: Reapply monitoring policy — overwrites all toggles
**Setup:** Existing `monitoring_feature_toggles` row
**Action:** Apply different monitoring policy template
**Expected:** All toggle values replaced with new template values

---

## Apply — App Allowlist Template

### TC-CT-026: Apply app allowlist template — seeds entries at tenant scope
**Input:** App allowlist template with 3 entries
**Action:** Apply
**Expected:** 3 `app_allowlists` rows with `scope_type = 'tenant'`, `scope_id = null`

### TC-CT-027: Reapply app allowlist — upserts by process_name
**Setup:** `app_allowlists` row for `chrome.exe` already exists at tenant scope
**Input:** Template includes `chrome.exe` with updated `is_allowed = false`
**Action:** Apply, `force_update = true`
**Expected:** Existing `chrome.exe` row updated, not duplicated

---

## Apply — Onboarding Template

### TC-CT-028: Apply onboarding template — seeds template definition only (no live tasks)
**Input:** Onboarding template with 3 tasks
**Action:** Apply
**Expected:** `onboarding_templates` row created, 3 `onboarding_template_tasks` rows created; no employee task records created

### TC-CT-029: Onboarding task order_index preserved
**Input:** Tasks with `order_index` 0, 1, 2
**Expected:** Tasks stored and returned in order_index order

### TC-CT-030: Onboarding template with job family and job level targeting
**Input:** Onboarding template with `target_job_family_template_key = "engineering"` and `target_job_level_rank = 2`
**Action:** Create/apply template
**Expected:** `onboarding_templates` row stores both targeting fields; generated onboarding task template applies only to new hires matching the targeted job family and level

### TC-CT-031: Onboarding target job level without target job family is rejected
**Input:** Onboarding template with `target_job_level_rank = 2` and `target_job_family_template_key = null`
**Action:** Create/update template
**Expected:** Validation fails with `target_job_family_required`; no template payload is saved

---

## Apply — Data Import Mapping Template

### TC-CT-032: Apply data import mapping — seeds template and field mappings
**Input:** Data import mapping template with `source_type = "csv"` and 4 field mappings
**Action:** Apply
**Expected:** 1 `data_import_mapping_templates` row, 4 `data_import_field_mappings` rows

### TC-CT-033: Required field mapping — validation_rule stored correctly
**Input:** Field mapping with `validation_rule = "date:DD/MM/YYYY"`
**Expected:** Stored verbatim; returned on GET

---

## Deactivation Guard

### TC-CT-034: Deactivate template — no pending links — succeeds
**Setup:** No `job_levels` with `pending_role_template_id` pointing to any role template in this template's payload
**Action:** `DELETE /admin/v1/configuration-templates/{id}`
**Expected:** HTTP 200, `is_active = false`

### TC-CT-035: Deactivate job family template — pending links exist — blocked
**Setup:** At least one `job_levels` row for any tenant has `pending_role_template_id` matching a role template referenced in this template
**Action:** `DELETE /admin/v1/configuration-templates/{id}`
**Expected:** HTTP 400, error code `deactivation_blocked`, message lists the affected tenants/levels

---

## Audit

### TC-CT-036: Apply action creates audit row with correct fields
**Action:** Apply any template
**Expected:** `tenant_configuration_template_applications` row: `status = "applied"`, `applied_version = template.version`, `applied_payload_json = snapshot`, `applied_by_id = current_operator`

### TC-CT-037: Reapply supersedes previous application row
**Setup:** Existing application row with `status = "applied"`
**Action:** Apply same template again
**Expected:** Previous row updated to `status = "superseded"`; new row with `status = "applied"`

### TC-CT-038: Apply with warnings — warnings stored in audit row
**Action:** Apply leave policy template with unmatched rank reference
**Expected:** Warning text stored in `tenant_configuration_template_applications.warnings_json`
