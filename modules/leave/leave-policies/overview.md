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

- [[leave|Leave Module]]
- [[balance-audit]]
- [[leave-entitlements]]
- [[leave-requests]]
- [[leave-types]]
- [[multi-tenancy]]
- [[error-handling]]
- [[compliance]]
- [[WEEK3-leave]]
