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

- [[core-hr|Core HR Module]]
- [[employee-profiles]]
- [[employee-lifecycle]]
- [[onboarding]]
- [[offboarding]]
- [[qualifications]]
- [[dependents-contacts]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[data-classification]]
- [[compliance]]
- [[shared-kernel]]
- [[WEEK2-core-hr-profile]]
