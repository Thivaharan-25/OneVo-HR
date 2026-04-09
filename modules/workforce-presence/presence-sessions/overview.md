# Presence Sessions

**Module:** Workforce Presence  
**Feature:** Presence Sessions

---

## Purpose

Unified presence — ONE row per employee per day. Combines biometric + agent data. This is the single source of truth for "is this employee present?"

## Database Tables

### `presence_sessions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `date` | `date` | The work day |
| `first_seen_at` | `timestamptz` | First sign of presence (any source) |
| `last_seen_at` | `timestamptz` | Last sign of presence |
| `total_present_minutes` | `int` | Computed from all sources |
| `total_break_minutes` | `int` | Sum of break records |
| `source` | `varchar(20)` | `biometric`, `agent`, `manual`, `mixed` |
| `status` | `varchar(20)` | `present`, `absent`, `partial`, `on_leave` |

**Indexes:** `(tenant_id, employee_id, date)` UNIQUE

## Key Business Rules

1. Presence session is COMPUTED, not directly written — aggregates from biometric, agent, and manual sources.
2. Deduplicates overlapping sources — uses earliest first_seen and latest last_seen.

## Hangfire Jobs

| Job | Schedule | Purpose |
|:----|:---------|:--------|
| `ReconcilePresenceSessions` | Every 5 min (work hours) | Merge biometric + agent → presence_sessions |
| `FlagUnresolvedAbsences` | Daily 10:00 AM | Flag no-presence employees |
| `CloseOpenSessions` | Daily 11:59 PM | Close open sessions |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/workforce/presence` | `attendance:read` | List presence |
| GET | `/api/v1/workforce/presence/{employeeId}` | `attendance:read` | Employee presence |
| GET | `/api/v1/workforce/presence/live` | `workforce:view` | Real-time status |

## Related

- [[modules/workforce-presence/overview|Workforce Presence Module]]
- [[modules/workforce-presence/device-sessions/overview|Device Sessions]]
- [[Userflow/Workforce-Presence/break-tracking|Break Tracking]]
- [[modules/workforce-presence/attendance-corrections/overview|Attendance Corrections]]
- [[modules/workforce-presence/shifts-schedules/overview|Shifts Schedules]]
- [[modules/workforce-presence/overtime/overview|Overtime]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/messaging/error-handling|Error Handling]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/shared-kernel|Shared Kernel]]
- [[code-standards/logging-standards|Logging Standards]]
- [[current-focus/DEV3-workforce-presence-setup|DEV3: Workforce Presence]]
