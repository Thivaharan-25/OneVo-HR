# Integration Connections

**Module:** Configuration  
**Feature:** Integrations

---

## Purpose

Manages external integration connections (PeopleHR, Stripe, Resend, Google Calendar, Slack, LMS).

## Database Tables

### `integration_connections`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `integration_type` | `varchar(50)` | `peoplehr`, `stripe`, `resend`, `google_calendar`, `slack`, `lms` |
| `config_json` | `jsonb` | |
| `credentials_encrypted` | `bytea` | Encrypted |
| `status` | `varchar(20)` | `active`, `inactive`, `error` |
| `last_sync_at` | `timestamptz` | |

**PeopleHR:** `peoplehr` connections are used by [[modules/data-import/peoplehr-full-migration|PeopleHR Full Migration]]. The connection card must support masked API key entry, permission preflight, last migration status, and audit links.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/settings/integrations` | `settings:admin` | List integrations |
| POST | `/api/v1/settings/integrations` | `settings:admin` | Add integration |

## Related

- [[modules/configuration/overview|Configuration Module]]
- [[modules/data-import/peoplehr-full-migration|PeopleHR Full Migration]]
- [[frontend/architecture/overview|Tenant Settings]]
- [[frontend/architecture/overview|Monitoring Toggles]]
- [[frontend/architecture/overview|Employee Overrides]]
- [[frontend/architecture/overview|Retention Policies]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/data-classification|Data Classification]]
- [[security/compliance|Compliance]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]]
