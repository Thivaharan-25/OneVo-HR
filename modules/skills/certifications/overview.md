# Certifications

**Module:** Skills & Learning  
**Feature:** Certifications

---

## Purpose

Employee certification records with expiry tracking and renewal reminders.

## Database Tables

### `employee_certifications`
Fields: `employee_id`, `course_id` (nullable), `certification_name`, `issuing_authority`, `credential_id`, `issue_date`, `expiry_date`, `status` (`active`, `expired`, `revoked`), `certificate_file_record_id`, `renewal_reminder_sent`.

## Key Business Rules

1. Hangfire job alerts 30 days before expiry, sets `renewal_reminder_sent` flag.

## Related

- [[skills|Skills Module]] — parent module
- [[courses-learning]] — courses that lead to certifications
- [[employee-skills]] — skill records that may require certification evidence
- [[development-plans]] — development milestones linked to certification goals
- [[multi-tenancy]] — tenant-scoped certification records
- [[event-catalog]] — expiry and renewal reminder events
- [[error-handling]] — expiry notification job error handling
- [[WEEK4-supporting-bridges]] — implementation task
