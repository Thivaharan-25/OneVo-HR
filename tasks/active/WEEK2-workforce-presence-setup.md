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

## Related Files

- [[workforce-presence]] — module architecture
- [[configuration]] — monitoring toggles (check before processing agent data)
- [[module-catalog]] — dependencies
