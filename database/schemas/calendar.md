# Calendar — Schema

**Module:** [[modules/calendar/overview|Calendar]]
**Phase:** Phase 1
**Tables:** 1

---

## `calendar_events`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `title` | `varchar(200)` |  |
| `description` | `text` |  |
| `start_date` | `timestamptz` |  |
| `end_date` | `timestamptz` |  |
| `event_type` | `varchar(30)` | `company`, `team`, `personal`, `leave`, `holiday`, `review` |
| `source_type` | `varchar(30)` | `manual`, `leave_request`, `holiday`, `review_cycle` |
| `source_id` | `uuid` | Polymorphic reference |
| `visibility` | `varchar(20)` | `public`, `team`, `private` |
| `external_id` | `varchar(255)` | Nullable — external system event ID (e.g. Google Calendar event ID). Used for deduplication when Phase 2 Google Calendar sync is enabled. |
| `external_source` | `varchar(30)` | Nullable — `google_calendar`, `outlook`, `ical`. Null for internally created events. |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `created_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## Related

- [[modules/calendar/overview|Calendar Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]