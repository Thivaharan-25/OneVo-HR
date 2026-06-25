# Integration Connections

**Module:** Configuration  
**Feature:** Integrations
**Phase:** Phase 2

---

## Purpose

Manages Phase 2 generic or legacy tenant integration connections. Phase 1 integrations do not use this feature: Stripe, PayHere, Paddle, Resend, Google Calendar, and Outlook Calendar use dedicated provider tables, not `integration_connections`.

## Database Tables

### `integration_connections`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `integration_type` | `varchar(50)` | Phase 2 generic or legacy tenant integrations only, e.g. `peoplehr`, `slack`, `lms` |
| `config_json` | `jsonb` | |
| `credentials_encrypted` | `bytea` | Encrypted |
| `status` | `varchar(20)` | `active`, `inactive`, `error` |
| `last_sync_at` | `timestamptz` | |

**Phase rule:** This feature is Phase 2 only. `peoplehr`, `slack`, and `lms` connections must not be exposed as usable Phase 1 connection flows.

**PeopleHR:** Phase 2 only. `peoplehr` connections are used by [[modules/data-import/peoplehr-full-migration|PeopleHR Full Migration]]. The connection card must support masked API key entry, permission preflight, last migration status, and audit links.

**Dedicated provider ownership:** Billing credentials are managed through Shared Platform `payment_gateway_credentials`; non-secret gateway metadata stays in `payment_gateway_configs`; Resend email delivery uses `platform_service_keys`, `notification_channels`, and `email_delivery_logs`; Google/Outlook user calendar sync uses `external_calendar_connections` and `external_calendar_event_links`. Configuration integration cards may link to those setup screens, but must not duplicate raw provider secrets.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/settings/integrations` | `settings:admin` | List integrations |
| POST | `/api/v1/settings/integrations` | `settings:admin` | Add integration |
| PUT | `/api/v1/settings/integrations/{id}` | `settings:admin` | Update integration config or rotate credentials |
| POST | `/api/v1/settings/integrations/{id}/test` | `settings:admin` | Test connection and required scopes |

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
