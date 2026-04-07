# Role Creation

**Area:** Auth & Access
**Required Permission(s):** `roles:manage`
**Related Permissions:** `users:manage` (to assign the new role to users)

---

## Preconditions

- Tenant is active
- Understanding of which permissions are needed for the role being created
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Role Management
- **UI:** Administration > Roles & Permissions. List view shows all roles: Name, Description, User Count (how many users have this role), Type (System/Custom), Created Date. System roles marked with a lock icon (cannot be deleted). "Create Role" button in top-right
- **API:** `GET /api/v1/roles`
- **Backend:** `RoleService.GetRolesAsync()` → [[authorization]]
- **Validation:** Permission check for `roles:manage`
- **DB:** `roles`, `user_roles` (for user count)

### Step 2: Click Create Role
- **UI:** Full-page form opens with sections:
  - **Basic Info:** Role Name (required, e.g., "HR Business Partner"), Description (optional, e.g., "Can manage employees in assigned departments")
  - **Permission Browser:** Accordion-style category list showing all 90+ permissions grouped by module
- **API:** `GET /api/v1/permissions` (loads all available permissions)
- **Backend:** `PermissionService.GetAllPermissionsAsync()` → [[authorization]]
- **Validation:** N/A
- **DB:** `permissions`

### Step 3: Browse and Select Permissions
- **UI:** Permission categories (accordions):
  - **Employees:** `employees:read`, `employees:read-own`, `employees:read-team`, `employees:write`, `employees:delete`
  - **Organization:** `org:read`, `org:manage`
  - **Leave:** `leave:read`, `leave:read-own`, `leave:read-team`, `leave:create`, `leave:approve`, `leave:manage`
  - **Payroll:** `payroll:read`, `payroll:read-own`, `payroll:write`, `payroll:run`, `payroll:approve`
  - **Performance:** `performance:read`, `performance:read-own`, `performance:read-team`, `performance:write`, `performance:manage`
  - **Documents:** `documents:read`, `documents:read-own`, `documents:write`, `documents:manage`
  - **Workforce Intelligence:** `workforce:view`, `workforce:manage`, `monitoring:configure`, `monitoring:view-settings`
  - **Exceptions:** `exceptions:view`, `exceptions:manage`, `exceptions:acknowledge`
  - **Analytics:** `analytics:view`, `analytics:export`
  - **Reporting:** `reports:read`, `reports:create`
  - **Skills:** `skills:read`, `skills:write`, `skills:validate`, `skills:manage`
  - **Grievance:** `grievance:read`, `grievance:write`, `grievance:manage`
  - **Expense:** `expense:read`, `expense:create`, `expense:approve`, `expense:manage`
  - **Calendar:** `calendar:read`, `calendar:write`
  - **Notifications:** `notifications:read`, `notifications:manage`
  - **Settings:** `settings:read`, `settings:admin`
  - **Users:** `users:read`, `users:manage`
  - **Roles:** `roles:read`, `roles:manage`
  - **Billing:** `billing:read`, `billing:manage`
  - **Agent:** `agent:register`, `agent:manage`, `agent:view-health`
  - **Verification:** `verification:view`, `verification:configure`
  
  Each permission has: checkbox, permission code, human-readable description, module badge. "Select All" per category. Search/filter across permissions. Selected count shown: "23 of 90+ permissions selected"
- **API:** N/A (client-side selection)
- **Backend:** N/A
- **Validation:** At least one permission must be selected
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
- **Backend:** `RoleService.CreateRoleAsync()` → [[authorization]]
  1. Validate role name is unique within tenant
  2. Create `roles` record
  3. Create `role_permissions` records for each selected permission
  4. Publish `RoleCreatedEvent`
- **Validation:** Role name must be unique within tenant. At least one permission required. Role name max 50 characters. Name cannot match system role names
- **DB:** `roles`, `role_permissions`

### Step 5: Role Available for Assignment
- **UI:** Redirect to role detail page showing: role name, description, permission list, "Assign to Users" button, "Edit" button. Role now appears in role dropdowns across the platform (user invitation, employee profile, job family setup)
- **API:** N/A (navigation)
- **Backend:** Role is immediately available in all role selection queries
- **Validation:** N/A
- **DB:** None

## Variations

### When cloning an existing role
- From role list, click a role → "Clone Role" button
- Pre-fills all permissions from the source role
- Admin modifies name, description, and adjusts permissions
- Saves as a new independent role (no link to source)

### When editing an existing custom role
- From role detail, click "Edit"
- Modify name, description, or permissions
- On save: all users with this role immediately get updated permissions
- Active sessions pick up new permissions on next token refresh (within 15 minutes)

### When role is linked to a Job Family Level
- Role created here can be assigned to a [[job-family-setup|Job Family Level]]
- Employees assigned to that job family level automatically receive this role
- Changes to the role's permissions cascade to all employees in that job family level

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate role name | `409 Conflict` returned | "A role with this name already exists" |
| No permissions selected | `400 Bad Request` returned | "At least one permission must be selected" |
| System role edit attempt | `403 Forbidden` returned | "System roles cannot be modified" |
| Role name too long | `400 Bad Request` returned | "Role name must be 50 characters or fewer" |

## Events Triggered

- `RoleCreatedEvent` → [[event-catalog]] — consumed by audit logging
- `AuditLogEntry` (action: `role.created`) → [[audit-logging]]

## Related Flows

- [[permission-assignment]] — assign permissions to roles or override per employee
- [[user-invitation]] — assign role during user invitation
- [[job-family-setup]] — link role to job family levels for automatic assignment
- [[employee-onboarding]] — role assigned during onboarding

## Module References

- [[authorization]] — RBAC implementation, role and permission management
- [[rbac-frontend]] — role management UI components
- [[authentication]] — JWT claims include permissions from assigned role
