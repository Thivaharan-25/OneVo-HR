# Calendar - Schema

**Module:** [[modules/calendar/overview|Calendar]]
**Phase:** Phase 1
**Tables:** 5

---

## `calendar_events`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `title` | `varchar(200)` | |
| `description` | `text` | Nullable |
| `start_date` | `timestamptz` | |
| `end_date` | `timestamptz` | |
| `source_type` | `varchar(30)` | `manual`, `time_off_request`, `holiday`, `review_cycle`, `external_sync`, `schedule_overlay` |
| `source_id` | `uuid` | Polymorphic reference |
| `color` | `varchar(7)` | Nullable hex color |
| `recurrence` | `varchar(20)` | `none`, `daily`, `weekly`, `monthly` |
| `external_id` | `varchar(255)` | Nullable external system event ID, used for deduplication |
| `external_source` | `varchar(30)` | Nullable: `google_calendar`, `outlook_calendar`, `country_holiday` |
| `is_all_day` | `boolean` | Default false; true for all-day events |
| `timezone` | `varchar(50)` | IANA timezone; nullable for all-day events |
| `event_status` | `varchar(20)` | `confirmed`, `tentative`, `cancelled`; nullable for manual events |
| `is_private` | `boolean` | Default false; true for private external events displayed as "Busy" |
| `organizer_name` | `varchar(200)` | Nullable; from external provider |
| `organizer_email` | `varchar(255)` | Nullable; from external provider |
| `location` | `varchar(500)` | Nullable; location text from external provider |
| `meeting_link` | `varchar(500)` | Nullable; meeting URL from external provider |
| `external_attendees` | `jsonb` | Nullable; attendee list from external provider: `[{name, email, status}]`. Non-employee attendees from Google/Outlook are stored here, not in `calendar_event_participants` |
| `recurrence_rule` | `text` | Nullable; RRULE string from external provider |
| `external_updated_at` | `timestamptz` | Nullable; last modified timestamp from provider |
| `created_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `created_by_id` -> [[database/schemas/infrastructure#`users`|users]]

---

## `calendar_event_participants`


| Column | Type | Notes |
|:-------|:-----|:------|
| `event_id` | `uuid` | FK -> calendar_events |
| `employee_id` | `uuid` | FK -> employees |
| `response_status` | `varchar(30)` | `pending`, `accepted`, `rejected`, `resolution_requested`, `replacement_nominated` when supported |
| `response_reason` | `text` | Nullable; required for rejection |

**Foreign Keys:** `event_id` -> [[#`calendar_events`|calendar_events]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]]

---

## `holiday_calendar_settings`

Per-legal-entity country holiday calendar settings for Calendar display. When legal entity country is set, Calendar creates a default row using the legal entity country. This table controls which holidays appear on the Calendar view. It is separate from `work_schedules.holiday_country_code`, which controls per-schedule holiday selection in Time & Attendance. Neither setting affects `legal_entities.timezone`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `legal_entity_id` | `uuid` | FK -> legal_entities |
| `default_country_code` | `char(2)` | ISO 3166-1 alpha-2 from the legal entity country |
| `override_country_code` | `char(2)` | Nullable; admin-selected calendar country override |
| `effective_country_code` | `char(2)` | Derived from override_country_code or default_country_code |
| `holiday_sync_enabled` | `boolean` | Admin can stop country holiday sync from Calendar screen |
| `provider` | `varchar(30)` | Phase 1 default: `nager_date`; fallback: `manual` |
| `last_synced_year` | `integer` | Nullable |
| `last_synced_at` | `timestamptz` | Nullable |
| `updated_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Unique:** `(tenant_id, legal_entity_id)`

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `legal_entity_id` -> [[database/schemas/org-structure#`legal_entities`|legal_entities]], `updated_by_id` -> [[database/schemas/infrastructure#`users`|users]]

---

## `external_calendar_connections`

User-level Google Calendar and Outlook Calendar OAuth connections. Tokens are encrypted using the shared encryption service; raw tokens are never logged or returned.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `user_id` | `uuid` | FK -> users |
| `provider` | `varchar(30)` | `google_calendar`, `outlook_calendar` |
| `external_account_email` | `varchar(255)` | Connected Google/Microsoft account email |
| `external_calendar_id` | `varchar(255)` | Calendar ID selected for sync; nullable means primary/default |
| `external_calendar_name` | `varchar(255)` | Display name of the selected external calendar |
| `access_token_encrypted` | `bytea` | Nullable; short-lived |
| `refresh_token_encrypted` | `bytea` | Encrypted refresh token |
| `scopes` | `jsonb` | Granted scopes |
| `sync_direction` | `varchar(20)` | `pull_only`, `push_only`, `two_way`, `disabled` |
| `status` | `varchar(20)` | `active`, `reauth_required`, `paused`, `revoked`, `failed` |
| `sync_token_encrypted` | `bytea` | Nullable encrypted Google Calendar `syncToken` for incremental fetch |
| `delta_link_encrypted` | `bytea` | Nullable encrypted Microsoft Graph delta link/token for incremental fetch |
| `failure_count` | `integer` | Consecutive sync failures; reset to 0 after successful sync |
| `last_synced_at` | `timestamptz` | Nullable |
| `last_successful_sync_at` | `timestamptz` | Nullable |
| `last_error` | `text` | Nullable last provider/sync error |
| `expires_at` | `timestamptz` | Nullable |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Unique:** `(tenant_id, user_id, provider, external_calendar_id)`

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `user_id` -> [[database/schemas/infrastructure#`users`|users]]

**Token ownership rule:** User-level Google/Outlook Calendar access and incremental sync state are stored here (`connection_scope = 'employee'`). `tenant_integration_credentials` is only for tenant-scope connected integrations (`connection_scope = 'tenant'`), not per-user calendar sync.

---

## `external_calendar_event_links`

Idempotency and sync state for events pulled from or pushed to Google/Outlook.

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

**Unique:** `(tenant_id, provider, external_calendar_id, external_event_id)`

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `calendar_event_id` -> [[#`calendar_events`|calendar_events]], `external_calendar_connection_id` -> [[#`external_calendar_connections`|external_calendar_connections]]

---

## Related

- [[modules/calendar/overview|Calendar Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]
