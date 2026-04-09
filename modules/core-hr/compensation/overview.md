# Compensation

**Module:** Core HR  
**Feature:** Compensation

---

## Purpose

Manages salary history and encrypted bank details.

## Database Tables

### `employee_salary_history`
Tracks salary changes with `effective_date`, `base_salary`, `currency_code`, `change_reason` (`hire`, `promotion`, `annual_review`, `adjustment`), `approved_by_id`.

### `employee_bank_details`
Bank details with `account_number_encrypted` (AES-256 via `IEncryptionService`), `routing_number`, `is_primary`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/employees/{id}/salary-history` | `payroll:read` | Salary history |
| PUT | `/api/v1/employees/{id}/bank-details` | `employees:write` | Update bank details (encrypted) |

## Related

- [[modules/core-hr/overview|Core HR Module]]
- [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- [[modules/core-hr/onboarding/overview|Onboarding]]
- [[modules/core-hr/offboarding/overview|Offboarding]]
- [[modules/core-hr/qualifications/overview|Qualifications]]
- [[modules/core-hr/dependents-contacts/overview|Dependents Contacts]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/data-classification|Data Classification]]
- [[security/compliance|Compliance]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV1-core-hr-profile|DEV1: Core HR Profile]]
