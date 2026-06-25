# Module: Calendar

**Feature Folder:** `Application/Features/Calendar`
**Phase:** 1 - Build
**Pillar:** Shared Foundation
**Owner:** Dev 2 backend / Dev 6 frontend
**Tables:** 5
**Task File:** [[current-focus/DEV2|DEV2: Backend HR + Time & Attendance Core]]

---

## Purpose

Calendar is the standalone visual planning surface for company events, holidays, employee schedules, shifts, Time Off, meetings, event requests, invitation responses, reminders, conflicts, sharing, and external sync.

Phase 1 includes country holiday sync and external calendar sync (Google Calendar and Outlook Calendar). Legal entity country is the default holiday calendar source for Calendar display; admins can disable holiday sync or override the calendar display country from the Calendar screen without changing the legal entity registration country.

External calendar connections are accessed from a `[Connections]` button in the Calendar page top action bar. Clicking it opens a centered **Calendar Connections** modal dialog. There is no Calendar Connections sidebar item, sub-sidebar item, Settings page, or separate route. The modal shows Google Calendar and Outlook Calendar connection cards with status, sync mode, and management actions.

Time & Attendance > Schedules owns the schedule-level holiday country selection and which holidays apply to each work schedule. Calendar may display holidays from schedule settings as visual overlays, but Calendar is not the primary place to configure work schedule holiday country or schedule holiday inclusion.

Time & Attendance owns operational attendance screens: **Attendance**, **Schedules**, **Clock-in Policy**, and **Overtime Rules**. Calendar may display schedule/attendance/Time Off/overtime overlays, but Schedules, Clock-in Policy, attendance correction, and overtime management remain Time & Attendance behavior.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/time-off/overview|Time Off]] | `ITimeOffService` | Approved time off for calendar |
| **Depends on** | [[modules/time-attendance/overview|Time & Attendance]] | - | Schedule and attendance overlays |
| **Depends on** | [[database/performance|Performance]] | - | Review cycle dates |
| **Depends on** | [[modules/org-structure/overview|Org Structure]] | `LegalEntityCountrySet` | Default holiday calendar country from legal entity country |
| **Depends on** | External API | Nager.Date | Phase 1 free country holiday source |
| **Depends on** | External API | Google Calendar API (OAuth 2.0) | Phase 1 external calendar sync |
| **Depends on** | External API | Microsoft Graph Calendar API (OAuth 2.0) | Phase 1 external calendar sync |
| **Consumed by** | [[modules/time-off/overview|Time Off]] | `ICalendarConflictService` | Conflict warnings for time off requests |
| **Consumed by** | Calendar Events | `ICalendarConflictService` | Conflict warnings for event creation, invitations, and reschedules |

---

## Public Interface

```csharp
// ONEVO.Application.Features.Calendar/Public/ICalendarConflictService.cs
public interface ICalendarConflictService
{
    /// <summary>
    /// Returns calendar events that overlap with the given date-time range for an employee.
    /// Used by Calendar and Time Off to show conflict warnings.
    /// Caller-specific exclusions apply; Time Off workflows may exclude holidays because holidays are already factored into time off day calculation.
    /// </summary>
    Task<Result<CalendarConflictSummaryDto>> GetConflictsForDateRangeAsync(
        Guid employeeId, DateTimeOffset startAt, DateTimeOffset endAt, CancellationToken ct);
}
```

---

## Code Location (Clean Architecture)

Domain entities:
  ONEVO.Domain/Features/Calendar/Entities/
  ONEVO.Domain/Features/Calendar/Events/

Application (CQRS):
  ONEVO.Application/Features/Calendar/Commands/
  ONEVO.Application/Features/Calendar/Queries/
  ONEVO.Application/Features/Calendar/DTOs/Requests/
  ONEVO.Application/Features/Calendar/DTOs/Responses/
  ONEVO.Application/Features/Calendar/Validators/
  ONEVO.Application/Features/Calendar/EventHandlers/

Infrastructure:
  ONEVO.Infrastructure/Persistence/Configurations/Calendar/

