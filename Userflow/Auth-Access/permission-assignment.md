# Permission Assignment

**Area:** Auth & Access
**Trigger:** Admin assigns permission to role or employee (user action)
**Required Permission(s):** `roles:manage`
**Related Permissions:** `users:manage` (to access employee profiles for per-employee overrides), `employees:write` (to modify employee records)

---

> **This is the KEY flow in the ONEVO RBAC system.** All other flows depend on permissions being correctly assigned. Explicit permissions can be assigned at two levels: (1) to a Role (affects all users with that role), or (2) as per-employee overrides (adds or removes specific permissions for one user). Universal permissions are auto-granted to every active employee and are never assigned or revoked here. Tenant Super Admin can manage permissions only from the tenant's enabled module catalog; commercial entitlement is never bypassed by role power.

## Preconditions

- Tenant is active
- Tenant enabled module catalog is resolved from subscription plan modules, paid add-ons, trial modules, approved feature grants, and disabled-module exclusions
- Roles exist (system or custom via [[Userflow/Auth-Access/role-creation|Role Creation Flow]])
- Explicit permissions are seeded (106 assignable permissions during [[Userflow/Platform-Setup/tenant-provisioning|Tenant Provisioning]]). Universal permissions are resolved automatically by the auth layer.
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]] (recursive: an admin who already has `roles:manage`)

## Flow Steps

### Path A: Assign Permissions to a Role

#### Step A1: Navigate to Role Detail
- **UI:** Administration > Roles & Permissions > click on a role name. Role detail page shows: Name, Description, User Count, and a full permission grid
- **API:** `GET /api/v1/roles/{roleId}`
- **Backend:** `RoleService.GetRoleWithPermissionsAsync()` â†’ [[frontend/cross-cutting/authorization|Authorization]]
- **Validation:** Permission check for `roles:manage`. System roles can be viewed but not modified
- **DB:** `roles`, `role_permissions`, `permissions`

#### Step A2: Manage Role Permissions
- **UI:** Click "Manage Permissions" button. Full permission browser opens (same as [[Userflow/Auth-Access/role-creation|Role Creation]]):
  - Accordion categories by module
  - Checkboxes for each explicitly grantable permission
  - Universal auto-grants shown in a read-only section without checkboxes
  - Currently assigned permissions pre-checked
  - Search bar to filter permissions
  - "Select All" / "Deselect All" per category
  - Change summary panel: "Adding 3, Removing 1"
- **API:** N/A (client-side selection)
- **Backend:** N/A
- **Validation:** At least one explicitly grantable permission must remain. Universal permissions cannot be added, removed, selected, or submitted.
- **DB:** None

#### Step A3: Save Permission Changes
- **UI:** Click "Save Changes". Confirmation dialog: "This will affect X users who have this role. Their permissions will be updated on their next token refresh (within 15 minutes). Continue?"
- **API:** `PUT /api/v1/roles/{roleId}/permissions`
  ```json
  {
    "permissionIds": ["uuid1", "uuid2", "uuid3"]
  }
  ```
- **Backend:** `RoleService.UpdatePermissionsAsync()` â†’ [[frontend/cross-cutting/authorization|Authorization]]
  1. Calculate diff: added permissions, removed permissions
  2. Delete removed `role_permissions` records
  3. Insert new `role_permissions` records
  4. Invalidate permission cache for all users with this role
  5. Publish `RolePermissionsUpdatedEvent`
  6. Audit log entry with old and new permission lists
- **Validation:** Cannot remove all explicitly grantable permissions. Cannot modify system role permissions. Reject any universal permission ID in the payload.
- **DB:** `role_permissions` (inserts + deletes), `audit_logs`

#### Step A4: Propagation
- **UI:** Toast: "Permissions updated. Changes will take effect within 15 minutes for active users"
- **API:** N/A
- **Backend:** Permission cache invalidated. On next token refresh, JWT will contain updated explicit permission claims plus the universal auto-grants. Active SignalR connections receive a `permissions-changed` event prompting client-side navigation refresh
- **Validation:** N/A
- **DB:** None

### Path B: Per-Employee Permission Override

#### Step B1: Navigate to Employee Profile
- **UI:** Employees > search for employee > click profile > Security tab. Shows: Assigned Role (from job family or manual assignment), Effective Permissions list (universal auto-grants + role permissions + overrides), "Override Permissions" button
- **API:** `GET /api/v1/users/{id}/permissions`
- **Backend:** `PermissionService.GetEffectivePermissionsAsync()` â†’ [[frontend/cross-cutting/authorization|Authorization]]
  - Computes: Universal auto-grants + role permissions + added overrides - removed overrides = effective permissions
- **Validation:** Permission check for `roles:manage` AND (`users:manage` OR `employees:write`)
- **DB:** `user_roles`, `role_permissions`, `user_permission_overrides`, `permissions`

