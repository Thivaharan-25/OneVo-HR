# Permission Assignment

**Area:** Auth & Access
**Trigger:** Admin assigns permission to role or employee (user action)
**Required Permission(s):** `roles:manage`
**Related Permissions:** `users:manage` (to access employee profiles for per-employee overrides), `employees:write` (to modify employee records)

---

> **This is the KEY flow in the ONEVO permission system.** Security role permissions are assigned to Security Roles and affect users with those roles. Team role permissions are assigned to standard Team Roles and apply only inside team/workspace context after the role is assigned through team membership. Per-employee overrides add or remove specific security permissions for one user. Module auto-grant permissions are given to every active employee based on the tenant's active modules and are never assigned or revoked here. Derived permissions (inbox:read, notifications:read) are computed automatically from the effective permission set. Tenant Super Admin can manage permissions only from the tenant's enabled module catalog; commercial entitlement is never bypassed by role power.

## Preconditions

- Tenant is active
- Tenant enabled module/feature catalog is resolved from active module entitlements, selected commercial feature keys, runtime flags, and disabled-module exclusions
- Roles exist (system or custom via [[Userflow/Auth-Access/role-creation|Role Creation Flow]])
- Explicit permissions are seeded (106 assignable permissions during [[Userflow/Platform-Setup/tenant-provisioning|Tenant Provisioning]]). Universal permissions are resolved automatically by the auth layer.
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]] (recursive: an admin who already has `roles:manage`)

## Flow Steps

### Role Surface Split

Roles & Permissions has two separate configuration surfaces:

- **Security Roles:** tenant/module authority. Stored in `roles`, `role_permissions`, and `user_roles`. Assigned to user/employee accounts.
- **Team Roles:** scoped team/workspace authority. Stored in `team_roles`, `team_role_permissions`, and `team_member_roles`. Assigned only inside team membership.

The UI must keep these surfaces separate. Team creation and team editing can show only Team Roles from `team_roles`: `Admin / Lead`, `Member`, and `Viewer / Reviewer`. They must not show security-role records from `roles`.


### Path A: Assign Permissions to a Security Role

#### Step A1: Navigate to Role Detail
- **UI:** Administration > Roles & Permissions > Security Roles > click on a security role name. Role detail page shows: Name, Description, User Count, and a full permission grid
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
  - Employee-data permissions are selected as permission codes only. Scope is not stored on `role_permissions`; it is stored on the `user_roles` assignment through `scope_type` and `scope_id`.
  - Change summary panel: "Adding 3, Removing 1"
- **API:** N/A (client-side selection)
- **Backend:** N/A
- **Validation:** At least one explicitly grantable permission must remain. Universal permissions cannot be added, removed, selected, or submitted. Access policy defaults to `self` for employee-data permissions if not explicitly chosen.
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


### Path B: Configure Team Role Permission Sets

#### Step B1: Navigate to Team Roles
- **UI:** Administration > Roles & Permissions > Team Roles
- **Standard Team Roles:** `Admin / Lead`, `Member`, `Viewer / Reviewer`
- **API:** `GET /api/v1/team-roles`
- **DB:** `team_roles`, `team_role_permissions`, `permissions`

#### Step B2: Manage Team Role Permissions
- **UI:** Select one team role -> Manage Permissions. The permission browser shows only scoped team/workspace permissions.
- **Allowed permission scope:** workspace/team-context permissions such as task assignment, sprint planning, availability viewing, workspace reporting, and workspace member invitation.
- **Blocked permission scope:** tenant security, HR admin, payroll, billing, system settings, security role management, and project visibility permissions.
- **API:** `PUT /api/v1/team-roles/{teamRoleId}/permissions`
- **Backend:** Replaces `team_role_permissions` transactionally, validates every permission against the team-scoped permission catalog, invalidates affected workspace/team permission cache, and writes audit log.
- **Validation:** Reject security-role permissions and any permission outside the tenant commercial/module boundary. Reject custom team role names outside `Admin / Lead`, `Member`, and `Viewer / Reviewer`.

