# Leave Types

**Module:** Leave  
**Feature:** Leave Types

---

## Purpose

Defines leave types per tenant (Annual, Sick, Maternity, etc.) with configuration for paid/unpaid, approval, document requirements, and max consecutive days.

## Database Tables

### `leave_types`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(50)` | e.g., "Annual", "Sick", "Maternity" |
| `is_paid` | `boolean` | |
| `requires_approval` | `boolean` | |
| `requires_document` | `boolean` | Medical certificate etc. |
| `max_consecutive_days` | `int` | Nullable |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/leave/types` | `leave:read` | List leave types |
| POST | `/api/v1/leave/types` | `leave:manage` | Create leave type |

## Related

- [[modules/leave/overview|Leave Module]]
- [[modules/leave/balance-audit/overview|Balance Audit]]
- [[modules/leave/leave-entitlements/overview|Leave Entitlements]]
- [[modules/leave/leave-policies/overview|Leave Policies]]
- [[modules/leave/leave-requests/overview|Leave Requests]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[backend/messaging/error-handling|Error Handling]]
- [[current-focus/DEV1-leave|DEV1: Leave]]