#### Step B2: Add or Remove Permission Overrides
- **UI:** Permission override panel shows three columns:
  1. **Universal:** Auto-granted permissions inherited by every active employee (read-only, no checkboxes)
  2. **From Role:** Explicit permissions inherited from the assigned role (read-only, grayed out checkboxes)
  3. **Added Overrides:** Extra explicit permissions granted to this specific employee (green highlight)
  4. **Removed Overrides:** Explicit role permissions revoked for this specific employee (red strikethrough)
  
  To add an override: click "+" next to any unassigned permission â†’ moves to "Added Overrides"
  To remove a role permission: click "-" next to any role permission â†’ moves to "Removed Overrides"
  To revert an override: click "x" next to any override â†’ returns to original state
- **API:** N/A (client-side editing)
- **Backend:** N/A
- **Validation:** Cannot override universal permissions such as `employees:read-own`, `leave:read-own`, or `workforce:dashboard`.
- **DB:** None

#### Step B3: Save Employee Overrides
- **UI:** Click "Save Overrides". Summary shown: "Adding 2 permissions, removing 1 permission for Jane Doe"
- **API:** `PUT /api/v1/users/{id}/permission-overrides`
  ```json
  {
    "addedPermissionIds": ["uuid1", "uuid2"],
    "removedPermissionIds": ["uuid3"],
    "validFrom": "2026-05-20T00:00:00Z",
    "expiresAt": "2026-05-22T23:59:59Z"
  }
  ```
- **Backend:** `PermissionService.SaveOverridesAsync()` â†’ [[frontend/cross-cutting/authorization|Authorization]]
  1. Validate every permission belongs to a module enabled for the tenant
  2. Validate optional `validFrom` / `expiresAt` window
  3. Upsert `user_permission_overrides` records (type: `grant` or `revoke`) with optional validity window
  4. Invalidate permission cache for this specific user
  5. Publish `UserPermissionsOverriddenEvent`
  6. Audit log entry with full before/after permission diff and expiry details
- **Validation:** Cannot create circular situations (e.g., removing `roles:manage` from the last admin). Reject any universal permission ID in `addedPermissionIds` or `removedPermissionIds`. Reject permissions from disabled or unpurchased modules. `expiresAt` must be empty or greater than `validFrom` / current time.
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
- **Backend:** `BypassGrantService.GetByEmployeeAsync()` â†’ [[modules/auth/authorization/end-to-end-logic|Authorization]]
- **Validation:** Permission check for `roles:manage`. Granter must have an active `permission_delegation_scopes` record or be Tenant Super Admin. Tenant Super Admin can grant bypasses only inside enabled tenant modules.
- **DB:** `hierarchy_scope_exceptions`, `permission_delegation_scopes`

#### Step C2: Add a Bypass Grant
- **UI:** Click **"Add Bypass Grant"**. A panel appears with three fields:
  1. **Scope Type** â€” dropdown: `Department` / `Person` / `Role`
  2. **Scope Target** â€” searchable picker (required â€” Save is blocked until a target is selected):
     - Department: dept tree filtered to granter's accessible depts
     - Person: employee search filtered to granter's accessible employee pool â€” all employees below the granter in the `reports_to_id` chain **plus** employees reachable via the granter's own broad (`applies_to IS NULL`) bypass grants. Feature-scoped bypasses (e.g. `applies_to = 'calendar'`) are excluded from this pool â€” a granter cannot re-delegate access they only have via a feature-specific bypass.
     - Role: role list (picker not yet implemented in v1 â€” the Role option is visible in the Scope Type dropdown but selecting it leaves Scope Target empty, so the Save button remains disabled until a role picker is implemented)
  3. **Applies To** â€” dropdown:
     - Root admin sees: `All Features` + individual feature names (e.g., `Calendar`, `Teams`)
     - Delegated granter sees: only features within their own `module_scope` â€” no "All Features" option
  4. **Expires At** â€” optional date picker
- **Validation:**
  - Scope target is required â€” the Save button is disabled until a valid target is selected for the chosen scope type.
  - Scope target must be within the granter's own accessible scope (ceiling rule).
  - Delegated granters cannot set `Applies To = All Features`.
  - For Person scope: selected employee must be in granter's subordinate chain or reachable via a broad (`applies_to IS NULL`) bypass grant. Feature-scoped bypasses do not extend the Person picker pool.
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
  - Module checklist is shown â€” one checkbox per module
  - Tenant root admin sees all modules enabled for that tenant, not the full ONEVO product catalog
  - Platform root admin sees platform modules only in Developer Platform / operator context
  - Delegated granter sees only modules within their own `module_scope` (ceiling rule â€” cannot delegate beyond own scope)
- **Validation:** At least one module must be selected before save is enabled.
- **DB:** None (client-side)

#### Step D2: Save Delegation
- **UI:** Included in the existing "Save Changes" or "Save Overrides" action â€” no separate save step
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
  - If granter is tenant root admin (no `permission_delegation_scopes` record), any enabled tenant modules are allowed
  - Disabled or unpurchased modules are never allowed in `moduleScope`
