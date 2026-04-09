# Task: Workforce Presence — Setup

**Assignee:** Dev 3
**Module:** WorkforcePresence
**Priority:** Critical
**Dependencies:** [[current-focus/DEV1-infrastructure-setup|DEV1 Infrastructure Setup]], [[current-focus/DEV4-shared-platform-agent-gateway|DEV4 Shared Platform Agent Gateway]] (agent gateway feeds device sessions)

---

## Step 1: Backend

### Acceptance Criteria

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
- [ ] Unit tests >= 80% coverage

### Backend References

- [[modules/workforce-presence/overview|workforce-presence]] — module architecture
- [[modules/configuration/monitoring-toggles/overview|configuration]] — monitoring toggles
- [[backend/module-catalog|Module Catalog]] — dependencies
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant-scoped presence data

---

## Step 2: Frontend

### Pages to Build

```
app/(dashboard)/workforce/presence/
├── page.tsx                      # Live who's-in/out (real-time via SignalR)
├── attendance/page.tsx           # Attendance history
├── overtime/page.tsx             # Overtime tracking
├── shifts/page.tsx               # Shift schedules
├── holidays/page.tsx             # Holiday calendar
├── components/                   # Colocated feature components
│   ├── LiveStatusBoard.tsx       # Real-time presence grid (summary cards + employee status)
│   ├── AttendanceTable.tsx       # Attendance records DataTable
│   ├── ShiftCalendar.tsx         # Shift schedule calendar view
│   ├── OvertimeTable.tsx         # Overtime requests DataTable
│   └── BiometricDeviceCard.tsx   # Device status card
└── _types.ts                     # Local TypeScript definitions
```

### What to Build

- [ ] Live workforce dashboard (LiveStatusBoard):
  - Summary cards: total active, idle, on break, absent, on leave (real-time via SignalR)
  - Employee DataTable: name, status (color-coded StatusBadge), current activity, check-in time, device
  - Filter by department, team, status
  - Auto-refresh via SignalR `workforce-live` channel
- [ ] Presence session detail (click employee row):
  - TimelineBar: full-day view showing active/idle/break/meeting segments
  - Device sessions list
  - Break records
- [ ] Shift management page (ShiftCalendar):
  - CRUD shifts (name, start/end time, type)
  - Schedule templates
  - Assign shifts to employees (bulk assign by department/team)
- [ ] Holiday management page:
  - Calendar view with holidays marked
  - CRUD holidays (name, date, country, recurring)
- [ ] PermissionGate: `workforce:read`, `workforce:manage-shifts`

### Userflows

- [[Userflow/Workforce-Intelligence/live-dashboard|Live Dashboard]] — real-time workforce status monitoring
- [[Userflow/Workforce-Presence/shift-schedule-setup|Shift Schedule Setup]] — configure shifts and schedules
- [[Userflow/Workforce-Presence/presence-session-view|Presence Session View]] — view employee presence details
- [[Userflow/Workforce-Presence/break-tracking|Break Tracking]] — view and manage break records

### API Endpoints (Frontend Consumes)

| Method | Endpoint | Purpose |
|:-------|:---------|:--------|
| GET | `/api/v1/workforce/presence/live` | Real-time workforce status |
| GET | `/api/v1/workforce/presence/{employeeId}?date={date}` | Employee presence detail |
| GET | `/api/v1/workforce/device-sessions/{employeeId}?date={date}` | Device sessions |
| GET | `/api/v1/workforce/breaks/{employeeId}?date={date}` | Break records |
| GET | `/api/v1/workforce/shifts` | List shifts |
| POST | `/api/v1/workforce/shifts` | Create shift |
| PUT | `/api/v1/workforce/shifts/{id}` | Update shift |
| GET | `/api/v1/workforce/schedules` | List schedules |
| POST | `/api/v1/workforce/schedules` | Create schedule |
| POST | `/api/v1/workforce/shift-assignments` | Assign shifts (bulk) |
| GET | `/api/v1/workforce/holidays` | List holidays |
| POST | `/api/v1/workforce/holidays` | Create holiday |
| **SignalR** | `/hubs/notifications` | `workforce-live` channel for real-time |

### Frontend References

- [[frontend/design-system/components/component-catalog|Component Catalog]] — DataTable, StatusBadge, TimelineBar, Calendar
- [[frontend/design-system/foundations/color-tokens|Color Tokens]] — status colors (active/idle/offline/on-leave)
- [[frontend/design-system/patterns/data-visualization|Data Visualization]] — timeline visualization

---

## Related Tasks

- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4 Shared Platform Agent Gateway]] — agent gateway ingest data feeds into device_sessions
- [[current-focus/DEV4-workforce-presence-biometric|DEV4 Workforce Presence Biometric]] — biometric events reconciled into presence_sessions
- [[current-focus/DEV1-leave|DEV1 Leave]] — LeaveApproved event sets presence status to on_leave
- [[current-focus/DEV2-exception-engine|DEV2 Exception Engine]] — reads IWorkforcePresenceService for no_presence and break_exceeded rules
- Payroll — deferred to Phase 2 (reads IWorkforcePresenceService for worked hours)
- [[current-focus/DEV1-productivity-analytics|DEV1 Productivity Analytics]] — aggregates from presence_sessions