API endpoints:
  ONEVO.Api/Controllers/Calendar/CalendarController.cs

---

## Database Tables (5)

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
| `color` | `varchar(7)` | Hex color; nullable |
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

Used when `audience_type = individual` or invitation response is needed.

| Column | Type | Notes |
|:-------|:-----|:------|
| `event_id` | `uuid` | FK -> calendar_events |
| `employee_id` | `uuid` | FK -> employees |
| `response_status` | `varchar(30)` | `pending`, `accepted`, `rejected`, `resolution_requested`, `replacement_nominated` when supported |
| `response_reason` | `text` | Nullable; required for rejection |

### `holiday_calendar_settings`

Controls country holiday sync per legal entity.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `legal_entity_id` | `uuid` | FK -> legal_entities |
| `default_country_code` | `char(2)` | Legal entity country |
| `override_country_code` | `char(2)` | Nullable admin override from Calendar screen |
| `effective_country_code` | `char(2)` | Override or default |
| `holiday_sync_enabled` | `boolean` | Admin can stop sync |
| `provider` | `varchar(30)` | `nager_date` or `manual` |
| `last_synced_year` | `integer` | Nullable |
| `last_synced_at` | `timestamptz` | Nullable |
| `updated_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `external_calendar_connections`

User-level Google Calendar and Outlook Calendar OAuth connections with encrypted tokens.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `user_id` | `uuid` | FK -> users |
| `provider` | `varchar(30)` | `google_calendar`, `outlook_calendar` |
| `external_account_email` | `varchar(255)` | Connected account email |
| `external_calendar_id` | `varchar(255)` | Nullable primary/default calendar |
| `external_calendar_name` | `varchar(255)` | Display name of selected external calendar |
| `access_token_encrypted` | `bytea` | Nullable; short-lived |
| `refresh_token_encrypted` | `bytea` | Encrypted refresh token |
| `scopes` | `jsonb` | Granted scopes |
| `sync_direction` | `varchar(20)` | `pull_only`, `push_only`, `two_way`, `disabled` |
| `status` | `varchar(20)` | `active`, `reauth_required`, `paused`, `revoked`, `failed` |
| `sync_token_encrypted` | `bytea` | Nullable encrypted Google Calendar incremental sync token |
| `delta_link_encrypted` | `bytea` | Nullable encrypted Microsoft Graph delta link/token |
| `failure_count` | `integer` | Consecutive sync failures; reset to 0 after successful sync |
| `last_synced_at` | `timestamptz` | Nullable |
| `last_successful_sync_at` | `timestamptz` | Nullable |
| `last_error` | `text` | Nullable last provider/sync error |
| `expires_at` | `timestamptz` | Nullable |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `external_calendar_event_links`

Sync state and idempotency between ONEVO events and Google/Outlook events.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `calendar_event_id` | `uuid` | FK -> calendar_events |
| `external_calendar_connection_id` | `uuid` | FK -> external_calendar_connections |
| `provider` | `varchar(30)` | `google_calendar`, `outlook_calendar` |
| `external_calendar_id` | `varchar(255)` | Provider calendar ID |
| `external_event_id` | `varchar(255)` | Provider event ID |
| `external_etag` | `varchar(255)` | Provider version/etag for conflict detection |
| `sync_direction` | `varchar(20)` | `inbound`, `outbound` |
| `sync_status` | `varchar(20)` | `synced`, `pending`, `failed`, `skipped`, `conflict` |
| `last_synced_at` | `timestamptz` | Nullable |
| `last_error` | `text` | Nullable |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

---

## Key Business Rules

1. **Unified calendar** - aggregates time off, holidays, review cycles, schedule overlays, and custom events into one view via `source_type` + `source_id` polymorphic references.
2. **Calendar boundary** - Calendar owns visual calendar views, events, invitations, reminders, conflicts, sharing, and sync. Time & Attendance owns Attendance, Schedules, Clock-in Policy, and Overtime Rules.
3. **Conflict behavior** - authority is enforcement; conflicts are warnings. Unauthorized assignment is blocked. Authorized assignment/invitation can continue with warning details.
4. **Recipient actions** - conflict response actions are Accept anyway, Reject, More -> Request conflict resolution, and More -> Nominate replacement only when eligible nominees exist.
5. **No automatic revocation** - older conflicting events remain until an organizer manually adjusts/removes them.
6. **External sync** - events with `source_type = external_sync` are read-only unless the connection is `two_way` and the current user owns the connection.
7. **Legal entity holiday default** - when legal entity country is set, Calendar creates `holiday_calendar_settings` with `default_country_code` from the legal entity country. This controls Calendar display holidays only. Work schedule holiday country is a separate per-schedule setting managed in Time & Attendance > Schedules.
8. **Holiday override** - Calendar admins can stop country holiday sync or set `override_country_code`. This changes the Calendar display only; it does not change the legal entity country, the Company timezone, or any work schedule holiday country.
9. **Country holiday provider** - Phase 1 uses Nager.Date for public holidays by year and ISO country code. Imported holidays are stored as `calendar_events` with `event_type = holiday`, `source_type = holiday`, and `external_source = country_holiday`.
10. **Google/Outlook sync** - users connect Google Calendar or Outlook Calendar with OAuth from the `[Connections]` button in the Calendar top action bar. Sync modes: Import only (`pull_only`), Export OneVo events only (`push_only`), Two-way sync (`two_way`), Paused (`disabled`). Provider event IDs are tracked in `external_calendar_event_links` to prevent duplicates. Google `syncToken` and Microsoft delta links are stored on `external_calendar_connections`; tenant-level `tenant_integration_credentials` is not used for per-user calendar tokens.
11. **External event display** - imported events appear in the normal Calendar grid with a source label (Google Calendar / Outlook Calendar). External events are read-only unless they are OneVo-created exported events. Private external events display as "Busy" with only time-block metadata.
12. **Sync window** - default sync range is past 30 days to future 180 days. Recurring external events are expanded only within the sync window.
13. **External events in conflict checks** - external calendar events are included in `ICalendarConflictService` conflict detection. Conflicts remain warnings; authority is enforcement.
14. **Disconnect** - removing a connection hides imported external events unless they were converted to OneVo-owned events. OneVo-owned events persist.
15. **Reconnect** - when token refresh fails, status becomes "Needs reconnect". Reconnect repeats OAuth and preserves existing connection settings.

---

## Domain Events (intra-module - MediatR)

> These events are published and consumed within this module only. They never cross the module boundary.

| Event | Published When | Handler |
|:------|:---------------|:--------|
| _(none)_ | - | - |

## Cross-Module Events (cross-module - MediatR INotification)

### Publishes

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| _(none)_ | - | - |

### Consumes

| Event | Source Module | Action Taken |
|:------|:-------------|:-------------|
| `TimeOffApproved` | [[modules/time-off/overview|Time Off]] | Create a `time_off` calendar event for the approved time_off period |
| `ReviewCycleStarted` | [[modules/performance/overview|Performance]] | Create a `review` calendar event for the cycle dates |
| `EmployeeHired` | [[modules/core-hr/overview|Core HR]] | Seed onboarding events for new employee |
| `LegalEntityCountrySet` | [[modules/org-structure/overview|Org Structure]] | Create default holiday calendar settings from the legal entity country |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/calendar` | Authenticated | Calendar events for date range |
| GET | `/api/v1/calendar/holiday-settings` | `calendar:admin` | Get legal entity holiday calendar settings |
| PUT | `/api/v1/calendar/holiday-settings/{id}` | `calendar:admin` | Enable/disable holiday sync or override country calendar |
| POST | `/api/v1/calendar/holiday-settings/{id}/sync` | `calendar:admin` | Pull public holidays for selected year/country |
| GET | `/api/v1/calendar/connections` | Authenticated | List current user's Google/Outlook calendar connections |
| GET | `/api/v1/calendar/connections/{provider}/connect` | Authenticated | Start Google/Outlook OAuth |
| GET | `/api/v1/calendar/connections/{provider}/callback` | Public callback | Complete OAuth and store encrypted tokens |
| PUT | `/api/v1/calendar/connections/{id}` | Authenticated | Change sync direction or selected calendar |
| DELETE | `/api/v1/calendar/connections/{id}` | Authenticated | Disconnect external calendar |
| POST | `/api/v1/calendar/connections/{id}/sync` | Authenticated | Run manual pull/push sync |
| GET | `/api/v1/calendar/conflicts` | Authenticated with relevant calendar/time_off permission | Get conflicts for employee + date-time range |
| POST | `/api/v1/calendar` | `calendar:write` | Create event |
| PUT | `/api/v1/calendar/{id}` | `calendar:write` | Update event (reschedule via drag-and-drop uses this) |
| DELETE | `/api/v1/calendar/{id}` | `calendar:write` | Delete event |

