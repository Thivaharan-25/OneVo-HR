# Module: Calendar

**Namespace:** `ONEVO.Modules.Calendar`
**Pillar:** Shared Foundation
**Owner:** Dev 1 (Week 4)
**Tables:** 1

---

## Purpose

Company-wide and team calendar events. Aggregates leave, holidays, review cycles, and custom events into a unified calendar view.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[leave]] | `ILeaveService` | Approved leave for calendar |
| **Depends on** | [[workforce-presence]] | — | Holidays |
| **Depends on** | [[performance]] | — | Review cycle dates |

---

## Database Tables (1)

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

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/calendar` | Authenticated | Calendar events for date range |
| POST | `/api/v1/calendar` | Authenticated | Create event |
| PUT | `/api/v1/calendar/{id}` | Authenticated | Update event |
| DELETE | `/api/v1/calendar/{id}` | Authenticated | Delete event |

See also: [[module-catalog]], [[leave]], [[workforce-presence]]
