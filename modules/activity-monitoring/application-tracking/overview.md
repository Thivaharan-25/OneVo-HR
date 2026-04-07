# Application Tracking

**Module:** Activity Monitoring
**Feature:** Application Tracking

---

## Purpose

Tracks time spent per application per day per employee. Applications are categorized via tenant-configurable `application_categories` table. Window titles are hashed (SHA-256) for privacy.

## Database Tables

### `application_usage`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `date` | `date` | |
| `application_name` | `varchar(255)` | e.g., "Google Chrome" |
| `application_category` | `varchar(100)` | FK-like to `application_categories` |
| `window_title_hash` | `varchar(64)` | SHA-256 hash (privacy — never store raw title) |
| `total_seconds` | `int` | Time spent |
| `is_productive` | `boolean` | Nullable — from `application_categories` |

## Key Business Rules

1. **Window titles are hashed** (SHA-256) before storage — never store raw window titles.
2. **Never log application names or window titles** in application logs — log counts only.
3. Data is append-only.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/activity/apps/{employeeId}` | `workforce:view` | Application usage breakdown |

See also: [[activity-monitoring/application-categories]]
