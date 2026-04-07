# Retention Policies

**Module:** Configuration  
**Feature:** Retention Policies

---

## Purpose

Configurable data retention per data type (screenshots, verification photos, activity snapshots, audit logs).

## Database Tables

### `retention_policies`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `data_type` | `varchar(50)` | `screenshots`, `verification_photos`, `activity_snapshots`, `audit_logs` |
| `retention_days` | `int` | |
| `created_at` | `timestamptz` | |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/settings/retention` | `settings:admin` | Retention policies |
| PUT | `/api/v1/settings/retention` | `settings:admin` | Update retention |

## Related

- [[configuration|Configuration Module]]
- [[configuration/tenant-settings/overview|Tenant Settings]]
- [[configuration/monitoring-toggles/overview|Monitoring Toggles]]
- [[configuration/employee-overrides/overview|Employee Overrides]]
- [[configuration/integrations/overview|Integrations]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[data-classification]]
- [[compliance]]
- [[WEEK1-shared-platform]]