#### Step B3: Assignment Boundary
- Team role permissions are not assigned directly to users.
- Org Structure > Teams assigns `team_member_roles` when adding or editing team members.
- Team creation must show only team roles and must not show `roles` security-role records.

### Path C: Per-Employee Permission Override

#### Step C1: Navigate to Employee Profile
- **UI:** Employees > search for employee > click profile > Security tab. Shows confirmed security roles, effective permissions list (universal auto-grants + role permissions + overrides), and "Override Permissions" button
- **API:** `GET /api/v1/users/{id}/permissions`
- **Backend:** `PermissionService.GetEffectivePermissionsAsync()` â†’ [[frontend/cross-cutting/authorization|Authorization]]
  - Computes: Universal auto-grants + role permissions + added overrides - removed overrides = effective permissions
- **Validation:** Permission check for `roles:manage` AND (`users:manage` OR `employees:write`)
- **DB:** `user_roles`, `role_permissions`, `user_permission_overrides`, `permissions`

#### Step C2: Add or Remove Permission Overrides
- **UI:** Permission override panel shows three columns:
  1. **Universal:** Auto-granted permissions inherited by every active employee (read-only, no checkboxes)
  2. **From Role:** Explicit permissions inherited from assigned roles. Each assigned role row shows its `scope_type` and `scope_id` from `user_roles`.
  3. **Added Overrides:** Extra explicit permissions granted to this specific employee (green highlight); scoped overrides can set `scope_type` and `scope_id` for employee-data permissions
  4. **Removed Overrides:** Explicit role permissions revoked for this specific employee (red strikethrough)
  
  To add an override: click "+" next to any unassigned permission â†’ moves to "Added Overrides"
  To remove a role permission: click "-" next to any role permission â†’ moves to "Removed Overrides"
  To revert an override: click "x" next to any override â†’ returns to original state
- **API:** N/A (client-side editing)
- **Backend:** N/A
- **Validation:** Cannot override universal permissions such as `employees:read-own`, `leave:read-own`, or `workforce:dashboard`.
- **DB:** None

