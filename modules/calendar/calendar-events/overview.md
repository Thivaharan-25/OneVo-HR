# Calendar Events

**Module:** Calendar
**Feature:** Calendar Events

---

## Purpose

Unified calendar aggregating leave, holidays, review cycles, and custom events into one view via `source_type` + `source_id` polymorphic references.

## Database Tables

### `calendar_events`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `title` | `varchar(200)` | |
| `description` | `text` | |
| `start_date` | `timestamptz` | |
| `end_date` | `timestamptz` | |
| `event_type` | `varchar(30)` | `meeting`, `company`, `team`, `personal`, `leave`, `holiday`, `training`, `out_of_office`, `review` |
| `source_type` | `varchar(30)` | `manual`, `leave_request`, `holiday`, `review_cycle`, `external_sync` |
| `source_id` | `uuid` | Polymorphic reference |
| `audience_type` | `varchar(20)` | `tenant`, `department`, `team`, `individual` — who the event targets |
| `audience_id` | `uuid` | FK → `departments`, `teams`, or `employees` depending on `audience_type`; null for `tenant` |
| `color` | `varchar(7)` | Hex color string (e.g. `#3B82F6`); nullable — defaults to type color in UI |
| `recurrence` | `varchar(20)` | `none`, `daily`, `weekly`, `monthly` |
| `visibility` | `varchar(20)` | `public`, `team`, `private` — controls who can see the event on the calendar |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |

### `calendar_event_participants`

Used only when `audience_type = individual`. For `department`, `team`, and `tenant` audiences, participants are resolved server-side from org hierarchy.

| Column | Type | Notes |
|:-------|:-----|:------|
| `event_id` | `uuid` | FK → calendar_events |
| `employee_id` | `uuid` | FK → employees |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/calendar` | Authenticated | Calendar events for date range (filtered by `IHierarchyScope`) |
| POST | `/api/v1/calendar` | `calendar:write` | Create event |
| PUT | `/api/v1/calendar/{id}` | `calendar:write` | Update event (also used for drag-and-drop reschedule) |
| DELETE | `/api/v1/calendar/{id}` | `calendar:write` | Delete event |

## Related

- [[modules/calendar/overview|Calendar Module]]
- [[Userflow/Calendar/conflict-detection|Conflict Detection]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[backend/messaging/error-handling|Error Handling]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]]
