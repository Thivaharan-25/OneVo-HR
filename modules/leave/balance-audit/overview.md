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

- [[leave|Leave Module]]
- [[leave-requests]]
- [[leave-entitlements]]
- [[leave-policies]]
- [[leave-types]]
- [[event-catalog]]
- [[error-handling]]
- [[data-classification]]
- [[retention-policies]]
- [[WEEK3-leave]]
