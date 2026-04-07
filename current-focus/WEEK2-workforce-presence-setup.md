# WEEK2: Workforce Presence — Setup

**Status:** Planned
**Priority:** Critical
**Assignee:** Dev 3
**Sprint:** Week 2 (Apr 14-18)
**Module:** WorkforcePresence

## Description

Implement shift/schedule management, presence session tracking, device sessions, and break detection. This replaces the old Attendance module.

## Acceptance Criteria

- [ ] `shifts` table + CRUD (morning, evening, night, flexible)
- [ ] `work_schedules` table + CRUD (weekly patterns)
- [ ] `schedule_templates` — reusable templates
- [ ] `employee_shift_assignments` — assign employees to shifts
- [ ] `employee_work_schedules` — employee-specific schedule overrides
- [ ] `holidays` table + CRUD (company + country holidays)
- [ ] `presence_sessions` table — **one row per employee per day**, unified from all sources
- [ ] Presence status computation: `present`, `absent`, `partial`, `on_leave`
- [ ] `device_sessions` table — multiple rows per employee per day (one per active/idle cycle)
- [ ] `break_records` table — with `auto_detected` flag for agent-detected breaks
- [ ] Break auto-detection: if agent reports idle > configurable threshold (default 15 min), create break record
- [ ] `ReconcilePresenceSessions` Hangfire job (every 5 min during work hours)
- [ ] `FlagUnresolvedAbsences` Hangfire job (daily 10 AM)
- [ ] `CloseOpenSessions` Hangfire job (daily 11:59 PM)
- [ ] `IWorkforcePresenceService` public interface implementation
- [ ] `GET /api/v1/workforce/presence/live` endpoint — real-time workforce status
- [ ] Unit tests ≥80% coverage

## Related

- [[workforce-presence]] — module architecture
- [[configuration]] — monitoring toggles (check before processing agent data)
- [[module-catalog]] — dependencies
- [[multi-tenancy]] — tenant-scoped presence data
- [[WEEK1-infrastructure-setup]] — shared kernel and EF Core setup
- [[WEEK1-shared-platform]] — agent gateway ingest data feeds into device_sessions
- [[WEEK2-workforce-presence-biometric]] — biometric events reconciled into presence_sessions (same week)
- [[WEEK3-leave]] — LeaveApproved event sets presence status to on_leave
- [[WEEK4-exception-engine]] — reads IWorkforcePresenceService for no_presence and break_exceeded rules
- [[WEEK4-payroll]] — reads IWorkforcePresenceService for worked hours
- [[WEEK4-productivity-analytics]] — aggregates from presence_sessions
