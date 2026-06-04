# Access Policy Reference

**Area:** Auth & Access
**Related:** [[Userflow/Auth-Access/permissions-reference|Permissions Reference]] Â· [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] Â· [[Userflow/Auth-Access/role-creation|Role Creation]]

---

## What Is an Access Policy?

A **permission** answers *what action* a user can perform. An **access policy** answers *whose data* that action can reach. The two are configured independently.

Example:

| User | Permission | Access Policy | Effect |
|---|---|---|---|
| Team Manager | `leave:read` | `reporting_tree` | Sees leave records for all direct and indirect reports |
| HR Generalist | `leave:read` | `organization` | Sees leave records for all active employees in the tenant |
| Department Head | `leave:approve` | `direct_reports` | Can only approve leave for employees who report directly to them |

The same permission (`leave:read`) produces a completely different data scope for different roles without needing separate permission codes.

---

## Named Access Policies

| Policy | Data Scope | Typical Assignment |
|---|---|---|
| `self` | Own employee record only | Default when no policy is set |
| `direct_reports` | Employees directly below this user in `employee_hierarchy_closure` (depth = 1), derived from position hierarchy | Manager approvals |
| `reporting_tree` | All employees anywhere below this user in the org tree (depth â‰¥ 1) | Manager read access |
| `department` | All active employees in the same department | Dept-level HR support |
| `department_tree` | All active employees in the dept's full org subtree | Department heads |
| `org_unit_tree` | All active employees under this user's org unit | Regional managers |
| `organization` | All active employees in the tenant | HR, Payroll, Executives |

---

## Which Permissions Use Access Policy

Access policy applies to permissions that operate on **employee records**. Tenant-wide permissions (`settings:admin`, `analytics:view`, `payroll:run`, `org:manage`, etc.) are not scoped by access policy â€” they apply tenant-wide and are controlled by the permission alone.

| Module | Permissions governed by access policy |
|---|---|
| Employees | `employees:read`, `employees:write`, `employees:delete` |
| Leave | `leave:read`, `leave:approve`, `leave:create` |
| Attendance | `attendance:read`, `attendance:approve`, `attendance:write` |
| Performance | `performance:read`, `performance:write` |
| Skills | `skills:read`, `skills:write`, `skills:validate` |
| Expense | `expense:read`, `expense:approve` |
| Documents | `documents:read`, `documents:write`, `documents:approve` |
| Tasks | `tasks:read`, `tasks:approve` |
| Time | `time:read`, `time:approve` |

---

## Assigning Access Scope

### Through a Security Role Assignment

Roles define what permissions exist. `user_roles.scope_type` and `user_roles.scope_id` define whose employee data those permissions can reach for a specific user assignment.

Example assignments:

| User | Role | Scope Type | Scope Id | Effect |
|---|---|---|---|---|
| Team Manager | Leave Approver | `DirectReports` | null | Can approve leave for direct reports |
| HR Generalist | HR Manager | `Organization` | null | Can access employee data across the tenant |
| Department HR | HR Manager | `Department` | EngineeringDepartmentId | Can access employees inside Engineering |

### Per-Employee Permission Override

A `user_permission_overrides` row can also carry `scope_type` and `scope_id`. Use this for explicit individual grants or revokes that differ from the role assignment scope.

## How the Backend Uses Access Policy

The backend resolves access policy at query time. The frontend never receives employee ID lists to send back.

**Pattern for list endpoints:**

```
Frontend: GET /api/leave/requests?view=team
Backend:
  1. User has leave:read â†’ âœ“
  2. Scope for `leave:read` on this user -> `DirectReports`, `Department`, `Team`, `Organization`, or `Own`
  3. Resolve descendant employee IDs from employee_hierarchy_closure table
  4. Filter leave requests to those employees
  5. Return filtered results
```

**Pattern for write/approve actions:**

```
Frontend: POST /api/leave/requests/{id}/approve
Backend:
  1. User has leave:approve â†’ âœ“
  2. Scope for `leave:approve` on this user -> `DirectReports`, `Department`, `Team`, `Organization`, or `Own`
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
-- direct_reports
WHERE tenant_id = @t AND ancestor_employee_id = @me AND depth = 1

-- reporting_tree
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

Normal HR, Payroll, and Executive access uses `organization` policy on the relevant permissions â€” **not** bypass grants. Bypass grants should be rare and always time-bounded.

---

## Default Policy

When a security role assignment has no explicit scope, the system defaults to `Own`. The user can only act on their own data until a scope is explicitly configured on `user_roles` or a scoped override.

This means a newly created role with `leave:read` but no policy set will only return the current user's own leave records â€” it will not silently expose team data.

