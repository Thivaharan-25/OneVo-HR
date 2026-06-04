# Configuration Template Management Userflow

**Module:** Developer Platform â†’ Configuration Template Manager
**Actor:** Platform operator with `platform.config_templates.manage`

---

## Global Template Journey

### Create a new configuration template

1. Navigate to Developer Platform â†’ Templates â†’ Template Manager â†’ Configuration
2. Click "New Template"
3. Fill Section 1: Identity â€” name, template_key, description, template_type, industry_profile_tag (monitoring_policy only)
4. Fill Section 2: Module Scope â€” select required modules
5. Fill Section 3: Payload â€” structured form for the selected template_type (fields vary by type â€” see end-to-end-logic payload schemas)
   - For `onboarding`, the assignment fields are Applies To, Departments, and Positions.
   - Department or position assignment requires at least one selected target.
6. Click "Save Template"
7. **API:** `POST /admin/v1/configuration-templates`
8. Template created with `version = 1`, `is_active = true`

### Edit an existing template

1. Open template detail â†’ click "Edit"
2. System templates show "Clone" instead of "Edit" â€” editing a system template is blocked
3. Edit name, description, module scope, or payload fields
4. Save â†’ `version` increments, `updated_at` set
5. **API:** `PATCH /admin/v1/configuration-templates/{id}`
6. Previously applied tenants are **not** automatically updated â€” reapply is manual

### Clone a system template

1. Open system template detail â†’ click "Clone"
2. New editable template created with `is_system = false`, `version = 1`, `template_key` = original key + `-copy`
3. Rename and edit the clone as needed
4. **API:** `POST /admin/v1/configuration-templates/{id}/clone`

### Deactivate a template

1. Open template â†’ click "Deactivate"
2. System checks for active tenant positions and assignment rows that still reference the template
3. If references exist: error shown listing affected tenants â€” operator must resolve before deactivating
4. If clear: template set to `is_active = false`
5. **API:** `DELETE /admin/v1/configuration-templates/{id}`

---

## Tenant Apply Journey

### Apply a template from the template detail

1. Open template detail â†’ click "Apply to Tenant"
2. Tenant picker opens â€” search by name or slug
3. System shows module entitlement status for selected tenant (green tick / red X per required module)
4. If any required module is not entitled: apply button is disabled, warning shown
5. Optional: toggle "Force Update" (overwrites existing records â€” use with caution)
6. Click "Apply"
7. **API:** `POST /admin/v1/tenants/{id}/configuration-templates/{templateId}/apply`
8. Result panel shows:
   - Applied version
   - Warnings (non-blocking - e.g. assignment target issues or permissions excluded from linked position role templates because the tenant has not bought the module)
   - Link to tenant's application history

### Apply templates from the provisioning wizard (Step 4)

Templates are selected per type during Step 4. Server applies them in a fixed order after Step 4 is saved.

See [[developer-platform/userflow/provisioning-flow#step-4-configuration|Provisioning Flow Step 4]] for the full field list.

### View tenant application history

1. Open tenant card â†’ Configuration tab â†’ "Template Applications"
2. Table shows all applications ordered by `applied_at desc`
3. Each row: template name, type, applied version, status, operator, applied_at, warnings count
4. Click row to see full `applied_payload_json` snapshot and warnings
5. **API:** `GET /admin/v1/tenants/{id}/configuration-template-applications`

---

## APIs Used

| Method | Path | When |
|---|---|---|
| `GET` | `/admin/v1/configuration-templates` | Load template list (with type filter) |
| `GET` | `/admin/v1/configuration-templates/{id}` | Load template detail |
| `POST` | `/admin/v1/configuration-templates` | Create new template |
| `PATCH` | `/admin/v1/configuration-templates/{id}` | Edit template |
| `DELETE` | `/admin/v1/configuration-templates/{id}` | Deactivate template |
| `POST` | `/admin/v1/configuration-templates/{id}/clone` | Clone template |
| `POST` | `/admin/v1/tenants/{id}/configuration-templates/{templateId}/apply` | Apply to tenant |
| `GET` | `/admin/v1/tenants/{id}/configuration-template-applications` | View apply history |


