# Calendar Integrations Flow

**Module:** Calendar
**Phase:** 1
**Backend Owner:** Dev 2
**Frontend Owner:** Dev 6

---

## Purpose

Calendar supports two Phase 1 integration paths:

1. Country holiday calendars, defaulted from the company country.
2. User-connected Google Calendar and Outlook Calendar pull/push sync.

---

## Company Country Holiday Default

```
Operator sets company registration profile country
  -> Selects country
  -> Org Structure saves company profile country_id
  -> Org Structure publishes CompanyProfileCountrySet
  -> Calendar creates holiday_calendar_settings
     -> default_country_code = company country
     -> override_country_code = null
     -> holiday_sync_enabled = true
     -> provider = nager_date
  -> Calendar imports current-year and next-year holidays
```

The company country is the default calendar country. Changing the Calendar country later does not change the company registration profile country.

---

## Calendar Admin Override

```
Admin opens Calendar settings
  -> Selects tenant/company holiday settings
  -> Can disable holiday sync
  -> Can choose a different holiday calendar country
  -> Calendar saves override_country_code
  -> Calendar resyncs holidays for selected years
```

If holiday sync is disabled, existing imported holiday events remain visible unless the admin explicitly removes/resyncs them.

---

## Google/Outlook Calendar Connection

```
User opens Calendar connections
  -> Chooses Google Calendar or Outlook Calendar
  -> OAuth consent completes
  -> Backend stores encrypted tokens
  -> User chooses sync mode:
     -> pull_only
     -> push_only
     -> two_way
     -> disabled
  -> Sync job imports or exports events
```

Provider event IDs are stored in `external_calendar_event_links` so retries do not create duplicates.

---

## Data Rules

- Country holidays are stored as `calendar_events` with `event_type = holiday`, `source_type = holiday`, and `external_source = country_holiday`.
- Google events use `external_source = google_calendar`.
- Outlook events use `external_source = outlook_calendar`.
- Two-way sync must respect ONEVO permissions before pushing edits/deletes to external calendars.
- Token fields are encrypted and never returned to the frontend.

---

## Related

- [[modules/calendar/overview|Calendar Module]]
- [[modules/calendar/calendar-events/end-to-end-logic|Calendar Events Logic]]
- [[database/schemas/calendar|Calendar Schema]]
- [[modules/org-structure/legal-entities/overview|Legal Entities]]
- [[current-focus/DEV2|DEV2]]
- [[current-focus/DEV6|DEV6]]
