# Break Tracking

**Module:** Time & Attendance  
**Feature:** Break Tracking

---

## Purpose

Tracks breaks with auto-detection from agent idle threshold (default 15 min).

## Database Tables

### `break_records`
Fields: `employee_id`, `break_start`, `break_end` (null if ongoing), `break_type` (`lunch`, `prayer`, `smoke`, `personal`, `other`), `auto_detected`.

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `BreakStarted` | Employee starts break (manual or auto-detected from idle) | [[modules/agent-gateway/overview\|Agent Gateway]] (pause monitoring - NO data collection during break) |
| `BreakEnded` | Employee ends break (manual or activity resumes) | [[modules/agent-gateway/overview\|Agent Gateway]] (resume monitoring) |
| `BreakExceeded` | Break exceeds allowed duration | [[modules/notifications/overview\|Notifications]] (Phase 1 lightweight alert, recipient resolved by Monitoring Policy); Phase 2: [[modules/exception-engine/overview\|Exception Engine]] |

**Break -> Agent lifecycle:** When `BreakStarted` fires, agent-gateway sends `PauseMonitoring` to the desktop agent. The agent stops ALL collectors - zero data captured during breaks. This is a GDPR requirement for employee break privacy. When `BreakEnded` fires, agent-gateway sends `ResumeMonitoring` and data collection resumes.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/time-attendance/breaks/{employeeId}` | `attendance:read` | Break records |
| POST | `/api/v1/time-attendance/breaks/start` | `attendance:write` | Employee manually starts a break |
| POST | `/api/v1/time-attendance/breaks/end` | `attendance:write` | Employee manually ends a break |

**Manual break flow:** Employee clicks "Start Break" in tray app or web UI -> `POST /breaks/start` -> publishes `BreakStarted` -> agent pauses monitoring. Employee clicks "End Break" -> `POST /breaks/end` -> publishes `BreakEnded` -> agent resumes.

**Auto-detected break:** If agent reports idle exceeding configurable threshold (default 15 min) AND employee has not manually started a break, the `ReconcilePresenceSessions` Hangfire job creates a `break_record` with `auto_detected = true` and fires `BreakStarted`. When activity resumes, it fires `BreakEnded`.

## Related

- [[modules/time-attendance/overview|Time & Attendance Module]]
- [[modules/time-attendance/presence-sessions/overview|Presence Sessions]]
- [[modules/time-attendance/device-sessions/overview|Device Sessions]]
- [[modules/time-attendance/shifts-schedules/overview|Shifts Schedules]]
- [[modules/time-attendance/attendance-corrections/overview|Attendance Corrections]]
- [[modules/time-attendance/overtime/overview|Overtime]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/messaging/error-handling|Error Handling]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV3-time-attendance-setup|DEV3: Time & Attendance]]
