# Pensions — End-to-End Logic

**Module:** Payroll
**Feature:** Pensions

---

## Create Pension Plan

### Flow

```
POST /api/v1/payroll/pension-plans
  -> PensionController.CreatePlan(CreatePensionPlanCommand)
    -> [RequirePermission("payroll:write")]
    -> PensionService.CreatePlanAsync(command, ct)
      -> 1. Validate: contribution percentages >= 0
      -> 2. INSERT into pension_plans
         -> employee_contribution_pct, employer_contribution_pct
         -> is_mandatory flag
      -> Return Result.Success(planDto)
```

## Enroll Employee in Pension

### Flow

```
POST /api/v1/payroll/pensions/enroll
  -> PensionController.Enroll(EnrollCommand)
    -> [RequirePermission("payroll:write")]
    -> PensionService.EnrollAsync(command, ct)
      -> 1. Validate employee and plan exist
      -> 2. Check not already enrolled in same plan
      -> 3. INSERT into employee_pension_enrollments
      -> Return Result.Success(enrollmentDto)

```

## Related

- [[payroll/pensions/overview|Pensions Overview]]
- [[payroll/payroll-execution/overview|Payroll Execution]]
- [[payroll/tax-configuration/overview|Tax Configuration]]
- [[error-handling]]
- [[shared-kernel]]
- [[WEEK4-payroll]]
