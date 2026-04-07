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

- [[configuration|Configuration Module]]
- [[configuration/monitoring-toggles/overview|Monitoring Toggles]]
- [[configuration/employee-overrides/overview|Employee Overrides]]
- [[configuration/integrations/overview|Integrations]]
- [[configuration/retention-policies/overview|Retention Policies]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[data-classification]]
- [[compliance]]
- [[WEEK1-shared-platform]]
