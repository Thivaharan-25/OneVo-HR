# Module: Calendar

**Feature Folder:** `Application/Features/Calendar`
**Phase:** 1 — Build
**Pillar:** Shared Foundation
**Owner:** Dev 2 backend / Dev 6 frontend
**Tables:** 5
**Task File:** [[current-focus/DEV2|DEV2: Backend HR + Workforce Core]]

---

## Purpose

Company-wide, legal-entity-wide, and team calendar events. Aggregates leave, holidays, review cycles, custom events, country holidays, and connected Google/Outlook events into a unified calendar view.

Phase 1 includes country holiday sync and external calendar sync. Legal entity country is the default holiday calendar source for employees in that legal entity; admins can disable holiday sync or override the calendar country from the Calendar screen without changing the legal entity registration country.

The Calendar's sidebar also surfaces three workforce management features: **Shifts & Schedules** (shift creation, schedule templates, employee assignments), **Attendance Correction** (manager corrections to presence data), and **Overtime** (overtime request and approval). The backend logic for all three lives in [[modules/workforce-presence/overview|Workforce Presence]]; the UI entry points are the Calendar sidebar panel.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/leave/overview\|Leave]] | `ILeaveService` | Approved leave for calendar |
| **Depends on** | [[modules/workforce-presence/overview\|Workforce Presence]] | — | Holidays |
| **Depends on** | [[database/performance\|Performance]] | — | Review cycle dates |
| **Depends on** | [[modules/org-structure/overview\|Org Structure]] | `LegalEntityCountrySet` | Default holiday calendar country from legal entity country |
| **Depends on** | External API | Nager.Date | Phase 1 free country holiday source |
| **Consumed by** | [[modules/leave/overview\|Leave]] | `ICalendarConflictService` | Conflict detection for leave requests |

---

## Public Interface

