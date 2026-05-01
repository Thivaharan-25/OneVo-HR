# DEV6: Frontend HR + Workforce UI

**Track:** Frontend
**Primary ownership:** HR screens, leave, calendar, presence, agent management UI
**Current Unfinished Task:** Task 1 - HR employee screens
**Blocked By:** DEV5 app foundation; DEV2 Core HR API for live data

---

## ADE Instructions

When Dev 6 asks to continue, start with the first unchecked item in **Current Unfinished Task**. If APIs are not ready, create MSW handlers that match the expected DTOs and record the backend contract gap.

---

## Task 1: HR Employee Screens

**Goal:** build employee list, detail, create, edit, onboarding, and offboarding screens.

### Acceptance Criteria

- [ ] Employee list supports search, filters, cursor pagination, and status badges.
- [ ] Employee detail shows profile, employment, manager, department, team, and activity summary.
- [ ] Create/edit form validates required fields and server errors.
- [ ] Onboarding flow supports staged employee creation.
- [ ] Offboarding flow supports reason, date, asset checklist placeholder, and confirmation.
- [ ] Tests cover list render, create validation, edit save, and forbidden state.

### References

- [[Userflow/Employee-Management/profile-management|Profile Management]]
- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]]
- [[Userflow/Employee-Management/employee-offboarding|Employee Offboarding]]
- [[frontend/design-system/patterns/form-patterns|Form Patterns]]

### Verification

```bash
npm run test -- employee
npm run build
```

---

## Task 2: Leave + Calendar Screens

**Goal:** build leave and calendar workflows used by employees and managers.

### Acceptance Criteria

- [ ] Leave balance view shows available, used, pending, and upcoming leave.
- [ ] Leave request form validates leave type, date range, overlap, and reason.
- [ ] Manager approval screen supports approve, reject, and comment.
- [ ] Calendar screen combines holidays, shifts, leave, and company events.
- [ ] Shift and holiday admin screens exist.
- [ ] Tests cover request validation, approval action, and calendar event render.

### References

- [[Userflow/Leave/leave-request-submission|Leave Request Submission]]
- [[Userflow/Leave/leave-approval|Leave Approval]]
- [[Userflow/Calendar/calendar-event-creation|Calendar Event Creation]]

### Verification

```bash
npm run test -- leave
npm run test -- calendar
npm run build
```

---

## Task 3: Presence + Workforce Screens

**Goal:** build the live presence, attendance, overtime, and monitoring settings surfaces.

### Acceptance Criteria

- [ ] Presence overview shows online, offline, break, idle, and active session states.
- [ ] Presence session detail shows timeline, breaks, shift, and exceptions.
- [ ] Attendance correction screen supports submit and review states.
- [ ] Overtime screen supports request, approval, and history.
- [ ] Monitoring configuration screen exposes tenant toggles and employee overrides.
- [ ] Tests cover presence state badges, overtime form, and monitoring toggle permissions.

### References

- [[Userflow/Workforce-Presence/presence-overview|Presence Overview]]
- [[Userflow/Workforce-Presence/presence-session-view|Presence Session View]]
- [[Userflow/Workforce-Presence/overtime-management|Overtime Management]]
- [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]]

### Verification

```bash
npm run test -- presence
npm run build
```

---

## Task 4: Agent Management UI

**Goal:** build admin screens for monitoring agent fleet, health, policies, and install status.

### Acceptance Criteria

- [ ] Agent fleet table shows device, employee, status, version, OS, last heartbeat, and policy state.
- [ ] Agent detail screen shows registration, active session, health logs, and latest policy.
- [ ] Agent health timeline distinguishes online, degraded, offline, and failed states.
- [ ] Bulk action shell exists for policy update and deregister actions.
- [ ] SignalR updates agent status without page refresh.
- [ ] Tests cover fleet render, status update event, and permission gating.

### References

- [[Userflow/Workforce-Intelligence/agent-deployment|Agent Deployment]]
- [[modules/agent-gateway/heartbeat-monitoring/overview|Heartbeat Monitoring]]
- [[frontend/data-layer/real-time|Real-Time Data]]

### Verification

```bash
npm run test -- agents
npm run build
```

---

## Open Backend Contracts

- [ ] Employee DTO from DEV2.
- [ ] Leave balance DTO from DEV2.
- [ ] Agent health DTO from DEV4.
