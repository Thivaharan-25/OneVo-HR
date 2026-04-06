# WEEK2: Core HR — Employee Profile

**Status:** Planned
**Priority:** Critical
**Assignee:** Dev 1
**Sprint:** Week 2 (Apr 14-18)
**Module:** CoreHR

## Description

Implement full employee profile CRUD: personal details, addresses, dependents, qualifications, work history, salary history, bank details (encrypted), manager hierarchy, and custom fields.

## Acceptance Criteria

- [ ] `employees` table + full CRUD endpoints
- [ ] Employee number auto-generation (tenant-scoped sequence)
- [ ] 1:1 linking to `users` via `user_id`
- [ ] Manager hierarchy via self-referencing `manager_id` (CTE queries for org tree)
- [ ] `employee_addresses` CRUD (permanent, current, emergency)
- [ ] `employee_dependents` CRUD
- [ ] `employee_qualifications` CRUD with document upload
- [ ] `employee_work_history` CRUD
- [ ] `employee_salary_history` — append-only, new entry on salary change
- [ ] `employee_bank_details` — **encrypted** `account_number_encrypted` via `IEncryptionService` (AES-256)
- [ ] `employee_emergency_contacts` CRUD
- [ ] `employee_custom_fields` CRUD (tenant-configurable)
- [ ] Avatar upload via `IFileService`
- [ ] `GET /api/v1/employees/me` (own profile, `employees:read-own`)
- [ ] `GET /api/v1/employees/{id}/team` (direct reports, `employees:read-team`)
- [ ] Cursor-based pagination on employee list
- [ ] FluentValidation for all create/update commands
- [ ] Unit tests ≥80% coverage

## Related Files

- [[core-hr]] — module architecture
- [[shared-kernel]] — BaseEntity, BaseRepository, IEncryptionService
- [[data-classification]] — PII fields, encryption requirements
- [[module-catalog]] — dependencies
