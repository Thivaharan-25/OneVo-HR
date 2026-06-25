# Calendar Integrations Flow

**Module:** Calendar
**Phase:** 1
**Backend Owner:** Dev 2
**Frontend Owner:** Dev 6

---

## Purpose

Calendar supports two Phase 1 integration paths:

1. Country holiday calendars, defaulted from the legal entity country.
2. User-connected Google Calendar and Outlook Calendar pull/push sync.

This flow belongs to **Calendar** and Calendar settings. It handles Calendar display holidays, sharing, reminders, and external sync. It does not move **Schedules**, **Clock-in Policy**, **Overtime Rules**, or **Attendance** out of Time & Attendance.

> **Boundary:** Calendar holiday settings control which holidays appear on the Calendar display. Work schedule holiday country is a separate per-schedule setting managed in Time & Attendance > Schedules. Calendar holiday settings do not affect schedule timezone or schedule holiday selection.

---

## Legal Entity Country Holiday Default

```
Admin sets legal entity country
  -> Selects country
  -> Org Structure saves legal entity country_id
  -> Org Structure publishes LegalEntityCountrySet
  -> Calendar creates holiday_calendar_settings
     -> legal_entity_id = resolved from the selected Company context
     -> default_country_code = legal entity country
     -> override_country_code = null
     -> holiday_sync_enabled = true
     -> provider = nager_date
  -> Calendar imports current-year and next-year holidays
```

The legal entity country is the default calendar country for employees under that legal entity. Changing the Calendar country later does not change the legal entity registration country.

---

## Calendar Admin Override

```
Admin opens Calendar settings for the selected Company context
  -> Company is determined by the topbar selection; legal_entity_id is resolved internally
  -> Can disable holiday sync
  -> Can choose a different holiday calendar country for Calendar display
  -> Calendar saves override_country_code
  -> Calendar resyncs holidays for selected years
```

This override changes the Calendar display country only. It does not change the Company timezone, the Company registration country, or any work schedule holiday country. Work schedule holiday country is configured per-schedule in Time & Attendance > Schedules.

If holiday sync is disabled, existing imported holiday events remain visible unless the admin explicitly removes/resyncs them.

---

## Google/Outlook Calendar Connection - Navigation and Access

Calendar integrations are accessed exclusively from the Calendar screen. There is no Calendar Connections sidebar item, sub-sidebar item, Settings page, profile menu entry, or global shell button.

### Button Placement

- Calendar is a main sidebar item at `/calendar`.
- When the user opens Calendar, they see the normal Calendar page with month/week/day grid.
- In the Calendar page **top action bar**, a `[Connections]` button is placed alongside existing actions (create event, filters, view controls).
- The `[Connections]` button is always visible in the Calendar top action bar for authenticated users.

### Modal Behavior

- Clicking `[Connections]` opens a **centered modal dialog** over the Calendar page.
- The modal title is **Calendar Connections**.
- The modal is not a right-side drawer, not a full-page route, and not a sub-sidebar panel.
- Opening the modal does not change the Calendar sidebar or sub-sidebar state.
- The Calendar URL does not change when the modal opens.

---

## Calendar Connections Modal Content

The modal shows exactly two connection cards:

1. **Google Calendar**
2. **Outlook Calendar**

Phase 1 supports Google Calendar and Outlook Calendar only. Do not add Slack, Teams, Zoom, or other calendar providers.

### Connection Card Fields

Each card displays:

| Field | When Shown |
|:------|:-----------|
| Connection status | Always |
| Connected account email | When connected |
| Selected external calendar name | When connected |
| Sync mode | When connected |
| Last synced time | When connected |
| Sync health | When connected |

### Connection Status Values

| Status | Meaning |
|:-------|:--------|
| Not connected | No OAuth connection exists |
| Connected | Active connection, sync running |
| Needs reconnect | Token refresh failed; user must re-authorize |

### Card Actions

