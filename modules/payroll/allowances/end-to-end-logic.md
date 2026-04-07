# Allowances — End-to-End Logic

**Module:** Payroll
**Feature:** Allowances

---

## Create Allowance Type

### Flow

```
POST /api/v1/payroll/allowance-types
  -> AllowanceController.CreateType(CreateAllowanceTypeCommand)
    -> [RequirePermission("payroll:write")]
    -> AllowanceService.CreateTypeAsync(command, ct)
      -> 1. Validate: name unique, calculation_method valid (fixed/percentage)
      -> 2. INSERT into allowance_types
         -> is_taxable flag determines if included in tax computation
      -> Return Result.Success(typeDto)
```

## Assign Allowance to Employee

### Flow

```
POST /api/v1/payroll/allowances
  -> AllowanceController.Assign(AssignAllowanceCommand)
    -> [RequirePermission("payroll:write")]
    -> AllowanceService.AssignAsync(command, ct)
      -> 1. Validate employee and allowance_type exist
      -> 2. INSERT into employee_allowances
         -> effective_from, effective_to, amount
      -> Return Result.Success(allowanceDto)

```

## Related

- [[payroll/allowances/overview|Allowances Overview]]
- [[payroll/payroll-execution/overview|Payroll Execution]]
- [[payroll/tax-configuration/overview|Tax Configuration]]
- [[error-handling]]
- [[shared-kernel]]
- [[WEEK4-payroll]]
