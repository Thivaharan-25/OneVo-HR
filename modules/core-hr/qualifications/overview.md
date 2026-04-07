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

- [[core-hr|Core HR Module]]
- [[employee-profiles]]
- [[employee-lifecycle]]
- [[onboarding]]
- [[offboarding]]
- [[compensation]]
- [[dependents-contacts]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[data-classification]]
- [[compliance]]
- [[shared-kernel]]
- [[WEEK2-core-hr-profile]]
