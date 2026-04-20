# Permission Assignment

**Area:** Auth & Access
**Trigger:** Admin assigns permission to role or employee (user action)
**Required Permission(s):** `roles:manage`
**Related Permissions:** `users:manage` (to access employee profiles for per-employee overrides), `employees:write` (to modify employee records)

---

> **This is the KEY flow in the ONEVO RBAC system.** All other flows depend on permissions being correctly assigned. Permissions can be assigned at two levels: (1) to a Role (affects all users with that role), or (2) as per-employee overrides (adds or removes specific permissions for one user).

## Preconditions

- Tenant is active
- Roles exist (system or custom via [[Userflow/Auth-Access/role-creation|Role Creation Flow]])
- Permissions are seeded (90+ permissions seeded during [[Userflow/Platform-Setup/tenant-provisioning|Tenant Provisioning]])
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]] (recursive: an admin who already has `roles:manage`)

## Flow Steps

### Path A: Assign Permissions to a Role

#### Step A1: Navigate to Role Detail
- **UI:** Administration > Roles & Permissions > click on a role name. Role detail page shows: Name, Description, User Count, and a full permission grid
- **API:** `GET /api/v1/roles/{roleId}`
- **Backend:** `RoleService.GetRoleWithPermissionsAsync()` → [[frontend/cross-cutting/authorization|Authorization]]
- **Validation:** Permission check for `roles:manage`. System roles can be viewed but not modified
- **DB:** `roles`, `role_permissions`, `permissions`

#### Step A2: Manage Role Permissions
- **UI:** Click "Manage Permissions" button. Full permission browser opens (same as [[Userflow/Auth-Access/role-creation|Role Creation]]):
  - Accordion categories by module
  - Checkboxes for each permission
  - Currently assigned permissions pre-checked
  - Search bar to filter permissions
  - "Select All" / "Deselect All" per category
  - Change summary panel: "Adding 3, Removing 1"
- **API:** N/A (client-side selection)
- **Backend:** N/A
- **Validation:** At least one permission must remain
- **DB:** None

#### Step A3: Save Permission Changes
- **UI:** Click "Save Changes". Confirmation dialog: "This will affect X users who have this role. Their permissions will be updated on their next token refresh (within 15 minutes). Continue?"
- **API:** `PUT /api/v1/roles/{roleId}/permissions`
  ```json
  {
    "permissionIds": ["uuid1", "uuid2", "uuid3"]
  }
  ```
- **Backend:** `RoleService.UpdatePermissionsAsync()` → [[frontend/cross-cutting/authorization|Authorization]]
  1. Calculate diff: added permissions, removed permissions
  2. Delete removed `role_permissions` records
  3. Insert new `role_permissions` records
  4. Invalidate permission cache for all users with this role
  5. Publish `RolePermissionsUpdatedEvent`
  6. Audit log entry with old and new permission lists
- **Validation:** Cannot remove all permissions. Cannot modify system role permissions
- **DB:** `role_permissions` (inserts + deletes), `audit_logs`

#### Step A4: Propagation
- **UI:** Toast: "Permissions updated. Changes will take effect within 15 minutes for active users"
- **API:** N/A
- **Backend:** Permission cache invalidated. On next token refresh, JWT will contain updated permission claims. Active SignalR connections receive a `permissions-changed` event prompting client-side navigation refresh
- **Validation:** N/A
- **DB:** None

### Path B: Per-Employee Permission Override

#### Step B1: Navigate to Employee Profile
- **UI:** Employees > search for employee > click profile > Security tab. Shows: Assigned Role (from job family or manual assignment), Effective Permissions list (role permissions + overrides), "Override Permissions" button
- **API:** `GET /api/v1/employees/{employeeId}/permissions`
- **Backend:** `PermissionService.GetEffectivePermissionsAsync()` → [[frontend/cross-cutting/authorization|Authorization]]
  - Computes: Role permissions + added overrides - removed overrides = effective permissions
- **Validation:** Permission check for `roles:manage` AND (`users:manage` OR `employees:write`)
- **DB:** `user_roles`, `role_permissions`, `user_permission_overrides`, `permissions`

#### Step B2: Add or Remove Permission Overrides
- **UI:** Permission override panel shows three columns:
  1. **From Role:** Permissions inherited from the assigned role (read-only, grayed out checkboxes)
  2. **Added Overrides:** Extra permissions granted to this specific employee (green highlight)
  3. **Removed Overrides:** Role permissions revoked for this specific employee (red strikethrough)
  
  To add an override: click "+" next to any unassigned permission → moves to "Added Overrides"
  To remove a role permission: click "-" next to any role permission → moves to "Removed Overrides"
  To revert an override: click "x" next to any override → returns to original state
