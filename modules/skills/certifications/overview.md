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
- [[modules/skills/courses-learning/overview|Courses Learning]] — courses that lead to certifications
- [[modules/skills/employee-skills/overview|Employee Skills]] — skill records that may require certification evidence
- [[modules/skills/development-plans/overview|Development Plans]] — development milestones linked to certification goals
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant-scoped certification records
- [[backend/messaging/event-catalog|Event Catalog]] — expiry and renewal reminder events
- [[backend/messaging/error-handling|Error Handling]] — expiry notification job error handling
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]] — implementation task
