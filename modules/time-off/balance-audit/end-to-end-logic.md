# Balance Audit - End-to-End Logic

**Module:** Time Off
**Feature:** Balance Audit

---

## Overview

The `time_off_balances_audit` table is an append-only ledger that records every change to an employee's Time Off balance. No rows are updated or deleted. Each entry captures the change type, minute amount, resulting minute balance, source, and reason.

---

## 1. Deduction on Time Off Approval

### Flow

```
TimeOffRequestService.ApproveAsync(requestId, ct)
  -> ... (approval logic) ...
  -> _entitlementRepo.IncrementUsedMinutes(employeeId, timeOffTypeId, period, deductionMinutes)
  -> _balanceAuditService.LogAsync(...)
    -> BalanceAuditService.LogAsync(employeeId, timeOffTypeId, changeType, minutesChanged, reason, ct)
      -> 1. currentBalanceMinutes = _entitlementRepo.GetAvailableMinutes(employeeId, timeOffTypeId, period)
      -> 2. INSERT into time_off_balances_audit:
           {
             employee_id,
             time_off_type_id,
             change_type: 'deduction',
             minutes_changed: -deductionMinutes,
             balance_after_minutes: currentBalanceMinutes,
             source: 'time_off',
             reason: "Time off approved: {requestId}",
             created_at: UTC now
           }
      -> 3. No separate notification event; TimeOffApproved handles notifications
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Entitlement not found for employee/period | 422 | `ENTITLEMENT_NOT_FOUND` |
| Concurrent modification | 409 | `BALANCE_CONFLICT` |

---

## 2. Adjustment on Time Off Cancellation

### Flow

```
TimeOffRequestService.CancelAsync(requestId, ct)
  -> ... (cancellation logic) ...
  -> _entitlementRepo.DecrementUsedMinutes(employeeId, timeOffTypeId, period, deductionMinutes)
  -> _balanceAuditService.LogAsync(...)
    -> BalanceAuditService.LogAsync(employeeId, timeOffTypeId, 'adjustment', +deductionMinutes, reason, ct)
      -> 1. currentBalanceMinutes = _entitlementRepo.GetAvailableMinutes(...)
      -> 2. INSERT into time_off_balances_audit:
           {
             change_type: 'adjustment',
             minutes_changed: +deductionMinutes,
             balance_after_minutes: currentBalanceMinutes,
             source: 'time_off',
             reason: "Time off cancelled: {requestId}"
           }
```

---

## 3. Accrual Entry

### Flow

```
TimeOffEntitlementService.CalculateEntitlementAsync(...)
  OR MonthlyAccrualJob.ExecuteAsync(...)
    -> After creating/updating entitlement
    -> _balanceAuditService.LogAsync(...)
      -> INSERT into time_off_balances_audit:
           {
             change_type: 'accrual',
             minutes_changed: +accruedMinutes,
             balance_after_minutes: totalMinutes,
             source: 'system',
             reason: "Entitlement 2026" | "Monthly accrual March/2026"
           }
```

---

## 4. Carry-Forward Entry

### Flow

```
TimeOffEntitlementRolloverJob.ExecuteAsync(...)
  -> After calculating carried_forward_minutes
  -> _balanceAuditService.LogAsync(...)
    -> INSERT into time_off_balances_audit:
         {
           change_type: 'carry_forward',
           minutes_changed: +carriedForwardMinutes,
           balance_after_minutes: newPeriodTotalMinutes,
           source: 'system',
           reason: "Carried forward from previous period"
         }
```

---

## 5. Forfeiture Entry

### Flow

```
TimeOffEntitlementRolloverJob.ExecuteAsync(...)
  -> When available_minutes exceeds the allowed carry-forward amount
  -> forfeitedMinutes = available_minutes - carried_forward_minutes
  -> _balanceAuditService.LogAsync(...)
    -> INSERT into time_off_balances_audit:
         {
           change_type: 'forfeiture',
           minutes_changed: -forfeitedMinutes,
           balance_after_minutes: closingBalanceMinutes,
           source: 'system',
           reason: "Carry-forward forfeiture"
         }
```

---

## 6. Late Arrival Deduction Entry

### Flow

```
ITimeOffService.DeductLateArrivalAsync(employeeId, timeOffTypeId, deductionMinutes, attendanceRecordId, calculationSnapshotJson, ct)
  -> _entitlementRepo.IncrementUsedMinutes(employeeId, timeOffTypeId, period, deductionMinutes)
  -> _balanceAuditService.LogAsync(...)
    -> 1. currentBalanceMinutes = _entitlementRepo.GetAvailableMinutes(...)
    -> 2. INSERT into time_off_balances_audit:
         {
           employee_id,
           time_off_type_id,
           attendance_record_id: attendanceRecordId,
           change_type: 'late_deduction',
           minutes_changed: -deductionMinutes,
           balance_after_minutes: currentBalanceMinutes,
           source: 'time_attendance',
           calculation_snapshot_json: calculationSnapshotJson,
           reason: "Late arrival deduction",
           created_by_id: null (system),
           created_at: UTC now
         }
```

If the Time Off type does not have sufficient balance, the deduction is not applied. An attendance exception is recorded and surfaced to the responsible manager/HR coverage owner.

---

## 7. Query Audit Trail

### Flow

```
GET /api/v1/time-off/audit/{employeeId}?timeOffTypeId={id}&period=2026
  -> TimeOffAuditController.GetAuditTrail(employeeId, timeOffTypeId, period)
    -> [RequirePermission("time_off:read")]
    -> _balanceAuditRepo.GetByEmployeeAsync(employeeId, timeOffTypeId, period, ct)
      -> SELECT * FROM time_off_balances_audit
         WHERE employee_id = @employeeId
         AND time_off_type_id = @timeOffTypeId
         AND period matches @period
         ORDER BY created_at ASC
    -> Map to List<BalanceAuditDto>
    -> HTTP 200 OK
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Employee not found | 404 | `EMPLOYEE_NOT_FOUND` |
| No audit entries | 200 | Empty list |
| Unauthorized | 403 | `FORBIDDEN` |

---

## Invariants

1. `time_off_balances_audit` is append-only.
2. `balance_after_minutes` always reflects the remaining minute balance after the change is applied.
3. `minutes_changed` is negative for deductions, late deductions, and forfeitures; positive for accruals, adjustments, and carry-forwards.
4. Every `time_off_entitlements` balance mutation must have a corresponding audit row.
5. Day equivalents are display-only and must be derived from policy/schedule context.
6. Late deduction entries must include `attendance_record_id`, `source: 'time_attendance'`, and `calculation_snapshot_json`.

## Related

- [[modules/time-off/balance-audit/overview|Balance Audit Overview]]
- [[modules/time-off/time-off-entitlements/overview|Time Off Entitlements]]
- [[modules/time-off/time-off-requests/overview|Time Off Requests]]
- [[modules/time-off/time-off-policies/overview|Time Off Policies]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
