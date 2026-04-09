# Payroll Adjustments — End-to-End Logic

**Module:** Payroll
**Feature:** Payroll Adjustments

---

## Create Adjustment

### Flow

```
POST /api/v1/payroll/adjustments
  -> AdjustmentController.Create(CreateAdjustmentCommand)
    -> [RequirePermission("payroll:write")]
    -> AdjustmentService.CreateAsync(command, ct)
      -> 1. Validate type: bonus, deduction, reimbursement, penalty
      -> 2. Validate payroll_run_id refers to a draft/processing run
      -> 3. INSERT into payroll_adjustments
      -> 4. Recalculate affected payslip net_pay
      -> Return Result.Success(adjustmentDto)
```

### Key Rules

- **Adjustments can only be added to draft/processing runs** — completed runs are immutable.
- **Bonuses and reimbursements increase net_pay**, deductions and penalties decrease it.

## Related

- [[frontend/architecture/overview|Adjustments Overview]]
- [[frontend/architecture/overview|Payroll Execution]]
- [[frontend/architecture/overview|Audit Trail]]
- [[backend/messaging/error-handling|Error Handling]]
- [[backend/shared-kernel|Shared Kernel]]
- Payroll task file (deferred to Phase 2)
