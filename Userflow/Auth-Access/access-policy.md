# Access Policy Reference

**Area:** Auth & Access
**Related:** [[Userflow/Auth-Access/permissions-reference|Permissions Reference]] Â· [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] Â· [[Userflow/Auth-Access/role-creation|Role Creation]]

---

## What Is an Access Policy?

A **permission** answers *what action* a user can perform. An **access policy** answers *whose data* that action can reach.

Access policy must not become a required per-permission setup step for every role. Role templates and assignment flows should provide practical defaults, such as self-service for employees, position-derived reporting hierarchy for managers, and position access templates for sensitive HR/administrative coverage. Administrators change access policy only when they need broader or exceptional employee-data access.

Example:

| User | Permission | Access Policy | Effect |
|---|---|---|---|
| Team Manager | `leave:read` | `ReportingTree` | Sees leave records for all direct and indirect reports |
| HR Generalist | `leave:read` | `Organization` | Sees leave records for all active employees in the tenant |
| Department-level approver | `leave:approve` | `DirectReports` | Can only approve leave for employees who report directly to them |

The same permission (`leave:read`) can produce a different data scope from assignment context without needing separate permission codes. The normal default for manager-style access is resolved from position hierarchy.

---

## Named Access Policies

| Policy | Data Scope | Typical Assignment |
|---|---|---|
| `Own` | Own employee record only | Default when no policy is set |
| `DirectReports` | Employees directly below this user in `employee_hierarchy_closure` (depth = 1), derived from position hierarchy | Manager approvals |
| `ReportingTree` | All employees anywhere below this user in the org tree (depth >= 1) | Manager read access |
| `Department` | All active employees in the selected department | Dept-level support or approved coverage |
| `DepartmentTree` | All active employees in the dept's full org subtree | Department-level leadership |
| `Team` | All active employees in the selected team | Team-level support or approved coverage |
| `Organization` | All active employees in the tenant | Explicit organization-wide employee-data authority |

---

## Which Permissions Use Access Policy

Access policy applies to permissions that operate on **employee records**. Tenant-wide or context-scoped permissions (`settings:admin`, `analytics:view`, `payroll:run`, `org:manage`, WorkSync workspace/project actions, etc.) are not governed by this employee access-policy table alone. They are controlled by the permission plus their own context, such as legal entity, workspace role, project membership, workflow assignment, or approved participation request.

| Module | Permissions governed by access policy |
|---|---|
| Employees | `employees:read`, `employees:write`, `employees:delete` |
| Leave | `leave:read`, `leave:approve`, `leave:create` |
| Attendance | `attendance:read`, `attendance:approve`, `attendance:write` |
| Performance | `performance:read`, `performance:write` |
| Skills | `skills:read`, `skills:write`, `skills:validate` |
| Expense | `expense:read`, `expense:approve` |
| Documents | `documents:read`, `documents:write`, `documents:approve` |
| Tasks | Employee-data views attached to tasks, such as subordinate workload summaries. Project task visibility itself is controlled by `project_members`, `workspace_members`, and project/workspace context. |
| Time | `time:read`, `time:approve` |

---

## Assigning Access Scope

### Through a Security Role Assignment

Roles define what permissions exist. `user_roles.scope_type` and `user_roles.scope_id` define whose employee data those permissions can reach for a specific user assignment.

This should be template-driven for normal setup. Do not ask administrators to select a scope for every permission on every role unless they intentionally open advanced access configuration.

Example assignments:

| User | Role | Scope Type | Scope Id | Effect |
|---|---|---|---|---|
| Team Manager | Leave Approver | `DirectReports` | null | Can approve leave for direct reports |
| HR Generalist | Employee Data Reviewer | `Organization` | null | Can access employee data across the tenant |
| Department support user | Employee Data Reviewer | `Department` | EngineeringDepartmentId | Can access employees inside Engineering |

### Through a Position Access Template

Positions can define access templates, but the position itself is not the active permission grant. A position access template generates a `user_roles` grant or an `access_grant_requests` approval record when an employee is assigned, transferred, promoted, or onboarded into that position.

Position access templates are used for default access tied to a position:

| Position | Template role | Template scope | Approval |
|---|---|---|---|
| Software Engineer | Employee | `Own` | Not required |
| Engineering Team Lead | Team Manager | `DirectReports` | Not required unless configured sensitive |
| HR Manager - Engineering | HR Manager | `Department = EngineeringDepartmentId` | Required |

For HR roles, the scope is the coverage area, not necessarily the HR employee's own department. If an HR employee sits in the HR department but supports Engineering, the template should grant `Department = EngineeringDepartmentId`.

