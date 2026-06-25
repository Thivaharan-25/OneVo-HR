# Calendar Events

**Module:** Calendar
**Feature:** Calendar Events

---

## Purpose

Unified calendar for company events, holidays, employee schedule overlays, Time Off overlays, meeting/event requests, invitations, reminders, conflicts, sharing, and connected Google/Outlook events via `source_type` + `source_id` polymorphic references.

Calendar is a real calendar-management surface. It is not a dashboard card collection and it does not own Time & Attendance setup screens.

## Product Boundary

- Calendar owns event creation, invitations, reminders, sharing, sync, and conflict warnings.
- Time & Attendance owns Attendance, Schedules, Clock-in Policy, and Overtime Rules.
- Time & Attendance > Schedules owns schedule-level holiday country selection and schedule holiday inclusion. Calendar may show holidays from schedule settings as visual overlays but is not the primary place to configure work schedule holiday country.
- Calendar can display schedules, shifts, Time Off, holidays, and overtime as overlays where useful.
- Calendar holiday sync settings control visual Calendar display behavior, not schedule-time behavior.
- Calendar is a main sidebar item at `/calendar`, not a Time & Attendance sub-screen.

## UI Contract

Calendar must use a real calendar layout:

- Month / Week / Day switch.
- Grid or timeline with events rendered as compact chips.
- Conflict markers on conflicting items.
- Side panel or popover for event detail.
- Clean white surfaces, subtle borders, compact row/cell spacing.

Do not use dashboard cards, KPI cards, hero sections, random colored containers, heavy shadows, nested cards, or automation-builder UI for Calendar.

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
| `source_type` | `varchar(30)` | `manual`, `time_off_request`, `holiday`, `review_cycle`, `external_sync`, `schedule_overlay` |
| `source_id` | `uuid` | Polymorphic reference |
| `color` | `varchar(7)` | Hex color string (e.g. `#3B82F6`); nullable - defaults to type color in UI |
| `recurrence` | `varchar(20)` | `none`, `daily`, `weekly`, `monthly` |
| `external_id` | `varchar(255)` | Nullable external system event ID |
| `external_source` | `varchar(30)` | Nullable: `google_calendar`, `outlook_calendar`, `country_holiday` |
| `is_all_day` | `boolean` | Default false; true for all-day events |
| `timezone` | `varchar(50)` | IANA timezone; nullable for all-day events |
| `event_status` | `varchar(20)` | `confirmed`, `tentative`, `cancelled`; nullable for manual |
| `is_private` | `boolean` | Default false; private external events display as "Busy" |
| `organizer_name` | `varchar(200)` | Nullable; from external provider |
| `organizer_email` | `varchar(255)` | Nullable; from external provider |
| `location` | `varchar(500)` | Nullable; location text |
| `meeting_link` | `varchar(500)` | Nullable; meeting URL |
| `external_attendees` | `jsonb` | Nullable; `[{name, email, status}]` from external provider |
| `recurrence_rule` | `text` | Nullable; RRULE string from external provider |
| `external_updated_at` | `timestamptz` | Nullable; last modified timestamp from provider |
| `created_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `calendar_event_participants`

| Column | Type | Notes |
|:-------|:-----|:------|
| `event_id` | `uuid` | FK -> calendar_events |
| `employee_id` | `uuid` | FK -> employees |
| `response_status` | `varchar(30)` | `pending`, `accepted`, `rejected`, `resolution_requested`, `replacement_nominated` when supported |
| `response_reason` | `text` | Nullable; required for rejection |

## External Event Display Rules

- Imported Google/Outlook events appear in the normal Calendar grid alongside OneVo events.
- External events are **read-only** unless they are OneVo-created exported events.
- Each external event shows a small source label: **Google Calendar** or **Outlook Calendar**.
- Private external events display title as **Busy** with only time-block metadata (start, end, all-day flag, timezone).
- External events must visually match the OneVo Calendar design language. Do not use a foreign-looking card style.
- External events use `source_type = 'external_sync'` and `external_source` = `'google_calendar'` or `'outlook_calendar'`.
- External events are included in conflict detection via `ICalendarConflictService`.

## Invitation and Conflict Rules

- Authority is enforcement; conflicts are warnings.
- Authorized actors can send events immediately even when conflicts exist.
- Unauthorized assignment/invitation is blocked.
- Conflicts show count, overlap range, conflicting event names, and optional organizer/owner.
- External calendar events are included in conflict checks.
- Do not block sending a OneVo event because of conflicts.
- Do not block accepting a OneVo event because of conflicts.
- Show conflict count and conflict period before sending.
- Show the same conflict warning to the recipient before accepting.
- Recipients can **Accept anyway**, **Reject**, or use **More** for **Request conflict resolution** and **Nominate replacement** (only when eligible nominees exist).
- Do not show "Nominate replacement" when no eligible nominees exist. Do not show disabled nominee text or an explanation.
- **Request conflict resolution** keeps the response pending and sends a message to the organizer/assigner. It does not automatically cancel or move any event.
- **Nominate replacement** sends the nomination as an inbox/request item to the event creator/assigner. The replacement is not automatically assigned until the creator/assigner confirms.
- No automatic revocation of older conflicting events.
- Event invitations and conflict-resolution requests are delivered through Inbox.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/calendar` | Authenticated | Calendar events for date range (filtered by visibility and scope) |
| GET | `/api/v1/calendar/holiday-settings` | `calendar:admin` | Get legal entity holiday sync settings |
| PUT | `/api/v1/calendar/holiday-settings/{id}` | `calendar:admin` | Enable/disable country holiday sync or override calendar country |
| POST | `/api/v1/calendar/holiday-settings/{id}/sync` | `calendar:admin` | Import holidays from configured provider |
| GET | `/api/v1/calendar/connections` | Authenticated | List user's Google/Outlook calendar connections |
| GET | `/api/v1/calendar/connections/{provider}/connect` | Authenticated | Start OAuth |
| GET | `/api/v1/calendar/connections/{provider}/callback` | Public callback | Complete OAuth and store encrypted tokens |
| PUT | `/api/v1/calendar/connections/{id}` | Authenticated | Update sync direction or selected calendar |
| DELETE | `/api/v1/calendar/connections/{id}` | Authenticated | Disconnect external calendar |
| POST | `/api/v1/calendar/connections/{id}/sync` | Authenticated | Run manual pull/push sync |
| GET | `/api/v1/calendar/conflicts` | Authenticated with relevant calendar/time_off permission | Get conflicts for employee + date-time range |
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
