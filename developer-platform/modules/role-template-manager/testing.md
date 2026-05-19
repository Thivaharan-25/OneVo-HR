# Role Template Manager — Testing

## Test Fixtures Required

- Platform account with `platform.role_templates.manage`
- Platform account with `platform.tenants.manage` (for applying templates)
- Platform account with `platform.role_templates.read` only
- 1 active tenant entitled to `core_hr` and `leave` modules only (not `monitoring`, not `work_management`)
- At least 2 system role templates seeded (`is_system = true`)
- `permissions` table seeded with permission codes per module

---

## Template Creation

### TC-RT-001: Create template — happy path
**Input:**
```json
{
  "name": "Leave Manager",
  "description": "Can approve and manage all leave requests.",
  "is_global": true,
  "module_scope": ["leave"],
  "permission_codes": ["leave:read", "leave:approve", "leave:policy:manage"]
}
```
**Action:** `POST /admin/v1/role-templates`
**Expected:**
- HTTP 201
- `role_templates` row: `version = 1`, `is_system = false`
- `role_template_permissions` rows: 3 entries for the listed codes
- Audit log: `action = 'role_template.created'`

### TC-RT-002: Unknown permission codes rejected
**Input:** `permission_codes: ["leave:approve", "leave:this_does_not_exist"]`
**Action:** `POST /admin/v1/role-templates`
**Expected:** HTTP 422, `code: "unknown_permission_codes"`, response lists `["leave:this_does_not_exist"]`

### TC-RT-003: Permission from module outside scope rejected
**Input:** `module_scope: ["leave"]`, `permission_codes: ["monitoring:read"]` (monitoring not in scope)
**Action:** `POST /admin/v1/role-templates`
**Expected:** HTTP 422, `code: "permissions_not_in_module_scope"` — `monitoring:read` is owned by `monitoring`, not `leave`

### TC-RT-004: Foundation module permissions always allowed regardless of scope
**Input:** `module_scope: ["leave"]`, `permission_codes: ["leave:read", "roles:manage"]` — `roles:manage` is owned by foundation module `roles_permissions`
**Action:** `POST /admin/v1/role-templates`
**Expected:** HTTP 201 — foundation module permissions are always allowed in any template

### TC-RT-005: Read-only account cannot create templates
**Setup:** Account with `platform.role_templates.read` only
**Action:** `POST /admin/v1/role-templates`
**Expected:** HTTP 403

---

## Template Versioning

### TC-RT-006: Editing template increments version
**Setup:** Template at `version = 1` with 3 permissions
**Action:** `PATCH /admin/v1/role-templates/{id}` adding 1 more permission code
**Expected:**
- `role_templates.version = 2`
- `role_template_permissions` rows replaced: old 3 removed, new 4 inserted
- `role_template_price_history` preserved (previous version still auditable)

### TC-RT-007: System template cannot be edited directly
**Setup:** System template with `is_system = true`
**Action:** `PATCH /admin/v1/role-templates/{systemTemplateId}`
**Expected:** HTTP 422, `code: "system_template_not_editable"`

### TC-RT-008: Editing materialized tenant roles is NOT triggered by template edit
**Setup:** Template applied to tenant T → materialized role `HR Admin` exists for tenant T. Template is then edited.
**Expected:**
- `roles` row for tenant T: permissions UNCHANGED from when template was applied
- Apply-to-tenant screen shows "Template updated — re-apply to get latest permissions" warning for tenant T

---

## Clone System Template

### TC-RT-009: Clone system template creates editable copy
**Setup:** System template `is_system = true`
**Action:** `POST /admin/v1/role-templates/{id}/clone` `{"name": "HR Admin — Custom"}`
**Expected:**
- New template: `is_system = false`, `version = 1`, `cloned_from_id` = source template ID
- Same permission codes as source
- New template is editable via PATCH

---

## Apply Template to Tenant

### TC-RT-010: Permission boundary filter excludes non-entitled module permissions
**Setup:**
- Template "HR Admin" has permissions: `employees:read`, `leave:approve`, `monitoring:read`
- Tenant entitled to `core_hr` and `leave` only — NOT `monitoring`
**Action:** `POST /admin/v1/tenants/{id}/role-templates/{templateId}/apply`
**Expected:**
- HTTP 200
- `permissions_applied: 2` (`employees:read`, `leave:approve`)
- `permissions_excluded: 1` (`monitoring:read`)
- `excluded_reason` mentions monitoring module not entitled
- `roles` row created for tenant with only 2 permissions — `monitoring:read` is NOT granted

### TC-RT-011: Apply with all permissions excluded is blocked
**Setup:** Template has only `monitoring:read`. Tenant not entitled to `monitoring`.
**Action:** `POST /admin/v1/tenants/{id}/role-templates/{templateId}/apply`
**Expected:** HTTP 422, `code: "all_permissions_excluded"` — nothing to materialize

### TC-RT-012: Idempotency — applying same template twice with on_duplicate=update
**Setup:** Tenant already has role "Leave Manager" from a previous template application (version 1). Template now at version 2.
**Action:** `POST /admin/v1/tenants/{id}/role-templates/{templateId}/apply` `{"on_duplicate": "update"}`
**Expected:**
- HTTP 200
- Existing `roles` row updated — permission codes replaced with new effective set
- Role name unchanged ("Leave Manager")
- Users already assigned to this role keep their assignment
- Audit log: `action = 'role_template.applied'`, `action_taken: "updated"`

### TC-RT-013: Idempotency — applying same template with on_duplicate=create
**Action:** `POST /admin/v1/tenants/{id}/role-templates/{templateId}/apply` `{"on_duplicate": "create"}`
**Expected:**
- New role created: `name = "Leave Manager v2"` (or next available suffix)
- Original "Leave Manager" role preserved unchanged
- Audit log: `action_taken: "created"`

### TC-RT-014: Applying without specifying on_duplicate when duplicate exists
**Action:** `POST /admin/v1/tenants/{id}/role-templates/{templateId}/apply` (no `on_duplicate`)
**Expected:** HTTP 409, `code: "role_name_duplicate"` — forces operator to explicitly choose

### TC-RT-015: Applied template version is recorded
**Action:** Apply template at version 3 to tenant T
**Expected:**
- `tenant_role_template_applications` row: `template_version = 3`, `applied_by_id`, `applied_at`
- `GET /admin/v1/tenants/{id}/role-template-applications` returns this history entry

---

## Owner Role Validation

### TC-RT-016: Activation blocked when no owner role has minimum permissions
**Setup:** Tenant with no materialized roles having `roles:manage` + `users:invite` + `settings:manage` + `billing:read`
**Action:** `PATCH /admin/v1/tenants/{id}/provision/confirm`
**Expected:** HTTP 422, blocker: `no_owner_role` with message listing required permissions

### TC-RT-017: Activation succeeds after applying Tenant Owner template
**Setup:** "Tenant Owner" template includes all 4 required permissions. Applied to tenant.
**Action:** `PATCH /admin/v1/tenants/{id}/provision/confirm`
**Expected:** Activation proceeds (assuming other blockers also resolved) — `no_owner_role` blocker absent

---

## Tenant-Specific Role

### TC-RT-018: Create tenant-specific role respects module entitlements
**Setup:** Tenant entitled to `leave` only
**Action:** `POST /admin/v1/tenants/{id}/roles` with `permission_codes: ["leave:approve", "monitoring:read"]`
**Expected:** HTTP 422 — `monitoring:read` not allowed; tenant not entitled to `monitoring`
