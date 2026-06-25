# Contract: Time & Attendance

**Backend owner:** DEV2 Task 4  
**Consumers:** DEV6 Task 3, DEV8 (clockin/clockout/break tags)  
**Canonical source:** `ONEVO.Application/Features/TimeAttendance/`

---

## GET `/api/v1/time-attendance/presence/current`

```ts
interface PresenceSessionDto {
  session_id: string
  employee_id: string
  state: "active" | "break" | "idle" | "offline"
  clock_in_at: string
  clock_out_at: string | null
  current_break_start: string | null
  shift_id: string | null
  breaks: Array<{ start: string; end: string | null; type: "personal" | "lunch" }>
  exceptions: Array<{ id: string; type: string; severity: "low" | "medium" | "high" }>
}
```

## GET `/api/v1/time-attendance/schedules/current`

```ts
interface ShiftDto {
  shift_id: string
  employee_id: string
  start_time: string          // ISO datetime
  end_time: string            // ISO datetime
  schedule_name: string
  is_current: boolean
}
```

## POST `/api/v1/time-attendance/clock-in` -> `PresenceSessionDto`

## POST `/api/v1/time-attendance/clock-out` -> `PresenceSessionDto`

## POST `/api/v1/time-attendance/breaks/start` -> `PresenceSessionDto`

## POST `/api/v1/time-attendance/breaks/end` -> `PresenceSessionDto`

## POST `/api/v1/time-attendance/overtime`

```ts
interface OvertimeRequestDto {
  date: string                // ISO date
  expected_hours: number
  reason: string
}
// response: { request_id: string; status: "pending" }
```

## Notes

- `state` drives presence badge color: `active` -> green, `break` -> amber, `idle` -> yellow, `offline` -> grey
- Monitoring data collection begins only after clock-in (monitoring-lifecycle-gated per agent policy)
- Overtime request uses Phase 1 management coverage routing and Notifications. Shared Platform workflow engine is Phase 2.

