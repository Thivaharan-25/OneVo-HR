# Calendar Events - End-to-End Logic

**Module:** Calendar
**Feature:** Calendar Events

---

## Get Calendar Events

### Flow

```
GET /api/v1/calendar?from=2026-04-01&to=2026-04-30
  -> CalendarController.GetEvents(from, to)
    -> [Authenticated]
    -> CalendarService.GetEventsAsync(from, to, ct)
      -> 1. Query calendar_events WHERE date range overlaps
      -> 2. Filter by Calendar visibility rules and management coverage where employee-data authority is required
      -> 3. Merge Time Off requests (source_type = 'time_off_request')
      -> 4. Merge holidays (source_type = 'holiday')
      -> 5. Merge external calendar events (source_type = 'external_sync')
      -> 6. Merge review cycles (source_type = 'review_cycle')
      -> 7. Merge employee schedule/shift overlays where supported
      -> Return Result.Success(eventDtos)
```

## Create Calendar Event

### Flow

```
POST /api/v1/calendar
  -> CalendarController.Create(CreateEventCommand)
    -> [RequirePermission("calendar:write")]
    -> CalendarService.CreateAsync(command, ct)
      -> 1. Validate title, start_date, end_date, event_type, audience
      -> 2. Validate actor authority for selected audience/participants
           -> if unauthorized, return 403
      -> 3. Check conflicts for selected participants
           -> warnings only; do not block authorized creation
      -> 4. INSERT into calendar_events
           -> source_type = 'manual', source_id = null
      -> 5. INSERT calendar_event_participants with response_status = 'pending' where invitation response is needed
      -> 6. Notify recipients through Inbox
      -> Return Result.Success(eventDto with conflict summary)
```

### Conflict Response Flow

```
Recipient opens invitation
  -> Calendar loads conflict summary
  -> UI shows inline actions:
       Accept anyway
       Reject
       More
  -> More contains:
       Request conflict resolution
       Nominate replacement only when eligible nominees exist
```

Rules:

- **Accept anyway** records conflict warning acknowledged and accepts the event.
- **Reject** requires a reason and sends it to the organizer/assigner.
- **Request conflict resolution** keeps the response pending and sends a message/explanation to the organizer.
- **Nominate replacement** is available only when calendar rules and delegation configuration return eligible nominees.
- Do not automatically revoke existing conflicting events.

### Error Scenarios

| Error | Handling |
|:------|:---------|
| End date before start date | Return 422 |
| Invalid event_type | Return 422 |
| Actor lacks audience/participant authority | Return 403 |
| Participant conflict | Return success with warning summary when actor has authority |
| Event not found (update/delete) | Return 404 |

## Legal Entity Holiday Calendar Default

### Flow

```
LegalEntityCountrySet(tenant_id, legal_entity_id, country_code)
  -> CalendarHolidaySettingsHandler
    -> 1. Create holiday_calendar_settings
       -> default_country_code = legal entity country
       -> override_country_code = null
       -> effective_country_code = default_country_code
       -> holiday_sync_enabled = true
       -> provider = "nager_date"
    -> 2. Queue holiday sync for current year and next year
    -> 3. Import public holidays as calendar_events
       -> event_type = "holiday"
       -> source_type = "holiday"
       -> external_source = "country_holiday"
```

## Change Holiday Calendar Country (Calendar Display)

This controls the Calendar visual display of holidays. It does not change any work schedule holiday country or Company timezone. Work schedule holiday country is managed in Time & Attendance > Schedules per-schedule.

### Flow

```
PUT /api/v1/calendar/holiday-settings/{id}
  body: { holiday_sync_enabled, override_country_code? }
  -> CalendarHolidaySettingsController.Update
    -> [RequirePermission("calendar:admin")]
    -> 1. Load setting and validate company tenant scope
    -> 2. If override_country_code is set, use it as effective country for Calendar display
    -> 3. If holiday_sync_enabled = false, stop future imports but keep existing events unless admin chooses resync
    -> 4. If country changed, mark current imported holiday events as superseded and queue resync
       Internal imported-event replacement is not a user-facing workflow status.
    -> 5. This does not change legal_entities.timezone or work_schedules.holiday_country_code
```

## Country Holiday Sync

### Flow

