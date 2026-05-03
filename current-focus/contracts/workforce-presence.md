# Contract: Workforce Presence

**Backend owner:** DEV2 Task 4  
**Consumers:** DEV6 Task 3, DEV8 (clockin/clockout/break tags)  
**Canonical source:** `ONEVO.Application/Features/WorkforcePresence/`

---

## GET `/api/v1/presence/sessions/current`

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

## GET `/api/v1/presence/shifts/current`

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

## POST `/api/v1/presence/sessions/start` -> `PresenceSessionDto`

## POST `/api/v1/presence/sessions/end` -> `PresenceSessionDto`

## POST `/api/v1/presence/breaks/start` -> `PresenceSessionDto`

## POST `/api/v1/presence/breaks/end` -> `PresenceSessionDto`

## POST `/api/v1/presence/overtime/request`

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
- Overtime request goes through the Shared Platform workflow engine (DEV1 Task 5)