If a template has `requires_approval = true` and the actor assigning/transferring/promoting the employee does not have `roles:manage` or `access:approve`, the backend creates an access approval request instead of activating the grant. If the actor already has `roles:manage` or `access:approve`, the backend may materialize the grant immediately after the actor confirms the generated access.

Approver resolution always uses the target position's department:

1. Find users with `roles:manage` or `access:approve` whose own scope covers the target department.
2. If none exist, find tenant-wide users with `roles:manage` or `access:approve`.
3. If none exist, route to Tenant Admin.
4. If multiple approvers match a step, notify all; the first approval wins.

Users without `roles:manage` or `access:approve` must not see role lists, permission details, or access editing controls during onboarding, transfer, promotion, or position assignment. They may only see a neutral message such as "Access changes require approval."

For pooled positions, editing the position template affects all current and future occupants. The UI must force authorized users to choose between:

- Apply to the position template, affecting all occupants.
- Apply only to this employee, creating an employee-specific override or user role grant.

### Per-Employee Permission Override

A `user_permission_overrides` row can also carry `scope_type` and `scope_id`. Use this for explicit individual grants or revokes that differ from the role assignment scope.

## How the Backend Uses Access Policy

The backend resolves access policy at query time. The frontend never receives employee ID lists to send back.

**Pattern for list endpoints:**

```
Frontend: GET /api/leave/requests?view=team
Backend:
  1. User has leave:read â†’ âœ“
  2. Resolve employee-data scope from assignment defaults, active position-template grants materialized in `user_roles`, hierarchy, approved coverage, or explicit override
  3. Resolve descendant employee IDs from employee_hierarchy_closure table
  4. Filter leave requests to those employees
  5. Return filtered results
```

**Pattern for write/approve actions:**

```
Frontend: POST /api/leave/requests/{id}/approve
Backend:
  1. User has leave:approve â†’ âœ“
  2. Resolve employee-data scope from assignment defaults, workflow assignment, active position-template grants materialized in `user_roles`, hierarchy, approved coverage, or explicit override
  3. Verify target employee is in resolved scope
  4. If not in scope â†’ 403 Forbidden
  5. If in scope â†’ proceed with approval
```

---

## The Employee Hierarchy Closure Table

The backend maintains an `employee_hierarchy_closure` table for efficient current-scope resolution. The table is derived from current `position_reporting_history` and active `position_assignments`; it is not source of truth and is not used for historical reporting:

| Column | Description |
|---|---|
| `ancestor_employee_id` | Manager or senior in the hierarchy |
| `descendant_employee_id` | Report or subordinate |
| `depth` | Steps apart: 1 = direct report, 2 = skip-level, etc. |

Every employee may also have a self-row (`ancestor = descendant`, `depth = 0`) if needed by query conventions.

**Query patterns:**

```sql
-- DirectReports
WHERE tenant_id = @t AND ancestor_employee_id = @me AND depth = 1

-- ReportingTree
WHERE tenant_id = @t AND ancestor_employee_id = @me AND depth >= 1
```

The table is rebuilt for the affected branch whenever current position reporting or position assignments change. No recursive application-code traversal is required at query time. Historical reporting uses `position_assignments` plus `position_reporting_history` instead of this cache.

---

## App Context â€” What the Frontend Receives

On session start, the frontend calls:

```
GET /api/v1/me/app-context
```

The backend returns effective capabilities (permission + scope pairs) and the resolved navigation items for this user:

```json
{
  "employeeId": "uuid",
  "displayTitle": "Engineering Manager",
  "modules": ["leave", "attendance", "calendar"],
  "capabilities": [
  ],
  "navigation": [
    "my-dashboard",
    "my-leave",
    "my-attendance",
    "team-dashboard",
    "team-leave",
    "team-leave-approvals",
    "team-attendance"
  ]
}
```

Angular renders the `navigation` array exactly as returned. No navigation is computed from role name or display title.

---

## Relation to Bypass Grants

**Bypass grants (Path C in [[Userflow/Auth-Access/permission-assignment|Permission Assignment]])** are for exceptional access that no named policy covers â€” temporary person-specific grants, feature-scoped delegation, or cross-company scenarios.

Normal HR, Payroll, and Executive access uses `Organization` policy on the relevant permissions - **not** bypass grants. Bypass grants should be rare and always time-bounded.

---

## Default Policy

When a security role assignment has no explicit scope, the system defaults to `Own`. The user can only act on their own data until a scope is explicitly configured on `user_roles` or a scoped override.

This means a newly created role with `leave:read` but no policy set will only return the current user's own leave records â€” it will not silently expose team data.

