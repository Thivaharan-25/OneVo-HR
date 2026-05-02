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
| `event_type` | `varchar(30)` | `meeting`, `company`, `team`, `personal`, `leave`, `holiday`, `training`, `out_of_office`, `review` |
| `source_type` | `varchar(30)` | `manual`, `leave_request`, `holiday`, `review_cycle`, `external_sync` |
| `source_id` | `uuid` | Polymorphic reference |
| `audience_type` | `varchar(20)` | `tenant`, `department`, `team`, `individual` |
| `audience_id` | `uuid` | FK to departments/teams/employees depending on audience_type; null for tenant-wide |
| `color` | `varchar(7)` | Nullable hex color |
| `recurrence` | `varchar(20)` | `none`, `daily`, `weekly`, `monthly` |
| `visibility` | `varchar(20)` | `public`, `team`, `private` |
| `external_id` | `varchar(255)` | Nullable external system event ID, used for deduplication |
| `external_source` | `varchar(30)` | Nullable: `google_calendar`, `outlook_calendar`, `country_holiday` |
| `created_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `created_by_id` -> [[database/schemas/infrastructure#`users`|users]]

---

## `calendar_event_participants`

Used only when `calendar_events.audience_type = individual`. For tenant, department, and team audiences, participants are resolved server-side from org hierarchy.

| Column | Type | Notes |
|:-------|:-----|:------|
| `event_id` | `uuid` | FK -> calendar_events |
| `employee_id` | `uuid` | FK -> employees |

**Foreign Keys:** `event_id` -> [[#`calendar_events`|calendar_events]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]]

---

## `holiday_calendar_settings`

Per-tenant or per-legal-entity country holiday calendar settings. When a legal entity is created, Calendar creates a default row using the legal entity country.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `legal_entity_id` | `uuid` | FK -> legal_entities; nullable for tenant default |
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
| `access_token_encrypted` | `bytea` | Nullable; short-lived |
| `refresh_token_encrypted` | `bytea` | Encrypted refresh token |
| `scopes` | `jsonb` | Granted scopes |
| `sync_direction` | `varchar(20)` | `pull_only`, `push_only`, `two_way`, `disabled` |
| `status` | `varchar(20)` | `active`, `reauth_required`, `paused`, `revoked`, `failed` |
| `last_synced_at` | `timestamptz` | Nullable |
| `expires_at` | `timestamptz` | Nullable |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Unique:** `(tenant_id, user_id, provider, external_calendar_id)`

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `user_id` -> [[database/schemas/infrastructure#`users`|users]]

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