## Features

- [[Userflow/Calendar/calendar-integrations|Calendar Integrations]] - Country holidays, Google Calendar, and Outlook Calendar
- [[Userflow/Calendar/conflict-detection|Conflict Detection]] - `ICalendarConflictService` for event, invitation, reschedule, and time_off conflict warnings

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] - All events are tenant-scoped
- [[backend/messaging/event-catalog|Event Catalog]] - Events sourced polymorphically from time_off, holidays, review cycles
- [[current-focus/DEV2|DEV2: Backend HR + Time & Attendance Core]] - Calendar backend implementation
- [[current-focus/DEV6|DEV6: Frontend HR + Monitoring UI]] - Calendar UI implementation

See also: [[backend/module-catalog|Module Catalog]], [[modules/time-off/overview|Time Off]], [[modules/time-attendance/overview|Time & Attendance]], [[Userflow/Calendar/conflict-detection|Calendar Conflict Detection]]

## Calendar and Time & Attendance Navigation

Calendar is a separate main sidebar item at `/calendar`. It supports company events, holidays, employee schedules, shifts, Time Off, meetings, event requests, invitation accept/decline, reminders, conflicts, sharing, and external sync.

Calendar UI must look like a real calendar:

- Month / Week / Day switch.
- Grid or timeline layout.
- Events rendered in date cells or time slots as compact chips.
- Conflict marker on conflicting items.
- Side panel or popover for event details.
- Clean white surfaces, subtle borders, compact spacing.