- **DB:** `user_permission_overrides` or `role_permissions` (existing) + `permission_delegation_scopes` (new)

#### Step D3: Combined Scope Effect
- The saved `module_scope` automatically governs two things:
  1. Which modules the recipient can manage permissions for
  2. Which `applies_to` values they can use when creating bypass grants (Path C)
- No separate configuration needed â€” one setting covers both.

#### Step D4: Confirmation
- **UI:** Toast: "Permissions updated. [Employee] can now manage permissions for: Calendar, HR."

---

## Permission Resolution Order

The system resolves effective permissions in this order:

1. **Tenant enabled catalog:** subscription plan modules + paid add-ons + trial modules + approved feature grants - disabled modules
2. **Universal:** Auto-grants for every active employee
3. **Tenant owner expansion:** tenant owner / Tenant Super Admin receives all assignable permissions from enabled tenant modules only
4. **Base:** Explicit permissions from the user's active assigned role (via `role_permissions`; ignore expired `user_roles`)
5. **Add:** Explicit permissions in active `user_permission_overrides` with type `grant`
6. **Remove:** Explicit permissions in active `user_permission_overrides` with type `revoke`
7. **Filter:** Remove any non-universal permission whose module is not enabled for the tenant
8. **Result:** `Universal + enabled-module tenant owner expansion + enabled-module role permissions + active grants - active revokes = Effective Permissions`

For customer web sessions, this effective permission set is stored in backend-held auth state and returned to the frontend as permission metadata. Browser JavaScript does not receive or decode the tenant JWT.

`*` must not be treated as a global tenant-user bypass. If a wildcard exists in implementation, tenant sessions must interpret it as "all permissions from enabled tenant modules." Platform-wide bypass belongs only to Developer Platform / operator routes.

## Variations

### When permissions change via Job Family Level change
- Employee is promoted/transferred to a new [[Userflow/Org-Structure/job-family-setup|Job Family Level]]
- New level has a different default role â†’ user's role changes automatically
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
| Attempting to assign or revoke a universal permission | Save blocked | "Universal permissions are auto-granted and cannot be manually assigned or revoked" |
| Tenant owner assigns disabled-module permission | Save blocked / API returns 403 | "This module is not enabled for this tenant" |
| Temporary permission expiry is in the past | Save blocked | "Expiry must be in the future" |
| Temporary permission has expired | Permission omitted on next permission snapshot | User no longer sees or can use the action |
| Platform admin bypass used on tenant route | `403 Forbidden` returned | "Platform administrator access is not valid for this tenant route" |
| System role modification attempt | `403 Forbidden` returned | "System roles cannot be modified. Create a custom role instead" |
| Employee not found | `404 Not Found` returned | "Employee not found" |
| Circular permission removal | Save blocked | "This change would lock out the last administrator. Operation cancelled" |
| Concurrent edit conflict | `409 Conflict` returned | "Permissions were modified by another admin. Please refresh and try again" |
| Bypass grant target outside granter's scope | Scope picker filters silently | Picker only shows accessible targets |
| Delegated granter sets `All Features` bypass | Save blocked | "All Features bypass can only be granted by Tenant Super Admin inside enabled tenant modules" |
| Delegation scope exceeds granter's own scope | Save blocked | "You can only delegate modules within your own scope" |

## Events Triggered

- `RolePermissionsUpdatedEvent` â†’ [[backend/messaging/event-catalog|Event Catalog]] â€” consumed by token cache invalidation
- `UserPermissionsOverriddenEvent` â†’ [[backend/messaging/event-catalog|Event Catalog]] â€” consumed by token cache invalidation
- `AuditLogEntry` (action: `role.permissions.updated` or `user.permissions.overridden`) â†’ [[modules/auth/audit-logging/overview|Audit Logging]]
- SignalR: `permissions-changed` event to affected clients
- SignalR: `force-token-refresh` event to specific user (for per-employee overrides)
- `BypassGrantCreatedEvent` â†’ [[backend/messaging/event-catalog|Event Catalog]]
- `PermissionDelegationScopeCreatedEvent` â†’ [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Auth-Access/role-creation|Role Creation]] â€” create roles before assigning permissions
- [[Userflow/Org-Structure/job-family-setup|Job Family Setup]] â€” automatic role assignment via job family levels
- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]] â€” initial permission assignment during onboarding
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]] â€” permission changes when promoted to new job family level
- [[Userflow/Auth-Access/login-flow|Login Flow]] â€” JWT contains effective permissions

## Module References

- [[frontend/cross-cutting/authorization|Authorization]] â€” RBAC engine, permission resolution, caching
- [[security/rbac-frontend|Rbac Frontend]] â€” permission browser UI components
- [[frontend/cross-cutting/authentication|Authentication]] â€” backend session metadata with permission set
- [[modules/auth/session-management/overview|Session Management]] â€” token refresh for permission propagation
- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]] â€” job family to role mapping
- [[modules/auth/audit-logging/overview|Audit Logging]] â€” permission change audit trail