#### Step C3: Save Employee Overrides
- **UI:** Click "Save Overrides". Summary shown: "Adding 2 permissions, removing 1 permission for Jane Doe"
- **API:** `PUT /api/v1/users/{id}/permission-overrides`
  ```json
  {
    "addedPermissionIds": ["uuid1", "uuid2"],
    "removedPermissionIds": ["uuid3"],
    "scopeType": "Department",
    "scopeId": "uuid",
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

#### Step C4: Immediate Effect
- **UI:** Toast: "Permission overrides saved. Changes take effect on Jane's next login or within 15 minutes"
- **API:** N/A
- **Backend:** If user has an active SignalR connection, a `force-token-refresh` message is sent, prompting immediate token refresh with new permissions
- **Validation:** N/A
- **DB:** None

### Path D: Grant Hierarchy Bypass to an Employee

#### Step D1: Navigate to Employee Security Tab
- **UI:** Employees > search employee > click profile > Security tab > scroll to **"Bypass Grants"** section (below Override Permissions panel)
- **API:** `GET /api/v1/employees/{employeeId}/bypass-grants`
- **Backend:** `BypassGrantService.GetByEmployeeAsync()` â†’ [[modules/auth/authorization/end-to-end-logic|Authorization]]
- **Validation:** Permission check for `roles:manage`. Granter must have an active `permission_delegation_scopes` record or be Tenant Super Admin. Tenant Super Admin can grant bypasses only inside enabled tenant modules.
- **DB:** `hierarchy_scope_exceptions`, `permission_delegation_scopes`

#### Step D2: Add a Bypass Grant
- **UI:** Click **"Add Bypass Grant"**. A panel appears with three fields:
  1. **Scope Type** â€” dropdown: `Department` / `Person` / `Role`
  2. **Scope Target** â€” searchable picker (required â€” Save is blocked until a target is selected):
     - Department: dept tree filtered to granter's accessible depts
     - Person: employee search filtered to granter's accessible employee pool â€” all employees below the granter in `employee_hierarchy_closure` **plus** employees reachable via the granter's own broad (`applies_to IS NULL`) bypass grants. Feature-scoped bypasses (e.g. `applies_to = 'calendar'`) are excluded from this pool â€” a granter cannot re-delegate access they only have via a feature-specific bypass.
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

#### Step D3: Save Bypass Grant
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

#### Step D4: Confirmation
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

1. **Tenant enabled catalog:** active module entitlements + selected commercial feature keys + runtime-enabled feature flags - runtime-disabled modules/features
2. **Module auto-grants:** self-service permissions for every active employee, gated by active modules (e.g. `leave:read-own` only if `leave` module is active)
3. **Tenant owner expansion:** tenant owner / Tenant Super Admin receives all assignable permissions from enabled tenant modules only
4. **Base:** Explicit permissions from the user's active assigned role (via `role_permissions`; ignore expired `user_roles`)
5. **Add:** Explicit permissions in active `user_permission_overrides` with type `grant`
6. **Remove:** Explicit permissions in active `user_permission_overrides` with type `revoke` (cannot remove module auto-grants)
7. **Filter:** Remove any permission whose module is not enabled for the tenant or whose feature key is not commercially included/runtime-enabled
8. **Derived:** `inbox:read` added if effective set contains any inbox-triggering permission; `notifications:read` added if effective set contains any notification-triggering permission
8a. **Access Scope Resolution:** For each employee-data permission in the effective set, resolve scope from `user_roles.scope_type` / `user_roles.scope_id` or from `user_permission_overrides.scope_type` / `user_permission_overrides.scope_id` when an individual override applies. Permissions with no explicit scope default to `Own`. The result is a `(permission, scope)` capability pair set.
9. **Result:** `Module auto-grants + enabled-module role permissions + active grants - active revokes + derived = Effective Permission Set`. Scope pairs are included in the `/api/v1/me/app-context` response as `capabilities`.

For customer web sessions, this effective permission set is stored in backend-held auth state and returned to the frontend as permission metadata. Browser JavaScript does not receive or decode the tenant JWT.

`*` must not be treated as a global tenant-user bypass. If a wildcard exists in implementation, tenant sessions must interpret it as "all permissions from enabled tenant modules." Platform-wide bypass belongs only to Developer Platform / operator routes.

### App Context Endpoint

`GET /api/v1/me/app-context` is called on session start and after any permission refresh signal. It returns:

- `modules` — active modules for this tenant
- `capabilities` — effective `(permission, scope)` pairs for this employee
- `navigation` — the list of nav items the user is allowed to see, computed by the backend from capabilities

Angular renders `navigation` exactly as returned. No navigation item is shown or hidden based on role name, title, or any frontend inference. See [[Userflow/Auth-Access/access-policy|Access Policy Reference]] for the full response shape and navigation resolution rules.

## Variations

### When job family level changes suggest role changes
- Employee is promoted/transferred to a new [[Userflow/Org-Structure/job-family-setup|Job Family Level]]
- New level may suggest a different role; the user's role changes only after an authorized admin confirms it
- Existing per-employee overrides are preserved unless the admin explicitly changes them
- Admin is warned: "This employee has 3 permission overrides that will carry over if you confirm this role change"
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
| Attempting to assign or revoke a module auto-grant permission | Save blocked | "Module auto-grant permissions are given automatically based on active modules and cannot be manually assigned or revoked" |
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
- [[Userflow/Org-Structure/job-family-setup|Job Family Setup]] â€” suggested role prefill via job family levels; admin confirmation is required
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