Do not build Calendar as dashboard cards, KPI cards, hero sections, random colored containers, heavy shadows, nested cards, or an automation-builder layout.

Availability:

- Employees see their own schedule, Time Off, meetings, events, invitations, and reminders.
- Managers see their own calendar plus team schedules, Time Off, and conflicts allowed by permission and management coverage.
- HR/admin users see calendar data allowed by management coverage.

Time & Attendance contains these operational items:

| Label | Route | Purpose |
|---|---|---|
| Attendance | `/time-attendance/attendance` | Own attendance, scoped team attendance, and row-level correction actions |
| Schedules | `/time-attendance/schedules` | Work schedule management with table columns: Name, Workdays, Work time, Assigned, Holidays, Created At, Actions |
| Clock-in Policy | `/time-attendance/clock-in-policy` | Grace/lateness, correction, overtime request behavior, outage fallback, clock-in requirement, date-effective ranges |
| Overtime Rules | `/time-attendance/overtime-rules` | Overtime policy setup |

**Deprecated navigation:** Do not document Work Weeks or Work Patterns as active standalone screens. Their behavior belongs inside Schedules. Do not document Schedules, Attendance, or Overtime as Calendar management screens.

**Connection to WMS:**
- Shift schedule hours from Time & Attendance feed into WMS Resource Management as the available capacity baseline for each employee.
- Approved timesheets from WMS Time Tracking can create Attendance correction records when discrepancies exist.
- Excess hours from approved timesheets can create Overtime entries for configured overtime approval.

See [[Userflow/Work-Management/time-tracking-flow|Time Tracking Flow]] for the full overtime and attendance connection.
