# Calendar Events — End-to-End Logic

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
      -> 1. Get current user context (employee_id, department, teams)
      -> 2. Query calendar_events WHERE date range overlaps
         -> Filter by visibility:
            -> 'public' -> all employees see
            -> 'team' -> same team/department only
            -> 'private' -> own events only
      -> 3. Merge with leave requests (source_type = 'leave_request')
      -> 4. Merge with holidays (source_type = 'holiday')
      -> 5. Merge with external calendar events (source_type = 'external_sync')
      -> 6. Merge with review cycles (source_type = 'review_cycle')
      -> Return Result.Success(eventDtos)
```

## Create Calendar Event

### Flow

```
POST /api/v1/calendar
  -> CalendarController.Create(CreateEventCommand)
    -> [Authenticated]
    -> CalendarService.CreateAsync(command, ct)
      -> 1. Validate: title, start_date, end_date, event_type, visibility
      -> 2. INSERT into calendar_events
         -> source_type = 'manual', source_id = null
      -> Return Result.Success(eventDto)
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| End date before start date | Return 422 |
| Invalid event_type | Return 422 |
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

## Change Holiday Calendar Country

### Flow

```
PUT /api/v1/calendar/holiday-settings/{id}
  body: { holiday_sync_enabled, override_country_code? }
  -> CalendarHolidaySettingsController.Update
    -> [RequirePermission("calendar:admin")]
    -> 1. Load setting and validate company tenant scope
    -> 2. If override_country_code is set, use it as effective country
    -> 3. If holiday_sync_enabled = false, stop future imports but keep existing events unless admin chooses resync
    -> 4. If country changed, mark current imported holiday events as superseded and queue resync
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

## Google/Outlook Calendar Sync

### Flow

```
User connects Google or Outlook calendar
  -> OAuth callback stores external_calendar_connections with encrypted tokens
  -> Sync job pulls provider events into calendar_events
  -> OneVo-created events are pushed out only when sync_direction is push_only or two_way
  -> external_calendar_event_links tracks provider event IDs and etags
```

## Related

- [[frontend/architecture/overview|Calendar Events Overview]]
- [[frontend/architecture/overview|Conflict Detection]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