| Action | When Available |
|:-------|:--------------|
| Connect | When status is Not connected |
| Change sync mode | When connected |
| Sync now | When connected |
| Disconnect | When connected or Needs reconnect |
| Reconnect | Only when status is Needs reconnect |

---

## Connection Flow

```
1. User opens Calendar
2. User clicks [Connections] button in the Calendar page top action bar
3. Calendar Connections modal opens (centered dialog)
4. User clicks Connect Google Calendar or Connect Outlook Calendar
5. OAuth flow opens in a new window/popup
6. After successful OAuth, control returns to OneVo
7. Setup step appears inside the same modal:
   -> Select which external calendar to sync
   -> Choose sync mode (Import only / Export OneVo events only / Two-way sync)
8. User saves connection
9. Sync job begins
10. Imported external events appear inside the normal Calendar view
```

Phase 1 supports selecting **one primary external calendar per provider account**. The user picks which calendar (e.g., "Work Calendar", "Personal Calendar") during setup. The selected calendar name is stored in `external_calendar_connections.external_calendar_name`.

---

## Sync Modes

| Display Label | Internal Value | Behavior |
|:--------------|:---------------|:---------|
| Import only | `pull_only` | External calendar events are imported into OneVo Calendar. OneVo events are not pushed to the external calendar. |
| Export OneVo events only | `push_only` | OneVo-created calendar events are pushed to the external calendar. External calendar events are not imported into OneVo. |
| Two-way sync | `two_way` | External calendar events are imported into OneVo. OneVo-created calendar events are pushed to the external calendar. OneVo can update OneVo-created exported events. Do not allow OneVo to edit events that were created directly in Google/Outlook unless a later product rule explicitly supports it. |
| Paused | `disabled` | Sync is stopped. The connection remains saved. No new import or export sync runs. |

---

## Data Imported from Google/Outlook

The following fields are imported and stored for each external event:

- External event ID
- Calendar ID
- Event title
- Start datetime
- End datetime
- All-day flag
- Timezone
- Event status
- Organizer name/email (if available)
- Attendee names/emails/status (if available)
- Recurrence metadata (if available)
- Last modified timestamp
- Provider change token / etag
- Location text (if available)
- Meeting link (if available)

### Data NOT Imported/Stored

- Email inbox content
- Attachments
- Full meeting notes/descriptions unless explicitly enabled later
- Private event details (beyond busy-block metadata)
- Events outside the sync window

---

## Private External Events

Private events from Google/Outlook are imported with limited metadata only.

### Stored for Private Events

- Provider event ID
- Calendar ID
- Start datetime
- End datetime
- All-day flag
- Timezone
- Private status flag (`is_private = true`)

### Display for Private Events

- Title shown as: **Busy**
- Do not show: description, attendees, location, meeting link, notes

### Conflict Behavior for Private Events

- Private external events are included in conflict detection.
- Conflict warnings reference the private event as "Busy" with its time range.

---

## Default Sync Window

- **Past:** 30 days
- **Future:** 180 days
- Do not sync full historical calendar data by default.
- Recurring events from external calendars are only expanded/displayed inside the sync window.

---

## Calendar Display of External Events

- Imported external events appear inside the normal Calendar grid/list alongside OneVo events.
- External events are **read-only** unless they are OneVo-created exported events (push_only or two_way).
- Each external event shows a small source label:
  - **Google Calendar**
  - **Outlook Calendar**
- Private external events display as **Busy**.
- External events must visually match the OneVo Calendar design language. Do not use a separate foreign-looking card style.
- External events use `source_type = 'external_sync'` and `external_source = 'google_calendar'` or `'outlook_calendar'`.

---

## Conflict Handling with External Events

- External calendar events **must be included** in conflict checks (`ICalendarConflictService`).
- Conflicts are **warnings, not blockers**.
- Do not block sending a OneVo event because of conflicts.
- Do not block accepting a OneVo event because of conflicts.
- Show conflict count and conflict period before sending.
- Show the same conflict warning to the recipient before accepting.

