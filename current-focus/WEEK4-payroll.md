# WEEK4: Payroll Module

**Status:** Planned
**Priority:** High
**Assignee:** Dev 3
**Sprint:** Week 4 (Apr 28 – May 2)
**Module:** Payroll

## Description

Implement payroll providers, tax engines, allowances, pensions, and batch payroll execution. Reads actual worked hours from [[workforce-presence]] and leave data from [[leave]].

## Acceptance Criteria

- [ ] `payroll_providers` table + CRUD (internal, ADP, Oracle)
- [ ] `payroll_connections` table — legal entity to provider mapping (uses `tenant_id`)
- [ ] `tax_configurations` table — country-specific progressive tax brackets in JSONB
- [ ] `allowance_types` table + CRUD (uses `tenant_id`)
- [ ] `employee_allowances` table — per-employee allowance assignments
- [ ] `pension_plans` table + CRUD (uses `tenant_id`)
- [ ] `employee_pension_enrollments` table
- [ ] `payroll_runs` table — batch execution with pessimistic locking (`SELECT FOR UPDATE`)
- [ ] Payroll run flow: draft → processing → completed/failed
- [ ] Never run payroll in parallel for same tenant — use Hangfire distributed lock
- [ ] `payslips` table — per-employee breakdown with `worked_hours` from `IWorkforcePresenceService`
- [ ] Payslip includes: base_salary + allowances - deductions - tax - pension = net_pay
- [ ] `payroll_adjustments` table — bonus, deduction, reimbursement, penalty
- [ ] `payroll_audit_trail` table — all payroll actions logged
- [ ] Leave days deduction from `ILeaveService`
- [ ] Overtime hours from overtime_requests (approved only)
- [ ] Unit tests ≥80% coverage

## Related

- [[payroll]] — module architecture
- [[workforce-presence]] — actual worked hours via IWorkforcePresenceService
- [[leave]] — leave deductions via ILeaveService
- [[core-hr]] — salary history and bank details
- [[multi-tenancy]] — tenant-scoped payroll providers and runs
- [[WEEK1-org-structure]] — legal entities linked to payroll connections
- [[WEEK2-core-hr-profile]] — salary history and encrypted bank details consumed here
- [[WEEK2-core-hr-lifecycle]] — EmployeeTerminated triggers final payroll run
- [[WEEK2-workforce-presence-setup]] — IWorkforcePresenceService for worked hours
- [[WEEK2-workforce-presence-biometric]] — approved overtime_requests consumed here
- [[WEEK3-leave]] — ILeaveService for leave day deductions
