# Tenant Settings

**Module:** Configuration  
**Feature:** Tenant Settings

---

## Purpose

Core tenant configuration: timezone, date format, currency, work week days, work hours, privacy mode, and extensible settings.

## Database Tables

### `tenant_settings`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants, UNIQUE |
| `timezone` | `varchar(50)` | Default timezone |
| `date_format` | `varchar(20)` | |
| `currency_code` | `varchar(3)` | |
| `work_week_days_json` | `jsonb` | e.g., `[1,2,3,4,5]` |
| `work_hours_start` | `time` | |
| `work_hours_end` | `time` | |
| `privacy_mode` | `varchar(20)` | `full_transparency`, `partial`, `covert` |
| `data_retention_days_json` | `jsonb` | Per-data-type retention settings |
| `settings_json` | `jsonb` | Extensible settings |
| `updated_at` | `timestamptz` | |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/settings` | `settings:read` | Get tenant settings |
| PUT | `/api/v1/settings` | `settings:admin` | Update settings |

## Related

- [[modules/configuration/overview|Configuration Module]]
- [[frontend/architecture/overview|Monitoring Toggles]]
- [[frontend/architecture/overview|Employee Overrides]]
- [[frontend/architecture/overview|Integrations]]
- [[frontend/architecture/overview|Retention Policies]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/data-classification|Data Classification]]
- [[security/compliance|Compliance]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]]