- **API:** N/A (client-side editing)
- **Backend:** N/A
- **Validation:** Cannot override system-critical permissions (e.g., cannot remove `employees:read-own` from any user)
- **DB:** None

#### Step B3: Save Employee Overrides
- **UI:** Click "Save Overrides". Summary shown: "Adding 2 permissions, removing 1 permission for Jane Doe"
- **API:** `PUT /api/v1/employees/{employeeId}/permission-overrides`
  ```json
  {
    "addedPermissionIds": ["uuid1", "uuid2"],
    "removedPermissionIds": ["uuid3"]
  }
  ```
- **Backend:** `PermissionService.SaveOverridesAsync()` → [[frontend/cross-cutting/authorization|Authorization]]
  1. Upsert `user_permission_overrides` records (type: `grant` or `revoke`)
  2. Invalidate permission cache for this specific user
  3. Publish `UserPermissionsOverriddenEvent`
  4. Audit log entry with full before/after permission diff
- **Validation:** Cannot create circular situations (e.g., removing `roles:manage` from the last admin)
- **DB:** `user_permission_overrides`, `audit_logs`

#### Step B4: Immediate Effect
- **UI:** Toast: "Permission overrides saved. Changes take effect on Jane's next login or within 15 minutes"
- **API:** N/A
- **Backend:** If user has an active SignalR connection, a `force-token-refresh` message is sent, prompting immediate token refresh with new permissions
- **Validation:** N/A
- **DB:** None

### Path C: Grant Hierarchy Bypass to an Employee

#### Step C1: Navigate to Employee Security Tab
- **UI:** Employees > search employee > click profile > Security tab > scroll to **"Bypass Grants"** section (below Override Permissions panel)
- **API:** `GET /api/v1/employees/{employeeId}/bypass-grants`
- **Backend:** `BypassGrantService.GetByEmployeeAsync()` → [[modules/auth/authorization/end-to-end-logic|Authorization]]
- **Validation:** Permission check for `roles:manage`. Granter must have an active `permission_delegation_scopes` record or be a root admin.
- **DB:** `hierarchy_scope_exceptions`, `permission_delegation_scopes`

#### Step C2: Add a Bypass Grant
- **UI:** Click **"Add Bypass Grant"**. A panel appears with three fields:
  1. **Scope Type** — dropdown: `Department` / `Person` / `Role`
  2. **Scope Target** — searchable picker:
     - Department: dept tree filtered to granter's accessible depts
     - Person: employee search filtered to granter's accessible employees
     - Role: role list
  3. **Applies To** — dropdown:
     - Root admin sees: `All Features` + individual feature names (e.g., `Calendar`, `Teams`)
     - Delegated granter sees: only features within their own `module_scope` — no "All Features" option
  4. **Expires At** — optional date picker
- **Validation:** Scope target must be within the granter's own accessible scope (ceiling rule). Delegated granters cannot set `Applies To = All Features`.
- **DB:** None (client-side selection)

#### Step C3: Save Bypass Grant
- **UI:** Click "Save Grant"
- **API:** `POST /api/v1/employees/{employeeId}/bypass-grants`
  ```json
  {
    "scopeType": "department",
    "scopeId": "uuid",
    "appliesTo": "calendar"
  }
  ```
- **Backend:** `BypassGrantService.CreateAsync()`
  1. Validate granter's scope (ceiling rule): target must be in granter's accessible scope
  2. Validate `appliesTo`: if granter is delegated, check `permission_delegation_scopes.module_scope`
  3. Insert `hierarchy_scope_exceptions` record
  4. Audit log entry
- **DB:** `hierarchy_scope_exceptions`, `audit_logs`

#### Step C4: Confirmation
- **UI:** Toast: "Bypass grant saved. [Employee] can now include [target] in [applies_to] operations."
- Bypass Grants section refreshes showing the new grant with scope type, target name, applies to, and expiry

---

### Path D: Delegate `roles:manage` with Module Scope

Triggered automatically when granting `roles:manage` to an employee via role assignment or per-employee override (Path A or Path B).

#### Step D1: Module Scope Panel Appears
- **UI:** After selecting the `roles:manage` permission in the permission browser, a **"Delegation Scope"** panel appears below automatically.
  - Module checklist is shown — one checkbox per module
  - Root admin sees all modules
  - Delegated granter sees only modules within their own `module_scope` (ceiling rule — cannot delegate beyond own scope)
- **Validation:** At least one module must be selected before save is enabled.
- **DB:** None (client-side)

