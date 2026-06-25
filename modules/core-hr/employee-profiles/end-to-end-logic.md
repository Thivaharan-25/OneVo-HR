# Employee Profiles - End-to-End Logic

**Module:** Core HR  
**Feature:** Employee Profiles

---

## Flow Overview

Employee Profiles is the central hub for HR data. Every employee record links 1:1 to `users` through `user_id`.

Reporting hierarchy is resolved from active Primary Employment Assignments and the position reporting tree. Employee records do not store manager references and profile commands must not accept manager fields.

---

## Full-Page Detail Read

```
GET /api/v1/employees/{id}
  -> Require employees:read with employee visibility
  -> Load employee profile
  -> Load current Primary Employment Assignment
  -> Load Additional Authority Assignments
  -> Resolve position, department, legal entity, reporting manager summary
  -> Resolve access/override summary only if caller has permission
  -> Return EmployeeDetailResponse
```

The response supports the full-page detail screen with section cards: About / Personal Information, Employment Status / Job Details, Policy & Access Overrides, Documents, and Lifecycle / Activity.

---

## Create Employee

```
POST /api/v1/employees
  -> Validate email and employee number uniqueness
  -> Validate legal entity, department, and initial position
  -> Create employees row
  -> Create PrimaryEmployment position_assignments row
  -> Initialize policy inheritance from primary assignment
  -> Publish EmployeeCreated
```

---

## Update Employee

```
PUT /api/v1/employees/{id}
  -> Validate actor has employees:write
  -> Fetch employee by tenant and id
  -> Reject manager fields; reporting belongs to Org Structure positions
  -> Apply section-level profile changes
  -> Write employee_lifecycle_events when relevant
  -> Return EmployeeDetailResponse
```

Section edits are preferred over one global edit action.

---

## Assignment Rules

- Exactly one active Primary Employment Assignment per employee.
- Primary assignment controls primary legal entity, time off policy, attendance policy, work schedule, holiday calendar, and payroll/statutory context.
- Additional Authority Assignments may grant role/access/approval authority.
- Additional Authority Assignments do not change policy inheritance.
- One employee cannot hold two active employment assignments inside the same legal entity.
- Cross-legal-entity authority assignments are allowed.
- Cross-legal-entity reporting lines are not allowed.

---


```
  -> Resolve active primary assignment
  -> Query employee_hierarchy_closure where ancestor_employee_id = id and depth = 1
  -> Return active direct reports
```

---

## Lifecycle Actions

Transfer and Promotion are compact modals launched from the full-page detail header. They load target position access impact and create `access_grant_requests` when approval is required. They do not invoke Workflow Engine in Phase 1.

---

## Error Scenarios

| Error | Handling |
|:---|:---|
| Duplicate email or employee number | 409 |
| Invalid legal entity / department / position | 422 |
| Manager field supplied | 422; use position reporting instead |
| Second active employment assignment in same legal entity | 422 |
| Missing employee visibility | 403 |

---

## Related

- [[modules/core-hr/employee-profiles/overview|Employee Profiles Overview]]
- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]]
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]]
