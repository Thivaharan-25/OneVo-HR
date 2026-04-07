# Leave Entitlements

**Module:** Leave  
**Feature:** Leave Entitlements

---

## Purpose

Calculated entitlement per employee per year based on policy + proration.

## Database Tables

### `leave_entitlements`
Key columns: `employee_id`, `leave_type_id`, `year`, `total_days`, `used_days` (updated on approval), `carried_forward_days`, `remaining_days` (computed).

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/leave/entitlements/{employeeId}` | `leave:read` | Get entitlements |

## Related

- [[leave|Leave Module]]
- [[balance-audit]]
- [[leave-requests]]
- [[leave-policies]]
- [[leave-types]]
- [[multi-tenancy]]
- [[error-handling]]
- [[migration-patterns]]
- [[retention-policies]]
- [[WEEK3-leave]]