#### Step D2: Save Delegation
- **UI:** Included in the existing "Save Changes" or "Save Overrides" action — no separate save step
- **API:** Existing permission save endpoints (`PUT /api/v1/roles/{roleId}/permissions` or `PUT /api/v1/employees/{employeeId}/permission-overrides`) receive an additional `delegationScope` field:
  ```json
  {
    "permissionIds": ["roles-manage-uuid"],
    "delegationScope": {
      "moduleScope": ["calendar", "hr"]
    }
  }
  ```
- **Backend:** After saving the permission, atomically insert `permission_delegation_scopes` record
  - Ceiling check: `moduleScope` must be subset of granter's own `module_scope`
  - If granter is root admin (no `permission_delegation_scopes` record), any modules are allowed
- **DB:** `user_permission_overrides` or `role_permissions` (existing) + `permission_delegation_scopes` (new)

#### Step D3: Combined Scope Effect
- The saved `module_scope` automatically governs two things:
  1. Which modules the recipient can manage permissions for
  2. Which `applies_to` values they can use when creating bypass grants (Path C)
- No separate configuration needed — one setting covers both.

#### Step D4: Confirmation
- **UI:** Toast: "Permissions updated. [Employee] can now manage permissions for: Calendar, HR."

---

## Permission Resolution Order

The system resolves effective permissions in this order:

1. **Base:** Permissions from the user's assigned role (via `role_permissions`)
2. **Add:** Permissions in `user_permission_overrides` with type `grant`
3. **Remove:** Permissions in `user_permission_overrides` with type `revoke`
4. **Result:** `(Role Permissions + Grants) - Revokes = Effective Permissions`

This effective permission set is embedded in the JWT access token claims.

## Variations

### When permissions change via Job Family Level change
- Employee is promoted/transferred to a new [[Userflow/Org-Structure/job-family-setup|Job Family Level]]
- New level has a different default role → user's role changes automatically
- Existing per-employee overrides are preserved (they layer on top of the new role)
- Admin is warned: "This employee has 3 permission overrides that will carry over to the new role"

### When viewing permission audit trail
- From employee's Security tab, click "Permission History"
- Shows timeline of all permission changes: role assignments, overrides added/removed, role permission changes that affected this user
- Each entry shows: date, changed by (admin name), what changed, reason (if provided)

### When bulk-assigning a role
- From role detail page, click "Assign to Users"
- Search and select multiple employees
- All selected employees receive the role (replacing their current role, or adding as secondary)
- Per-employee overrides are not affected

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Removing last admin's `roles:manage` | Save blocked | "Cannot remove this permission: at least one user must retain roles:manage" |
| System role modification attempt | `403 Forbidden` returned | "System roles cannot be modified. Create a custom role instead" |
| Employee not found | `404 Not Found` returned | "Employee not found" |
| Circular permission removal | Save blocked | "This change would lock out the last administrator. Operation cancelled" |
| Concurrent edit conflict | `409 Conflict` returned | "Permissions were modified by another admin. Please refresh and try again" |
| Bypass grant target outside granter's scope | Scope picker filters silently | Picker only shows accessible targets |
| Delegated granter sets `All Features` bypass | Save blocked | "All Features bypass can only be granted by root administrators" |
| Delegation scope exceeds granter's own scope | Save blocked | "You can only delegate modules within your own scope" |

## Events Triggered

- `RolePermissionsUpdatedEvent` → [[backend/messaging/event-catalog|Event Catalog]] — consumed by token cache invalidation
- `UserPermissionsOverriddenEvent` → [[backend/messaging/event-catalog|Event Catalog]] — consumed by token cache invalidation
- `AuditLogEntry` (action: `role.permissions.updated` or `user.permissions.overridden`) → [[modules/auth/audit-logging/overview|Audit Logging]]
- SignalR: `permissions-changed` event to affected clients
- SignalR: `force-token-refresh` event to specific user (for per-employee overrides)
- `BypassGrantCreatedEvent` → [[backend/messaging/event-catalog|Event Catalog]]
- `PermissionDelegationScopeCreatedEvent` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Auth-Access/role-creation|Role Creation]] — create roles before assigning permissions
- [[Userflow/Org-Structure/job-family-setup|Job Family Setup]] — automatic role assignment via job family levels
- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]] — initial permission assignment during onboarding
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]] — permission changes when promoted to new job family level
- [[Userflow/Auth-Access/login-flow|Login Flow]] — JWT contains effective permissions

## Module References

- [[frontend/cross-cutting/authorization|Authorization]] — RBAC engine, permission resolution, caching
- [[security/rbac-frontend|Rbac Frontend]] — permission browser UI components
- [[frontend/cross-cutting/authentication|Authentication]] — JWT claims with permission set
- [[modules/auth/session-management/overview|Session Management]] — token refresh for permission propagation
- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]] — job family to role mapping
- [[modules/auth/audit-logging/overview|Audit Logging]] — permission change audit trail
