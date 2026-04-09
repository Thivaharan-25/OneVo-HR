# Qualifications

**Module:** Core HR  
**Feature:** Qualifications

---

## Purpose

Manages employee qualifications (degrees, certifications, licenses) and previous work history.

## Database Tables

### `employee_qualifications`
Fields: `qualification_type` (`degree`, `certification`, `license`), `title`, `institution`, `year_obtained`, `expiry_date`, `document_file_id`.

### `employee_work_history`
Fields: `company_name`, `job_title`, `start_date`, `end_date`, `reason_for_leaving`.

## Related

- [[modules/core-hr/overview|Core HR Module]]
- [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- [[modules/core-hr/onboarding/overview|Onboarding]]
- [[modules/core-hr/offboarding/overview|Offboarding]]
- [[modules/core-hr/compensation/overview|Compensation]]
- [[modules/core-hr/dependents-contacts/overview|Dependents Contacts]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/data-classification|Data Classification]]
- [[security/compliance|Compliance]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV1-core-hr-profile|DEV1: Core HR Profile]]
