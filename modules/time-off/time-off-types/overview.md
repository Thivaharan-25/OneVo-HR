# Time Off Types

**Module:** Time Off
**Feature:** Time Off Types

---

## Purpose

Defines what Time Off types exist per tenant, such as Annual, Sick, Maternity, Compassionate, and Unpaid.

Time Off Type defines:
- Name
- Paid/unpaid
- Active/inactive
- Whether supporting document is required

Time Off Types do not own entitlement amount, carry-forward, approval, notice-period, consecutive limit, or request-limit rules. Those are policy rules in [[modules/time-off/time-off-policies/overview|Time Off Policies]].

Phase 1 does not define full-day, half-day, or hourly as canonical request modes on the type. All Time Off requests store `request_duration_minutes` directly. If UI duration shortcuts are added later, they are UI-only and must convert to explicit minutes before saving.

## Database Tables

### `time_off_types`

Core columns:

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `name` | `varchar(50)` | e.g., "Annual", "Sick", "Maternity" |
| `code` | `varchar(30)` | Unique per tenant when implemented |
| `description` | `text` | Nullable |
| `is_paid` | `boolean` | Type-level classification if supported |
| `requires_document` | `boolean` | Whether supporting document is required |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |

Deprecated/avoid in docs as type-level rules: `allow_full_day`, `allow_half_day`, `allow_hourly`, approval, document threshold, consecutive limit, entitlement, and carry-forward fields. If legacy schema still has them, treat policy as the source of truth for new product behavior.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/time-off/types` | `time_off:read` | List time off types |
| POST | `/api/v1/time-off/types` | `time_off:manage` | Create time off type |

## Related

- [[modules/time-off/overview|Time Off Module]]
- [[modules/time-off/time-off-policies/overview|Time Off Policies]]
- [[modules/time-off/time-off-entitlements/overview|Time Off Entitlements]]
- [[modules/time-off/time-off-requests/overview|Time Off Requests]]
