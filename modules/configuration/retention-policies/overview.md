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

- [[modules/configuration/overview|Configuration Module]]
- [[frontend/architecture/overview|Tenant Settings]]
- [[frontend/architecture/overview|Monitoring Toggles]]
- [[frontend/architecture/overview|Employee Overrides]]
- [[frontend/architecture/overview|Integrations]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/data-classification|Data Classification]]
- [[security/compliance|Compliance]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]]
