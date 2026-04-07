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
| `event_type` | `varchar(30)` | `company`, `team`, `personal`, `leave`, `holiday`, `review` |
| `source_type` | `varchar(30)` | `manual`, `leave_request`, `holiday`, `review_cycle` |
| `source_id` | `uuid` | Polymorphic reference |
| `visibility` | `varchar(20)` | `public`, `team`, `private` |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/calendar` | Authenticated | Calendar events for date range |
| POST | `/api/v1/calendar` | Authenticated | Create event |
| PUT | `/api/v1/calendar/{id}` | Authenticated | Update event |
| DELETE | `/api/v1/calendar/{id}` | Authenticated | Delete event |

## Related

- [[calendar|Calendar Module]]
- [[calendar/conflict-detection/overview|Conflict Detection]]
- [[event-catalog]]
- [[multi-tenancy]]
- [[error-handling]]
- [[WEEK4-supporting-bridges]]