### Recipient Event Response Actions

Always visible:

- **Accept anyway**
- **Reject**
- **More**

Inside **More**:

- **Request conflict resolution** - asks the event creator/assigner to review the conflict. Does not automatically cancel or move any event. Creates an inbox/request item for the event creator/assigner.
- **Nominate replacement** - only shown when the recipient has eligible people under their reporting hierarchy. Recipient selects a replacement person. The event creator/assigner receives the nomination as an inbox/request item. The replacement is not automatically assigned until the creator/assigner confirms.

Do not show "Nominate replacement" when no eligible nominees exist. Do not show disabled nominee text. Do not show an explanation when no nominee exists.

### Authority Rule

Only block the event if the sender does not have authority to assign/invite that person. Conflict is a warning. Authority is enforcement.

---

## Disconnect Behavior

- Disconnect removes the stored OAuth token/connection.
- Future sync stops immediately.
- Already imported external events are **hidden/removed** from OneVo Calendar unless they were converted into OneVo-owned events.
- OneVo-owned events remain in OneVo regardless of disconnect.

---

## Reconnect Behavior

- If token refresh fails during a sync run, the connection status changes to **Needs reconnect**.
- User can click **Reconnect** in the Calendar Connections modal.
- Reconnect repeats OAuth and keeps the existing connection settings (selected calendar, sync mode) when possible.

---

## Background Sync Job

```
Hangfire recurring job: CalendarSyncJob
  Cadence: every 15 minutes
  Per active external_calendar_connection (status = active):

    1. Load connection; skip if sync_direction = disabled
    2. Check expires_at - if token expires within 5 minutes:
         a. Use refresh_token_encrypted to get new access token
         b. Update access_token_encrypted + expires_at
         c. If refresh fails -> set status = reauth_required; skip connection
    3. Determine sync direction:
         pull_only  -> fetch external events since last_synced_at -> upsert calendar_events
         push_only  -> find local events modified since last_synced_at -> push to provider
         two_way    -> pull first, then push (pull wins on same-event conflict; see below)
    4. Apply sync window: past 30 days to future 180 days
    5. Batch limit: 200 events per run per connection
    6. On success -> update last_synced_at
    7. On error   -> increment failure counter; after 3 consecutive failures
                    -> set status = failed; notify user via notifications channel
```

Provider sync calls:
- **Google Calendar:** `events.list` with `updatedMin` + `syncToken` for incremental fetch; `events.insert` / `events.patch` / `events.delete` for outbound.
- **Outlook Calendar:** Microsoft Graph `calendarView` with `$deltaToken` for incremental fetch; `POST /events`, `PATCH /events/{id}`, `DELETE /events/{id}` for outbound.

---

## Conflict Resolution (Two-Way Sync)

A conflict occurs when the same event was modified in both ONEVO and the external calendar since the last sync. Detected via etag mismatch on pull.

This sync conflict is different from an employee scheduling conflict. Scheduling conflicts remain warnings; authority rules are the only hard enforcement for assigning or inviting employees.

```
Pull phase fetches event with external_etag != stored external_etag:
  -> Load external_calendar_event_links row
  -> If local calendar_event.updated_at > last_synced_at (local was also changed):
       CONFLICT - apply resolution rule:
         pull_wins  -> overwrite local with external version; log conflict
         push_wins  -> keep local; push local version to provider; log conflict
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
- Private external events store only busy-block metadata (`is_private = true`); display title is "Busy".

---

## Related

- [[modules/calendar/overview|Calendar Module]]
- [[modules/calendar/calendar-events/end-to-end-logic|Calendar Events Logic]]
- [[database/schemas/calendar|Calendar Schema]]
- [[modules/org-structure/legal-entities/overview|Legal Entities]]
- [[current-focus/DEV2|DEV2]]
- [[current-focus/DEV6|DEV6]]
