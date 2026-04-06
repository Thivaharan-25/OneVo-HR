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
- [ ] `leave_balances_audit` — append-only balance change log
- [ ] Workflow integration for approval routing (manager → HR for long leave)
- [ ] Domain events: `LeaveRequested`, `LeaveApproved`, `LeaveRejected`, `LeaveCancelled`
- [ ] `LeaveApproved` → update `presence_sessions` status to `on_leave`
- [ ] `GET /api/v1/leave/calendar` — team leave calendar view
- [ ] `GET /api/v1/leave/requests/me` — own requests (`leave:read-own`)
- [ ] Unit tests ≥80% coverage

## Related Files

- [[leave]] — module architecture
- [[core-hr]] — employee context
- [[workforce-presence]] — presence status update
- [[shared-platform]] — workflow engine for approvals
