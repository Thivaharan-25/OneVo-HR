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

- [[modules/leave/overview|Leave Module]]
- [[modules/leave/balance-audit/overview|Balance Audit]]
- [[modules/leave/leave-requests/overview|Leave Requests]]
- [[modules/leave/leave-policies/overview|Leave Policies]]
- [[modules/leave/leave-types/overview|Leave Types]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[backend/messaging/error-handling|Error Handling]]
- [[database/migration-patterns|Migration Patterns]]
- [[modules/configuration/retention-policies/overview|Retention Policies]]
- [[current-focus/DEV1-leave|DEV1: Leave]]
