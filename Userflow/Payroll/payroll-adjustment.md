# Payroll Adjustment

**Area:** Payroll  
**Required Permission(s):** `payroll:write`  
**Related Permissions:** `payroll:approve` (approve adjustment)

---

## Preconditions

- Payroll run exists for the period → [[payroll-run-execution]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Create Adjustment
- **UI:** Payroll → Adjustments → "Create Adjustment" → select employee → select pay period
- **API:** `POST /api/v1/payroll/adjustments`

### Step 2: Enter Details
- **UI:** Select type (Bonus, Deduction, Correction, Back Pay, Advance Recovery) → enter amount → enter description/reason → select if taxable
- **Backend:** AdjustmentService.CreateAsync() → [[adjustments]]
- **DB:** `payroll_adjustments`

### Step 3: Submit
- **UI:** Submit → included in next payroll run or processed as standalone payment
- **Validation:** Amount positive for additions, negative for deductions

### Step 4: Payroll Integration
- **Backend:** Adjustment appears as separate line item in next run → audit trail maintained
- **DB:** `payroll_line_items` — linked to adjustment record

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Employee not in payroll | Blocked | "Employee not enrolled in payroll for this entity" |
| Run already approved | Creates supplementary | "Will be included in supplementary run" |

## Events Triggered

- `PayrollAdjustmentCreated` → [[event-catalog]]

## Related Flows

- [[payroll-run-execution]]
- [[compensation-setup]]
- [[expense-approval]]

## Module References

- [[adjustments]]
- [[payroll-execution]]
- [[audit-trail]]
