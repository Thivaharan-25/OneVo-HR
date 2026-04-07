# WEEK3: Leave Module

**Status:** Planned
**Priority:** High
**Assignee:** Dev 1
**Sprint:** Week 3 (Apr 21-25)
**Module:** Leave

## Description

Implement leave types, country/level-specific policies with versioning, entitlement calculation (prorated), and request/approval workflow via [[shared-platform]] workflow engine.

## Acceptance Criteria

- [ ] `leave_types` table + CRUD (Annual, Sick, Maternity, etc.) — uses `tenant_id`
- [ ] `leave_policies` table with versioning chain (`superseded_by_id`)
- [ ] Policy matching: leave type + country + job level combination
- [ ] Active policy query: `WHERE superseded_by_id IS NULL`
- [ ] `leave_entitlements` table — calculated per employee per year
- [ ] Entitlement calculation: accrual method (`annual`, `monthly`, `daily`) + proration for mid-year hires
- [ ] Carry forward logic: max days + expiry months
- [ ] `leave_requests` table + submit/approve/reject workflow
- [ ] Request validation: check sufficient balance, no overlapping requests, max consecutive days
- [ ] Calendar conflict detection: call `ICalendarConflictService` on submission, store `conflict_snapshot_json` on `leave_requests`
- [ ] Manager approval view: show conflict snapshot (at submission) + live re-check (current conflicts)
- [ ] `LeaveRequested` notification to manager includes conflict count if > 0
- [ ] `leave_balances_audit` — append-only balance change log
- [ ] Workflow integration for approval routing (manager → HR for long leave)
- [ ] Domain events: `LeaveRequested`, `LeaveApproved`, `LeaveRejected`, `LeaveCancelled`
- [ ] `LeaveApproved` → update `presence_sessions` status to `on_leave`
- [ ] `GET /api/v1/leave/calendar` — team leave calendar view
- [ ] `GET /api/v1/leave/requests/me` — own requests (`leave:read-own`)
- [ ] Unit tests ≥80% coverage

## Related

- [[leave]] — module architecture
- [[core-hr]] — employee context (country, job level for policy matching)
- [[workforce-presence]] — presence status updated on LeaveApproved
- [[shared-platform]] — workflow engine for approval routing
- [[calendar]] — conflict detection via ICalendarConflictService
- [[multi-tenancy]] — tenant-scoped leave types and policies
- [[2026-04-06-leave-calendar-conflict-detection]] — design spec for conflict detection
- [[WEEK1-shared-platform]] — workflow engine used for approval routing (built Week 1)
- [[WEEK1-org-structure]] — job levels referenced in policy matching
- [[WEEK2-core-hr-profile]] — employee country and job level used in policy matching
- [[WEEK2-workforce-presence-setup]] — presence_sessions updated on leave approval
- [[WEEK4-payroll]] — leave deductions read via ILeaveService
- [[WEEK4-supporting-bridges]] — Calendar module (ICalendarConflictService) built in Week 4
