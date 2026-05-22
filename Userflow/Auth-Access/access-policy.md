# Access Policy Reference

**Area:** Auth & Access
**Related:** [[Userflow/Auth-Access/permissions-reference|Permissions Reference]] · [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] · [[Userflow/Auth-Access/role-creation|Role Creation]]

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
| `direct_reports` | Employees whose `reports_to_id` = this user (depth = 1) | Manager approvals |
| `reporting_tree` | All employees anywhere below this user in the org tree (depth ≥ 1) | Manager read access |
| `department` | All active employees in the same department | Dept-level HR support |
| `department_tree` | All active employees in the dept's full org subtree | Department heads |
| `org_unit_tree` | All active employees under this user's org unit | Regional managers |
| `organization` | All active employees in the tenant | HR, Payroll, Executives |

---

## Which Permissions Use Access Policy

Access policy applies to permissions that operate on **employee records**. Tenant-wide permissions (`settings:admin`, `analytics:view`, `payroll:run`, `org:manage`, etc.) are not scoped by access policy — they apply tenant-wide and are controlled by the permission alone.

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

## Assigning Access Policies

### Through a Role

When configuring a role's permissions in the permission browser, employee-data permissions display an **access policy picker** inline. The selected policy applies to all users who hold that role.

Example — "Team Manager" role configuration:

| Permission | Access Policy |
|---|---|
| `leave:read` | `reporting_tree` |
| `leave:approve` | `direct_reports` |
| `attendance:read` | `reporting_tree` |
| `attendance:approve` | `direct_reports` |
| `performance:read` | `reporting_tree` |
| `employees:read` | `reporting_tree` |

Example — "HR Generalist" role configuration:

| Permission | Access Policy |
|---|---|
| `employees:read` | `organization` |
| `employees:write` | `organization` |
| `leave:read` | `organization` |
| `leave:manage` | `organization` |
| `attendance:read` | `organization` |

### Per-Employee Override

An employee's permission override can specify a different access policy than their role default. For example, promoting an employee to department head gives them `attendance:read` with `department` policy even if their role default is `reporting_tree`.

---

## How the Backend Uses Access Policy

The backend resolves access policy at query time. The frontend never receives employee ID lists to send back.

**Pattern for list endpoints:**

```
Frontend: GET /api/leave/requests?view=team
Backend:
  1. User has leave:read → ✓
  2. Access policy for leave:read on this user → reporting_tree
  3. Resolve descendant employee IDs from employee_hierarchy closure table
  4. Filter leave requests to those employees
  5. Return filtered results
```

**Pattern for write/approve actions:**

```
Frontend: POST /api/leave/requests/{id}/approve
Backend:
  1. User has leave:approve → ✓
  2. Access policy for leave:approve on this user → direct_reports
  3. Verify target employee is in resolved scope
  4. If not in scope → 403 Forbidden
  5. If in scope → proceed with approval
```

---

## The Employee Hierarchy Closure Table

The backend maintains an `employee_hierarchy` table for efficient scope resolution:

| Column | Description |
|---|---|
| `ancestor_employee_id` | Manager or senior in the hierarchy |
| `descendant_employee_id` | Report or subordinate |
| `depth` | Steps apart: 1 = direct report, 2 = skip-level, etc. |

Every employee also has a self-row (`ancestor = descendant`, `depth = 0`).

**Query patterns:**

```sql
-- direct_reports
WHERE tenant_id = @t AND ancestor_employee_id = @me AND depth = 1

-- reporting_tree
WHERE tenant_id = @t AND ancestor_employee_id = @me AND depth >= 1
```

The table is rebuilt for the affected subtree whenever `employee.reports_to_id` changes. No recursive application-code traversal at query time.

---

## App Context — What the Frontend Receives

On session start, the frontend calls:

```
GET /api/v1/me/app-context
```

The backend returns effective capabilities (permission + policy pairs) and the resolved navigation items for this user:

```json
{
  "employeeId": "uuid",
  "displayTitle": "Engineering Manager",
  "modules": ["leave", "attendance", "calendar"],
  "capabilities": [
    { "permission": "leave:read",    "policy": "reporting_tree", "source": "role" },
    { "permission": "leave:approve", "policy": "direct_reports", "source": "role" }
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

**Bypass grants (Path C in [[Userflow/Auth-Access/permission-assignment|Permission Assignment]])** are for exceptional access that no named policy covers — temporary person-specific grants, feature-scoped delegation, or cross-company scenarios.

Normal HR, Payroll, and Executive access uses `organization` policy on the relevant permissions — **not** bypass grants. Bypass grants should be rare and always time-bounded.

---

## Default Policy

When a permission is assigned to a role without selecting an access policy, the system defaults to `self`. The user can only act on their own data until a policy is explicitly configured.

This means a newly created role with `leave:read` but no policy set will only return the current user's own leave records — it will not silently expose team data.
