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

- [[payroll/adjustments/overview|Adjustments Overview]]
- [[payroll/payroll-execution/overview|Payroll Execution]]
- [[payroll/audit-trail/overview|Audit Trail]]
- [[error-handling]]
- [[shared-kernel]]
- [[WEEK4-payroll]]
