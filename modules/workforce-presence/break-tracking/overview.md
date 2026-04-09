# Break Tracking

**Module:** Workforce Presence  
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
| `BreakStarted` | Employee starts break (manual or auto-detected from idle) | [[modules/agent-gateway/overview|Agent Gateway]] (pause monitoring — NO data collection during break) |
| `BreakEnded` | Employee ends break (manual or activity resumes) | [[modules/agent-gateway/overview|Agent Gateway]] (resume monitoring) |
| `BreakExceeded` | Break exceeds allowed duration | [[modules/exception-engine/overview|Exception Engine]] |

**Break → Agent lifecycle:** When `BreakStarted` fires, agent-gateway sends `PauseMonitoring` to the desktop agent. The agent stops ALL collectors — zero data captured during breaks. This is a GDPR requirement for employee break privacy. When `BreakEnded` fires, agent-gateway sends `ResumeMonitoring` and data collection resumes.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/workforce/breaks/{employeeId}` | `attendance:read` | Break records |
| POST | `/api/v1/workforce/breaks/start` | `attendance:write` | Employee manually starts a break |
| POST | `/api/v1/workforce/breaks/end` | `attendance:write` | Employee manually ends a break |

**Manual break flow:** Employee clicks "Start Break" in tray app or web UI → `POST /breaks/start` → publishes `BreakStarted` → agent pauses monitoring. Employee clicks "End Break" → `POST /breaks/end` → publishes `BreakEnded` → agent resumes.

**Auto-detected break:** If agent reports idle exceeding configurable threshold (default 15 min) AND employee has not manually started a break, the `ReconcilePresenceSessions` Hangfire job creates a `break_record` with `auto_detected = true` and fires `BreakStarted`. When activity resumes, it fires `BreakEnded`.

## Related

- [[modules/workforce-presence/overview|Workforce Presence Module]]
- [[modules/workforce-presence/presence-sessions/overview|Presence Sessions]]
- [[modules/workforce-presence/device-sessions/overview|Device Sessions]]
- [[modules/workforce-presence/shifts-schedules/overview|Shifts Schedules]]
- [[modules/workforce-presence/attendance-corrections/overview|Attendance Corrections]]
- [[modules/workforce-presence/overtime/overview|Overtime]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/messaging/error-handling|Error Handling]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV3-workforce-presence-setup|DEV3: Workforce Presence]]
