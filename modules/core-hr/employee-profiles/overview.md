# Employee Profiles

**Module:** Core HR  
**Feature:** Employee Profiles  
**Phase:** 1

---

## Purpose

Central employee data management: profiles, addresses, emergency contacts, custom fields, assignment summary, access/override summary, and lifecycle entry points.

Employee detail is a full-page operational screen, not a side drawer. It uses section cards for About / Personal Information, Employment Status / Job Details, Policy & Access Overrides, Documents, and Lifecycle / Activity. Transfer, Promotion, and Start Offboarding launch compact actions from the detail page.

---

## Database Tables

### `employees`

Central hub entity. Linked 1:1 to `users` via `user_id`. Reporting hierarchy is resolved from active Primary Employment Assignments and the position hierarchy; employee records do not store manager references.

Key columns: `id`, `tenant_id`, `user_id`, `employee_number`, `first_name`, `last_name`, `email`, `phone`, `date_of_birth`, `gender`, `nationality_id`, `department_id`, `legal_entity_id`, `employment_type`, `employment_status`, `work_mode`, `hire_date`, `probation_end_date`, `termination_date`, `avatar_file_id`, `is_deleted`.

`department_id` and `legal_entity_id` are current profile snapshots from the Primary Employment Assignment. The source of truth for assignment history is `position_assignments`.

Employee detail is the operational center for the employee. Do not rely on one giant global Edit Profile action; each section may expose its own edit action based on permission.

### Assignment Summary

Each employee has exactly one active Primary Employment Assignment. Additional Authority Assignments may grant role/access/approval authority but do not change time off policy, attendance policy, schedule, holiday calendar, payroll context, or primary legal entity.

### `employee_addresses`

Address records per employee: `address_type`, `address_json`, `is_primary`.

### `employee_emergency_contacts`

Emergency contact records: `name`, `relationship`, `phone`, `email`, `is_primary`.

### `employee_custom_fields`

Extensible custom fields: `field_name`, `field_value`, `field_type`.

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/employees` | `employees:read` | List employees |
| GET | `/api/v1/employees/{id}` | `employees:read` | Full-page employee detail |
| POST | `/api/v1/employees` | `employees:write` | Create employee |
| PUT | `/api/v1/employees/{id}` | `employees:write` | Section-level employee update |
| DELETE | `/api/v1/employees/{id}` | `employees:delete` | Soft delete |
| GET | `/api/v1/employees/me` | `employees:read-own` | Get own profile |

---

## Related

- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- [[modules/core-hr/employee-profiles/frontend|Employee Profiles Frontend]]
- [[modules/core-hr/employee-profiles/end-to-end-logic|Employee Profiles End-to-End Logic]]
- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]]
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]]
