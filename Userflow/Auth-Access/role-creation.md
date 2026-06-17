# Security Role Creation

**Area:** Auth & Access
**Trigger:** Admin clicks Create Security Role (user action - configuration)
**Required Permission(s):** `roles:manage`
**Related Permissions:** `users:manage` (to assign the new role to users)

---

## Preconditions

- Tenant is active
- Understanding of which tenant/module permissions are needed for the security role
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Security Role Management
- **UI:** Administration > Roles & Permissions > Security Roles. List view shows security roles: Name, Description, User Count, Type (System/Custom), Created Date. System roles are marked with a lock icon. Team Roles are shown in a separate Team Roles section and are not created here.
- **API:** `GET /api/v1/roles`
- **Backend:** `RoleService.GetRolesAsync()` -> [[frontend/cross-cutting/authorization|Authorization]]
- **Validation:** Permission check for `roles:manage`
- **DB:** `roles`, `user_roles` (for user count)

### Step 2: Click Create Security Role
- **UI:** Full-page security-role form opens with sections:
  - **Basic Info:** Role Name (required, e.g., "HR Business Partner"), Description (optional, e.g., "Can manage employees in assigned departments")
  - **Permission Browser:** Accordion-style category list showing all 106 explicitly grantable permissions grouped by module. Universal permissions are shown separately as read-only auto-grants and cannot be selected.
- **API:** `GET /api/v1/permissions` (loads all explicitly grantable permissions; universal permissions are excluded from assignment payloads)
- **Backend:** `PermissionService.GetAllPermissionsAsync()` -> [[frontend/cross-cutting/authorization|Authorization]]
- **Validation:** N/A
- **DB:** `permissions`

### Step 3: Browse and Select Permissions
- **UI:** Permission categories (accordions):
  - **Universal auto-grants (read-only):** `inbox:read`, `notifications:read`, `employees:read-own`, `leave:read-own`, `attendance:read-own`, `payroll:read-own`, `performance:read-own`, `documents:read-own`, `calendar:read`, `activity:read:self`, `workforce:dashboard`
  - **Employees:** `employees:read`, `employees:write`, `employees:delete`
  - **Organization:** `org:read`, `org:manage`
  - **Leave:** `leave:read`, `leave:create`, `leave:approve`, `leave:manage`
  - **Attendance:** `attendance:read`, `attendance:approve`, `attendance:write`
  - **Payroll:** `payroll:read`, `payroll:write`, `payroll:run`, `payroll:approve`
  - **Performance:** `performance:read`, `performance:write`, `performance:manage`
  - **Documents:** `documents:read`, `documents:write`, `documents:approve`, `documents:manage`, `documents:admin`
  - **Workforce Intelligence:** `workforce:view`, `workforce:manage`, `monitoring:configure`, `monitoring:view-settings`
  - **Exceptions:** `exceptions:view`, `exceptions:manage`, `exceptions:acknowledge`
  - **Analytics:** `analytics:read`, `analytics:view`, `analytics:export`, `analytics:write`
  - **Reporting:** `reports:read`, `reports:create`
  - **Skills:** `skills:read`, `skills:write`, `skills:validate`, `skills:manage`
  
  Employee-data permissions are selected here as permissions only. Data scope is not configured on `role_permissions`; it is configured later on the `user_roles` assignment through `scope_type` and `scope_id`.
  - **Grievance:** `grievance:read`, `grievance:write`, `grievance:manage`
  - **Expense:** `expense:read`, `expense:create`, `expense:approve`, `expense:manage`
  - **Calendar:** `calendar:write`
  - **Notifications:** `notifications:manage`
  - **Settings:** `settings:read`, `settings:admin`, `settings:billing`, `settings:branding`, `settings:integrations`, `settings:notifications`, `settings:alerts`, `settings:system`, `settings:device`, `settings:device:configure`
  - **Users:** `users:read`, `users:manage`
  - **Roles:** `roles:read`, `roles:manage`, `access:approve`
  - **Billing:** `billing:read`, `billing:manage`
  - **Integrations:** `integrations:read`, `integrations:manage`
  - **Agent:** `agent:command`, `agent:register`, `agent:manage`, `agent:view-health`
  - **Verification:** `verification:view`, `verification:review`, `verification:configure`
  - **Chat:** `chat:read`, `chat:write`, `chat:manage`
  - **Tasks:** `tasks:read`, `tasks:write`, `tasks:approve`, `tasks:delete`
  - **Time Tracking:** `time:read`, `time:write`, `time:approve`
  - **Projects:** `projects:read`, `projects:write`, `projects:create`
  - **Work Management:** `okr:read`, `okr:write`, `wiki:read`, `wiki:write`, `sprints:read`, `sprints:manage`, `workspaces:read`, `workspaces:create`, `workspaces:manage`, `resources:read`, `resources:manage`, `roadmaps:read`, `roadmaps:write`
  
  Each explicitly grantable permission has: checkbox, permission code, human-readable description, and module badge. "Select All" per category. Search/filter across assignable permissions. Universal auto-grants are shown without checkboxes.
