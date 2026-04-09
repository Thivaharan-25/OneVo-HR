# Balance Audit — End-to-End Logic

**Module:** Leave  
**Feature:** Balance Audit

---

## Overview

The `leave_balances_audit` table is an **append-only** ledger that records every change to an employee's leave balance. No rows are ever updated or deleted. Each entry captures the change type, amount, resulting balance, and reason.

---

## 1. Deduction on Leave Approval

### Flow

```
LeaveRequestService.ApproveAsync(requestId, ct)
  -> ... (approval logic) ...
  -> _entitlementRepo.IncrementUsedDays(employeeId, leaveTypeId, year, totalDays)
  -> _balanceAuditService.LogAsync(...)
    -> BalanceAuditService.LogAsync(employeeId, leaveTypeId, changeType, daysChanged, reason, ct)
      -> 1. currentBalance = _entitlementRepo.GetRemainingDays(employeeId, leaveTypeId, year)
      -> 2. INSERT into leave_balances_audit:
           {
             employee_id,
             leave_type_id,
             change_type: 'deduction',
             days_changed: -totalDays,      // negative
             balance_after: currentBalance,
             reason: "Leave approved: {requestId}",
             created_at: UTC now
           }
      -> 3. No domain event — the LeaveApproved event from the request handles notifications
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Entitlement not found for employee/year | 422 | `ENTITLEMENT_NOT_FOUND` |
| Concurrent modification (stale balance) | 409 | `BALANCE_CONFLICT` — retry with fresh read |

---

## 2. Adjustment on Leave Cancellation

### Flow

```
LeaveRequestService.CancelAsync(requestId, ct)
  -> ... (cancellation logic) ...
  -> _entitlementRepo.DecrementUsedDays(employeeId, leaveTypeId, year, totalDays)
  -> _balanceAuditService.LogAsync(...)
    -> BalanceAuditService.LogAsync(employeeId, leaveTypeId, changeType, daysChanged, reason, ct)
      -> 1. currentBalance = _entitlementRepo.GetRemainingDays(...)
      -> 2. INSERT into leave_balances_audit:
           {
             change_type: 'adjustment',
             days_changed: +totalDays,       // positive — restoring days
             balance_after: currentBalance,
             reason: "Leave cancelled: {requestId}"
           }
```

---

## 3. Accrual Entry

### Flow

```
LeaveEntitlementService.CalculateEntitlementAsync(...)
  OR MonthlyAccrualJob.ExecuteAsync(...)
    -> After creating/updating entitlement
    -> _balanceAuditService.LogAsync(...)
      -> INSERT into leave_balances_audit:
           {
             change_type: 'accrual',
             days_changed: +accruedDays,
             balance_after: totalDays,
             reason: "Annual entitlement 2026" | "Monthly accrual March/2026"
           }
```

---

## 4. Carry-Forward Entry

### Flow

```
YearEndEntitlementJob.ExecuteAsync(...)
  -> After calculating carry-forward amount
  -> _balanceAuditService.LogAsync(...)
    -> INSERT into leave_balances_audit:
         {
           change_type: 'carry_forward',
           days_changed: +carriedDays,
           balance_after: newYearTotal,
           reason: "Carried forward from 2025"
         }
```

---

## 5. Forfeiture Entry

### Flow

```
YearEndEntitlementJob.ExecuteAsync(...)
  -> When remaining_days > carry_forward_max_days
  -> forfeitedDays = remaining_days - carry_forward_max_days
  -> _balanceAuditService.LogAsync(...)
    -> INSERT into leave_balances_audit:
         {
           change_type: 'forfeiture',
           days_changed: -forfeitedDays,     // negative — days lost
           balance_after: 0,                 // year is closing
           reason: "Year-end forfeiture 2025"
         }
```

---

## 6. Query Audit Trail

### Flow

```
GET /api/v1/leave/audit/{employeeId}?leaveTypeId={id}&year=2026
  -> LeaveAuditController.GetAuditTrail(employeeId, leaveTypeId, year)
    -> [RequirePermission("leave:read")]
    -> _balanceAuditRepo.GetByEmployeeAsync(employeeId, leaveTypeId, year, ct)
      -> SQL: SELECT * FROM leave_balances_audit
              WHERE employee_id = @employeeId
              AND leave_type_id = @leaveTypeId
              AND EXTRACT(YEAR FROM created_at) = @year
              ORDER BY created_at ASC
    -> Map to List<BalanceAuditDto>
    -> HTTP 200 OK
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Employee not found | 404 | `EMPLOYEE_NOT_FOUND` |
| No audit entries | 200 | Empty list (not an error) |
| Unauthorized | 403 | `FORBIDDEN` |

---

## Invariants

1. `leave_balances_audit` is **append-only** — no UPDATE, no DELETE.
2. `balance_after` always reflects the balance **after** the change is applied.
3. `days_changed` is **negative** for deductions and forfeitures, **positive** for accruals, adjustments, and carry-forwards.
4. Every balance mutation in `leave_entitlements` must have a corresponding audit row — enforced at the service layer.

## Related

- [[modules/leave/balance-audit/overview|Balance Audit Overview]]
- [[modules/leave/leave-entitlements/overview|Leave Entitlements]]
- [[modules/leave/leave-requests/overview|Leave Requests]]
- [[modules/leave/leave-policies/overview|Leave Policies]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
