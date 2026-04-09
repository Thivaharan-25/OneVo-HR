# Leave Policies

**Module:** Leave  
**Feature:** Leave Policies

---

## Purpose

Country/level-specific leave policies with versioning via `superseded_by_id`.

## Database Tables

### `leave_policies`
Key columns: `leave_type_id`, `country_id` (nullable = global), `job_level_id` (nullable = all levels), `annual_entitlement_days`, `carry_forward_max_days`, `carry_forward_expiry_months`, `accrual_method` (`annual`, `monthly`, `daily`), `proration_method` (`calendar_days`, `working_days`), `superseded_by_id` (self-referencing), `effective_from`.

**Active policy:** `WHERE superseded_by_id IS NULL` for given leave type + country + job level.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/leave/policies` | `leave:manage` | List policies |
| POST | `/api/v1/leave/policies` | `leave:manage` | Create policy |

## Related

- [[modules/leave/overview|Leave Module]]
- [[modules/leave/balance-audit/overview|Balance Audit]]
- [[modules/leave/leave-entitlements/overview|Leave Entitlements]]
- [[modules/leave/leave-requests/overview|Leave Requests]]
- [[modules/leave/leave-types/overview|Leave Types]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[backend/messaging/error-handling|Error Handling]]
- [[security/compliance|Compliance]]
- [[current-focus/DEV1-leave|DEV1: Leave]]
