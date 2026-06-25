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
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `date` | `date` | |
| `process_name` | `varchar(100)` | e.g., `chrome.exe` - authoritative matching key |
| `application_name` | `varchar(255)` | e.g., "Google Chrome" - display metadata only |
| `application_category` | `varchar(100)` | FK-like to `application_categories` |
| `window_title_hash` | `varchar(64)` | SHA-256 hash (privacy - never store raw title) |
| `total_seconds` | `int` | Time spent |
| `is_productive` | `boolean` | Nullable - from `application_categories` |

## Key Business Rules

1. **Process name is authoritative** for app identity, allowlist/blocklist matching, and catalog joins.
2. **Application name is display metadata only** and must not be used as the primary matching key.

1. **Window titles are hashed** (SHA-256) before storage - never store raw window titles.
2. **Never log application names or window titles** in application logs - log counts only.
3. Data is append-only.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/activity/apps/{employeeId}` | `monitoring:view` | Application usage breakdown |

See also: [[database/schemas/activity-monitoring#`application_categories`|Application Categories Schema]]
