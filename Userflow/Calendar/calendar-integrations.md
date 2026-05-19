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

## Background Sync Job

```
Hangfire recurring job: CalendarSyncJob
  Cadence: every 15 minutes
  Per active external_calendar_connection (status = active):

    1. Load connection; skip if sync_direction = disabled
    2. Check expires_at — if token expires within 5 minutes:
         a. Use refresh_token_encrypted to get new access token
         b. Update access_token_encrypted + expires_at
         c. If refresh fails → set status = reauth_required; skip connection
    3. Determine sync direction:
         pull_only  → fetch external events since last_synced_at → upsert calendar_events
         push_only  → find local events modified since last_synced_at → push to provider
         two_way    → pull first, then push (pull wins on same-event conflict; see below)
    4. Batch limit: 200 events per run per connection
    5. On success → update last_synced_at
    6. On error   → increment failure counter; after 3 consecutive failures
                    → set status = failed; notify user via notifications channel
```

Provider sync calls:
- **Google Calendar:** `events.list` with `updatedMin` + `syncToken` for incremental fetch; `events.insert` / `events.patch` / `events.delete` for outbound.
- **Outlook Calendar:** Microsoft Graph `calendarView` with `$deltaToken` for incremental fetch; `POST /events`, `PATCH /events/{id}`, `DELETE /events/{id}` for outbound.

---

## Conflict Resolution (Two-Way Sync)

A conflict occurs when the same event was modified in both ONEVO and the external calendar since the last sync. Detected via etag mismatch on pull.

```
Pull phase fetches event with external_etag != stored external_etag:
  -> Load external_calendar_event_links row
  -> If local calendar_event.updated_at > last_synced_at (local was also changed):
       CONFLICT — apply resolution rule:
         pull_wins  → overwrite local with external version; log conflict
         push_wins  → keep local; push local version to provider; log conflict
  -> Default resolution rule: pull_wins (external calendar is treated as authoritative)
  -> Set external_calendar_event_links.sync_status = conflict + log in last_error
  -> Admin can view conflicts in Calendar settings; manual resolution resets sync_status = synced
```

Conflict rules per sync direction:
| Scenario | Resolution |
|:---------|:-----------|
| Two-way, both sides changed | External wins (pull_wins) by default |
| Push-only, provider rejects etag | Retry with latest etag; if rejected twice, mark failed |
| Pull-only, local edit detected | Local edit is ignored; external version applied |
| Event deleted externally | Soft-delete local event; mark `source_type = external_sync` deletion |
| Event deleted locally in two-way | Attempt delete on provider; if fails, mark sync_status = failed |

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
