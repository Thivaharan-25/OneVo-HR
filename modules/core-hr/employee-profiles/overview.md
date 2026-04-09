# Employee Profiles

**Module:** Core HR  
**Feature:** Employee Profiles

---

## Purpose

Central employee data management — profiles, addresses, emergency contacts, and custom fields.

## Database Tables

### `employees`
Central hub entity. Linked 1:1 to `users` via `user_id`. Self-referencing `manager_id` forms reporting hierarchy.

Key columns: `id`, `tenant_id`, `user_id`, `employee_number`, `first_name`, `last_name`, `email`, `phone`, `date_of_birth` (PII), `gender`, `nationality_id`, `department_id`, `job_title_id`, `manager_id`, `legal_entity_id`, `employment_type`, `employment_status`, `work_mode`, `hire_date`, `probation_end_date`, `termination_date`, `avatar_file_id`, `is_deleted` (soft delete).

### `employee_addresses`
Address records per employee: `address_type` (`permanent`, `current`, `emergency`), `address_json`, `is_primary`.

### `employee_emergency_contacts`
Emergency contact records: `name`, `relationship`, `phone`, `email`, `is_primary`.

### `employee_custom_fields`
Extensible custom fields: `field_name`, `field_value`, `field_type` (`text`, `number`, `date`, `boolean`, `select`).

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/employees` | `employees:read` | List employees (paginated) |
| GET | `/api/v1/employees/{id}` | `employees:read` | Get employee detail |
| POST | `/api/v1/employees` | `employees:write` | Create employee |
| PUT | `/api/v1/employees/{id}` | `employees:write` | Update employee |
| DELETE | `/api/v1/employees/{id}` | `employees:delete` | Soft delete |
| GET | `/api/v1/employees/me` | `employees:read-own` | Get own profile |
| GET | `/api/v1/employees/{id}/team` | `employees:read-team` | Get direct reports |

## Related

- [[modules/core-hr/overview|Core HR Module]]
- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- [[modules/core-hr/onboarding/overview|Onboarding]]
- [[modules/core-hr/offboarding/overview|Offboarding]]
- [[modules/core-hr/compensation/overview|Compensation]]
- [[modules/core-hr/qualifications/overview|Qualifications]]
- [[modules/core-hr/dependents-contacts/overview|Dependents Contacts]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/data-classification|Data Classification]]
- [[security/compliance|Compliance]]
- [[backend/shared-kernel|Shared Kernel]]
- [[code-standards/logging-standards|Logging Standards]]
- [[current-focus/DEV1-core-hr-profile|DEV1: Core HR Profile]]
