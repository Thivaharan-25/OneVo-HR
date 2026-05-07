# DEV6: Frontend HR + Workforce UI

**Track:** Frontend
**Primary ownership:** HR screens, leave, calendar, presence, agent management UI
**Current Unfinished Task:** Task 1 - HR employee screens
**Blocked By:** DEV5 app foundation; DEV2 Core HR API for live data

---

## ADE Instructions

When Dev 6 asks to continue, start with the first unchecked item in **Current Unfinished Task**. If APIs are not ready, create MSW handlers that match the expected DTOs and record the backend contract gap.

**Phase 1 scope cap:** DEV6 builds only Tasks 1-4 in this file. Do not build standalone identity verification, exception, discrepancy, productivity analytics, skills, org admin, notification center, or broad configuration screens in Phase 1 unless a new DEV9 build pack is created.

---

## Task 1: HR Employee Screens

**Goal:** build employee list, detail, create, edit, onboarding, and offboarding screens.

**Requires:** DEV5 Tasks 1-4 complete  
**Live integration:** DEV2 Task 1 (use MSW until ready) - Contract: `current-focus/contracts/hr-employee.md`

### Acceptance Criteria

- [ ] Employee list supports search, filters, cursor pagination, and status badges.
- [ ] Employee detail shows profile, employment, manager, department, team, and activity summary.
- [ ] Create/edit form validates required fields and server errors.
- [ ] Onboarding flow supports staged employee creation.
- [ ] Offboarding flow supports reason, date, asset checklist placeholder, and confirmation.
- [ ] Tests cover list render, create validation, edit save, and forbidden state.

### References

- [[Userflow/Employee-Management/profile-management|Profile Management]] (Userflow/Employee-Management/profile-management.md)
- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]] (Userflow/Employee-Management/employee-onboarding.md)
- [[Userflow/Employee-Management/employee-offboarding|Employee Offboarding]] (Userflow/Employee-Management/employee-offboarding.md)
- [[frontend/design-system/patterns/form-patterns|Form Patterns]] (frontend/design-system/patterns/form-patterns.md)

### Verification

```bash
npm run test -- employee
npm run build
```

---

> **Parallel group** — Tasks 2, 3, and 4 all require DEV5 Tasks 1–4 and DEV6 Task 1, but are independent of each other. Run all three simultaneously.

## Task 2: Leave + Calendar Screens

**Goal:** build leave and calendar workflows used by employees and managers.

**Requires:** DEV5 Tasks 1-4 and DEV6 Task 1 complete  
**Live integration:** DEV2 Task 3 (use MSW until ready) - Contract: `current-focus/contracts/hr-employee.md`

### Acceptance Criteria

- [ ] Leave balance view shows available, used, pending, and upcoming leave.
- [ ] Leave request form validates leave type, date range, overlap, and reason.
- [ ] Manager approval screen supports approve, reject, and comment.
- [ ] Calendar screen combines holidays, shifts, leave, and company events.
- [ ] Shift and holiday admin screens exist.
- [ ] Calendar holiday settings screen lets admins disable country holiday sync or override the country calendar from the legal entity default.
- [ ] Google/Outlook calendar connection controls support connect, disconnect, sync direction, sync status, and manual sync.
- [ ] Tests cover request validation, approval action, calendar event render, holiday override controls, and external calendar connection states.

### References

- [[Userflow/Leave/leave-request-submission|Leave Request Submission]] (Userflow/Leave/leave-request-submission.md)
- [[Userflow/Leave/leave-approval|Leave Approval]] (Userflow/Leave/leave-approval.md)
- [[Userflow/Calendar/calendar-event-creation|Calendar Event Creation]] (Userflow/Calendar/calendar-event-creation.md)
- [[Userflow/Calendar/calendar-integrations|Calendar Integrations]] (Userflow/Calendar/calendar-integrations.md)
- [[modules/calendar/overview|Calendar Module]] (modules/calendar/overview.md)
- [[modules/calendar/calendar-events/end-to-end-logic|Calendar Events Logic]] (modules/calendar/calendar-events/end-to-end-logic.md)

### Verification

```bash
npm run test -- leave
npm run test -- calendar
npm run build
```

---

## Task 3: Presence + Workforce Screens

**Goal:** build the live presence, attendance, overtime, and monitoring settings surfaces.

**Requires:** DEV5 Tasks 1-4 and DEV6 Task 1 complete  
**Live integration:** DEV2 Task 4, DEV1 Task 6 (use MSW until ready) - Contract: `current-focus/contracts/workforce-presence.md`

### Acceptance Criteria

- [ ] Presence overview shows online, offline, break, idle, and active session states.
- [ ] Presence session detail shows timeline, breaks, shift, and exceptions.
- [ ] Attendance correction screen supports submit and review states.
- [ ] Overtime screen supports request, approval, and history.
- [ ] Monitoring configuration screen exposes tenant toggles and employee overrides.
- [ ] Tests cover presence state badges, overtime form, and monitoring toggle permissions.

### References

- [[Userflow/Workforce-Presence/presence-overview|Presence Overview]] (Userflow/Workforce-Presence/presence-overview.md)
- [[Userflow/Workforce-Presence/presence-session-view|Presence Session View]] (Userflow/Workforce-Presence/presence-session-view.md)
- [[Userflow/Workforce-Presence/overtime-management|Overtime Management]] (Userflow/Workforce-Presence/overtime-management.md)
- [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]] (Userflow/Configuration/monitoring-toggles.md)

### Verification

```bash
npm run test -- presence
npm run build
```

---

## Task 4: Agent Management UI

**Goal:** build admin screens for monitoring agent fleet, health, policies, and install status.

**Requires:** DEV5 Tasks 1-4 and DEV6 Task 1 complete  
**Live integration:** DEV4 Tasks 1 and 3 (use MSW until ready) - Contract: `current-focus/contracts/agent-gateway.md`

### Acceptance Criteria

- [ ] Agent fleet table shows device, employee, status, version, OS, last heartbeat, and policy state.
- [ ] Agent detail screen shows registration, active session, health logs, and latest policy.
- [ ] Agent health timeline distinguishes online, degraded, offline, and failed states.
- [ ] Bulk action shell exists for policy update and deregister actions.
- [ ] SignalR updates agent status without page refresh.
- [ ] Tests cover fleet render, status update event, and permission gating.

### References

- [[Userflow/Workforce-Intelligence/agent-deployment|Agent Deployment]] (Userflow/Workforce-Intelligence/agent-deployment.md)
- [[modules/agent-gateway/heartbeat-monitoring/overview|Heartbeat Monitoring]] (modules/agent-gateway/heartbeat-monitoring/overview.md)
- [[frontend/data-layer/real-time|Real-Time Data]] (frontend/data-layer/real-time.md)

### Verification

```bash
npm run test -- agents
npm run build
```

---

## Open Backend Contracts

- [x] Employee and leave balance DTOs -> `current-focus/contracts/hr-employee.md`
- [x] Agent fleet health DTOs -> `current-focus/contracts/agent-gateway.md`
- [ ] Calendar holiday settings DTO and external calendar connection DTO from DEV2 (pending).