- **API:** N/A (client-side selection)
- **Backend:** N/A
- **Validation:** At least one explicitly grantable permission must be selected. Universal permissions cannot be selected, submitted, added, or removed.
- **DB:** None

### Step 4: Save Role
- **UI:** Click "Save Role" button. Loading spinner
- **API:** `POST /api/v1/roles`
  ```json
  {
    "name": "HR Business Partner",
    "description": "Can manage employees in assigned departments",
    "permissionIds": ["uuid1", "uuid2", "uuid3"]
  }
  ```
  Scope is intentionally absent from this payload. Scope is selected when assigning this role to a user.
- **Backend:** `RoleService.CreateRoleAsync()` -> [[frontend/cross-cutting/authorization|Authorization]]
  1. Validate role name is unique within tenant
  2. Create `roles` record
  3. Create `role_permissions` records for each selected permission
  4. Publish `RoleCreatedEvent`
- **Validation:** Role name must be unique within tenant. At least one permission required. Role name max 50 characters. Name cannot match system role names
- **DB:** `roles`, `role_permissions`

### Step 5: Security Role Available for Assignment
- **UI:** Redirect to security role detail page showing: role name, description, permission list, "Assign to Users" button, "Edit" button. Role now appears in security-role dropdowns such as user invitation and employee profile. It does not appear in team creation.
- **API:** N/A (navigation)
- **Backend:** Role is immediately available in all role selection queries
- **Validation:** N/A
- **DB:** None

## Variations

### When cloning an existing role
- From role list, click a role -> "Clone Role" button
- Pre-fills all permissions from the source role
- Admin modifies name, description, and adjusts permissions
- Saves as a new independent role (no link to source)

### When editing an existing custom role
- From role detail, click "Edit"
- Modify name, description, or permissions
- On save: all users with this role immediately get updated permissions
- Active sessions pick up new permissions on next token refresh (within 15 minutes)

### When role is used by a Position Access Template
- A security role created here can be selected by an authorized admin in a position access template.
- Employees assigned to that position do not receive the role directly from the role catalog. The backend creates a scoped `user_roles` grant only after the position-template grant is confirmed or approved.
- Changes to the role permissions affect only employees who already have an active confirmed security role assignment.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate role name | `409 Conflict` returned | "A role with this name already exists" |
| No permissions selected | `400 Bad Request` returned | "At least one permission must be selected" |
| System role edit attempt | `403 Forbidden` returned | "System roles cannot be modified" |
| Role name too long | `400 Bad Request` returned | "Role name must be 50 characters or fewer" |

## Events Triggered

- `RoleCreatedEvent` -> [[backend/messaging/event-catalog|Event Catalog]] - consumed by audit logging
- `AuditLogEntry` (action: `role.created`) -> [[modules/auth/audit-logging/overview|Audit Logging]]

## Related Flows

- [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] - assign permissions to roles or override per employee
- [[Userflow/Auth-Access/user-invitation|User Invitation]] - assign role during user invitation
- [[Userflow/Org-Structure/position-setup|Position Setup]] - configure position access templates that generate scoped grants after confirmation or approval
- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]] - role assigned during onboarding

## Module References

- [[frontend/cross-cutting/authorization|Authorization]] - RBAC implementation, role and permission management
- [[security/rbac-frontend|Rbac Frontend]] - role management UI components
- [[frontend/cross-cutting/authentication|Authentication]] - backend session metadata includes permissions from assigned role

