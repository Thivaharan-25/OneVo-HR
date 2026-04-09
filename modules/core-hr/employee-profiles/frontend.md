# Page: Employee Management

**Route:** `/hr/employees` (list), `/hr/employees/[id]` (detail), `/hr/employees/new` (create)
**Permission:** `employees:read` (list/detail), `employees:write` (create/edit)

## Purpose

Central employee directory with search, filters, and CRUD. Links to all HR data for an employee.

## List Layout

```
┌─────────────────────────────────────────────────────────────┐
│ PageHeader: "Employees"                   [+ Add Employee]  │
├─────────────────────────────────────────────────────────────┤
│ [Search by name/email] [Department ▼] [Status ▼] [Job ▼]   │
├─────────────────────────────────────────────────────────────┤
│ Employee Table                                              │
│ ┌──────┬────────┬────────┬──────────┬─────────┬──────────┐ │
│ │ Name │ Email  │ Dept   │ Job Title│ Status  │ Actions  │ │
│ ├──────┼────────┼────────┼──────────┼─────────┼──────────┤ │
│ │ J.D. │ j@...  │ Eng    │ Sr Dev   │ 🟢 Act  │ [View]   │ │
│ │ M.K. │ m@...  │ Sales  │ AE       │ 🟢 Act  │ [View]   │ │
│ │ A.T. │ a@...  │ Supp   │ Agent    │ 🔴 Term │ [View]   │ │
│ └──────┴────────┴────────┴──────────┴─────────┴──────────┘ │
│ Pagination (cursor-based)                                   │
└─────────────────────────────────────────────────────────────┘
```

## Detail Layout

```
┌─────────────────────────────────────────────────────────────┐
│ ← Back  "John Doe"  [Edit] [Offboard ▼]                    │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│ Status   │ Dept     │ Manager  │ Joined   │ Employment     │
│ Active   │ Eng      │ Jane S.  │ 2024-01  │ Full-time      │
├──────────┴──────────┴──────────┴──────────┴────────────────┤
│                                                             │
│ [Profile | Leave | Performance | Payroll | Documents | Activity] │
│                                                             │
│ Tab Content Area                                            │
│ (Each tab loads relevant data for this employee)            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Detail Tabs

| Tab | Permission | Data Source |
|:----|:-----------|:-----------|
| Profile | `employees:read` | `GET /employees/{id}` |
| Leave | `leave:read` | `GET /leave/requests?employeeId={id}` |
| Performance | `performance:read` | `GET /performance/reviews?employeeId={id}` |
| Payroll | `payroll:read` | `GET /payroll/slips?employeeId={id}` |
| Documents | `documents:read` | `GET /documents?employeeId={id}` |
| Activity | `workforce:view` | `GET /activity/summary/{id}?date=today` |

**Activity tab** only visible if:
1. User has `workforce:view` permission
2. Monitoring is enabled for this employee (check toggles + overrides)

## Data Sources

| Component | API |
|:----------|:----|
| Employee list | `GET /employees?search=&department=&status=&cursor=` |
| Employee detail | `GET /employees/{id}` |
| Create employee | `POST /employees` |
| Update employee | `PUT /employees/{id}` |

## Interactions

- Search filters update URL params via nuqs (shareable, bookmarkable)
- Click row → navigate to `/hr/employees/{id}`
- "Add Employee" → navigate to `/hr/employees/new` (form page)
- Detail tabs use lazy loading (data fetched on tab switch)
- "Offboard" dropdown: Terminate, Resign, Retire (triggers workflow)

## Empty States

- **No employees:** "No employees found. Add your first employee to get started."
- **No results for filter:** "No employees match your filters. Try adjusting your search."

## Related

- [[modules/core-hr/employee-profiles/overview|Employee Profiles Overview]]
- [[modules/core-hr/employee-profiles/end-to-end-logic|Employee Profiles — End-to-End Logic]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/data-classification|Data Classification]]
