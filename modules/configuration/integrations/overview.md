# Integration Connections

**Module:** Configuration  
**Feature:** Integrations

---

## Purpose

Manages external integration connections (Stripe, Resend, Google Calendar, Slack, LMS).

## Database Tables

### `integration_connections`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `integration_type` | `varchar(50)` | `stripe`, `resend`, `google_calendar`, `slack`, `lms` |
| `config_json` | `jsonb` | |
| `credentials_encrypted` | `bytea` | Encrypted |
| `status` | `varchar(20)` | `active`, `inactive`, `error` |
| `last_sync_at` | `timestamptz` | |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/settings/integrations` | `settings:admin` | List integrations |
| POST | `/api/v1/settings/integrations` | `settings:admin` | Add integration |

## Related

- [[configuration|Configuration Module]]
- [[configuration/tenant-settings/overview|Tenant Settings]]
- [[configuration/monitoring-toggles/overview|Monitoring Toggles]]
- [[configuration/employee-overrides/overview|Employee Overrides]]
- [[configuration/retention-policies/overview|Retention Policies]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[data-classification]]
- [[compliance]]
- [[WEEK1-shared-platform]]