```csharp
// ONEVO.Application.Features.Calendar/Public/ICalendarConflictService.cs
public interface ICalendarConflictService
{
    /// <summary>
    /// Returns calendar events that overlap with the given date range for an employee.
    /// Used by Leave module to show conflict warnings during submission and approval.
    /// Excludes 'leave' and 'holiday' event types (holidays are already factored into leave day calculation).
    /// </summary>
    Task<Result<LeaveConflictSummaryDto>> GetConflictsForDateRangeAsync(
        Guid employeeId, DateOnly startDate, DateOnly endDate, CancellationToken ct);
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
| `event_type` | `varchar(30)` | `meeting`, `company`, `team`, `personal`, `leave`, `holiday`, `training`, `out_of_office`, `review` |
| `source_type` | `varchar(30)` | `manual`, `leave_request`, `holiday`, `review_cycle`, `external_sync` |
| `source_id` | `uuid` | Polymorphic reference |
| `audience_type` | `varchar(20)` | `tenant`, `department`, `team`, `individual` |
| `audience_id` | `uuid` | FK → departments/teams/employees; null for tenant-wide |
| `color` | `varchar(7)` | Hex color; nullable |
| `recurrence` | `varchar(20)` | `none`, `daily`, `weekly`, `monthly` |
| `visibility` | `varchar(20)` | `public`, `team`, `private` |
| `external_id` | `varchar(255)` | Nullable external system event ID |
| `external_source` | `varchar(30)` | Nullable: `google_calendar`, `outlook_calendar`, `country_holiday` |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |

---

### `calendar_event_participants`

Used when `audience_type = individual`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `event_id` | `uuid` | FK -> calendar_events |
| `employee_id` | `uuid` | FK -> employees |

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
| `sync_direction` | `varchar(20)` | `pull_only`, `push_only`, `two_way`, `disabled` |
| `status` | `varchar(20)` | `active`, `reauth_required`, `paused`, `revoked`, `failed` |

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
| `sync_status` | `varchar(20)` | `synced`, `pending`, `failed`, `skipped`, `conflict` |

---

## Key Business Rules

1. **Unified calendar** — aggregates leave, holidays, review cycles, and custom events into one view via `source_type` + `source_id` polymorphic references.
2. **Conflict detection** — `ICalendarConflictService` queries overlapping events for a given employee + date range. Excludes `leave` and `holiday` event types. Severity: `review` and `company` events are **high**, `team` and `personal` are **medium**. See [[Userflow/Calendar/conflict-detection|Leave-Calendar Conflict Detection]].
3. **Hierarchy-scoped audience** — `audience_type` determines who receives the event. Available options are filtered by `IHierarchyScope`: a user can only target entities in their reporting chain. Super Admin bypasses scoping. For `department`/`team` audiences, participants are resolved server-side before conflict checks run.
4. **External sync** — events with `source_type = external_sync` are read-only unless the connection is `two_way` and the current user owns the connection.
5. **Legal entity holiday default** — when legal entity country is set, Calendar creates `holiday_calendar_settings` with `default_country_code` from the legal entity country.
6. **Holiday override** — Calendar admins can stop country holiday sync or set `override_country_code`. This changes the calendar only; it does not change the legal entity country.
7. **Country holiday provider** — Phase 1 uses Nager.Date for public holidays by year and ISO country code. Imported holidays are stored as `calendar_events` with `event_type = holiday`, `source_type = holiday`, and `external_source = country_holiday`.
8. **Google/Outlook sync** — users connect Google Calendar or Outlook Calendar with OAuth. Sync can be pull-only, push-only, two-way, or disabled per connection. Provider event IDs are tracked in `external_calendar_event_links` to prevent duplicates.

---

## Domain Events (intra-module — MediatR)

> These events are published and consumed within this module only. They never leave the module.

| Event | Published When | Handler |
|:------|:---------------|:--------|
| _(none)_ | — | — |

## Cross-Module Events (cross-module — MediatR INotification)

### Publishes

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| _(none)_ | — | — |

### Consumes

| Event | Source Module | Action Taken |
|:------|:-------------|:-------------|
| `LeaveApproved` | [[modules/leave/overview\|Leave]] | Create a `leave` calendar event for the approved leave period |
| `ReviewCycleStarted` | [[modules/performance/overview\|Performance]] | Create a `review` calendar event for the cycle dates |
| `EmployeeHired` | [[modules/core-hr/overview\|Core HR]] | Seed onboarding events for new employee |
| `LegalEntityCountrySet` | [[modules/org-structure/overview\|Org Structure]] | Create default holiday calendar settings from the legal entity country |

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
| GET | `/api/v1/calendar/conflicts` | `leave:create` or `leave:approve` | Get conflicts for employee + date range |
| POST | `/api/v1/calendar` | `calendar:write` | Create event |
| PUT | `/api/v1/calendar/{id}` | `calendar:write` | Update event (reschedule via drag-and-drop uses this) |
| DELETE | `/api/v1/calendar/{id}` | `calendar:write` | Delete event |

## Features

- [[Userflow/Calendar/calendar-integrations|Calendar Integrations]] - Country holidays, Google Calendar, and Outlook Calendar

- [[modules/calendar/calendar-events/overview|Calendar Events]] — Company, team, personal, leave, holiday, training, out-of-office, and review events
- [[Userflow/Calendar/conflict-detection|Conflict Detection]] — `ICalendarConflictService` for leave request conflict warnings

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] — All events are tenant-scoped
- [[backend/messaging/event-catalog|Event Catalog]] — Events sourced polymorphically from leave, holidays, review cycles
- [[current-focus/DEV2|DEV2: Backend HR + Workforce Core]] - Calendar backend implementation
- [[current-focus/DEV6|DEV6: Frontend HR + Workforce UI]] - Calendar UI implementation

See also: [[backend/module-catalog|Module Catalog]], [[modules/leave/overview|Leave]], [[modules/workforce-presence/overview|Workforce Presence]], [[Userflow/Calendar/conflict-detection|Leave-Calendar Conflict Detection]]

## Calendar Panel Navigation Items

The Calendar pillar expansion panel contains four items:

| Label | Route | Purpose |
|---|---|---|
| Calendar | `/calendar` | Unified view — leave dates, public holidays, review cycles, and shift schedule overlays |
| Schedules | `/calendar/schedule` | Shift schedule management — view and edit employee shift patterns |
| Attendance | `/calendar/attendance` | Attendance correction requests — adjust clock-in/out records |
| Overtime | `/calendar/overtime` | Overtime request submission and approval |

**Why scheduling lives in Calendar (not Workforce):**
Schedules, Attendance, and Overtime are time-visual concepts — they are understood in the context of a calendar timeline. The Workforce pillar is for doing work (projects, tasks). The Calendar pillar is for scheduling when work happens.

**Connection to WMS:**
- Shift schedule hours from this module feed into WMS Resource Management as the available capacity baseline for each employee.
- Approved timesheets from WMS Time Tracking create Attendance correction records here when discrepancies exist.
- Excess hours from approved timesheets create Overtime entries here for manager approval.

See [[Userflow/Work-Management/time-tracking-flow|Time Tracking Flow]] for the full overtime and attendance connection.