```
POST /api/v1/calendar/holiday-settings/{id}/sync?year=2026
  -> CalendarHolidaySyncService.SyncCountryHolidaysAsync
    -> 1. Resolve effective_country_code
    -> 2. Fetch Nager.Date /api/v3/PublicHolidays/{year}/{countryCode}
    -> 3. Upsert one all-day calendar_events row per holiday
    -> 4. Use external_id = "{countryCode}:{year}:{date}:{localName}" for deduplication
```

## Google/Outlook Calendar Connection

### Access

```
User opens Calendar (main sidebar item)
  -> Calendar page loads with normal calendar grid
  -> Top action bar contains [Connections] button alongside create event, filters, view controls
  -> User clicks [Connections]
  -> Centered modal dialog opens with title "Calendar Connections"
  -> Modal shows Google Calendar and Outlook Calendar connection cards
```

No sidebar item, sub-sidebar item, Settings page, or separate route is used.

### Connect Flow

```
User clicks Connect Google Calendar or Connect Outlook Calendar
  -> OAuth consent opens in new window/popup
  -> Provider authenticates user and grants calendar access
  -> OAuth callback:
     -> GET /api/v1/calendar/connections/{provider}/callback
     -> Backend stores encrypted tokens in external_calendar_connections
     -> status = active
  -> Control returns to OneVo
  -> Setup step appears inside the same Calendar Connections modal:
     -> Select which external calendar to sync (one primary calendar per provider)
     -> Choose sync mode:
        Import only (pull_only)
        Export OneVo events only (push_only)
        Two-way sync (two_way)
  -> User saves connection
  -> PUT /api/v1/calendar/connections/{id}
     -> Stores external_calendar_id, external_calendar_name, sync_direction
  -> Sync job begins on next cycle (every 15 minutes) or user clicks Sync now
  -> Imported events appear in normal Calendar view
```

### Imported Data Fields

Each external event stores:
- External event ID, calendar ID
- Event title (or "Busy" for private events)
- Start datetime, end datetime, all-day flag, timezone
- Event status
- Organizer name/email (if available)
- Attendee names/emails/status (if available)
- Recurrence metadata (if available)
- Last modified timestamp, provider change token / etag
- Location text (if available)
- Meeting link (if available)
- Private flag (`is_private`)

Not imported: email inbox content, attachments, full meeting notes/descriptions, events outside the sync window.

### Private External Events

```
External event has private/confidential visibility
  -> Store busy-block metadata only:
     provider event ID, calendar ID, start, end, all-day flag, timezone, is_private = true
  -> Display title as "Busy"
  -> Do not show description, attendees, location, meeting link, notes
  -> Include in conflict detection (conflict references "Busy" with time range)
```

### Default Sync Window

- Past 30 days to future 180 days
- Recurring events expanded only inside sync window
- Do not sync full historical calendar data

### Change Sync Mode

```
User opens Calendar Connections modal
  -> Clicks Change sync mode on connected card
  -> Selects new sync mode (Import only / Export OneVo events only / Two-way sync / Paused)
  -> PUT /api/v1/calendar/connections/{id}
     -> Updates sync_direction
  -> Next sync run applies new mode
```

### Sync Now (Manual)

```
User clicks Sync now on connected card
  -> POST /api/v1/calendar/connections/{id}/sync
  -> Runs immediate pull/push based on current sync_direction
  -> Updates last_synced_at on completion
```

### Disconnect Flow

```
User clicks Disconnect on connected card
  -> Confirmation dialog
  -> DELETE /api/v1/calendar/connections/{id}
  -> Backend removes stored OAuth tokens
  -> Future sync stops immediately
  -> Imported external events are hidden/removed from Calendar
     (unless converted to OneVo-owned events)
  -> OneVo-owned events remain in OneVo
  -> Connection card returns to Not connected state
```

### Reconnect Flow

```
Sync job detects token refresh failure
  -> Sets external_calendar_connections.status = reauth_required
  -> Connection card shows status: Needs reconnect
  -> User clicks Reconnect
  -> OAuth consent repeats
  -> On success:
     -> Tokens updated
     -> status = active
     -> Existing connection settings (selected calendar, sync mode) preserved
     -> Sync resumes on next cycle
```

## Related

- [[modules/calendar/calendar-events/overview|Calendar Events Overview]]
- [[modules/calendar/conflict-detection/overview|Conflict Detection]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
