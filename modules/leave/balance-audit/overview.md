# Leave Balance Audit

**Module:** Leave  
**Feature:** Balance Audit

---

## Purpose

Audit trail for all leave balance changes.

## Database Tables

### `leave_balances_audit`
Fields: `employee_id`, `leave_type_id`, `change_type` (`accrual`, `deduction`, `carry_forward`, `forfeiture`, `adjustment`), `days_changed` (positive/negative), `balance_after`, `reason`, `created_at`.

## Related

- [[modules/leave/overview|Leave Module]]
- [[modules/leave/leave-requests/overview|Leave Requests]]
- [[modules/leave/leave-entitlements/overview|Leave Entitlements]]
- [[modules/leave/leave-policies/overview|Leave Policies]]
- [[modules/leave/leave-types/overview|Leave Types]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
- [[security/data-classification|Data Classification]]
- [[modules/configuration/retention-policies/overview|Retention Policies]]
- [[current-focus/DEV1-leave|DEV1: Leave]]
