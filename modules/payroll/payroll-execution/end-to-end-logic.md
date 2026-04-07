# Payroll Execution — End-to-End Logic

**Module:** Payroll
**Feature:** Payroll Execution

---

## Execute Payroll Run

### Flow

```
POST /api/v1/payroll/runs
  -> PayrollController.Execute(ExecutePayrollCommand)
    -> [RequirePermission("payroll:run")]
    -> PayrollService.ExecutePayrollRunAsync(command, ct)
      -> 1. Acquire distributed lock (Hangfire) for tenant
         -> Prevent concurrent payroll runs
      -> 2. INSERT payroll_runs (status = 'processing')
      -> 3. Get active employees for legal_entity in period
      -> 4. For each employee:
         -> a. Get base_salary from employee_salary_history (latest effective)
         -> b. Get worked_hours from IWorkforcePresenceService.GetTotalWorkedHoursAsync()
         -> c. Get leave_days from ILeaveService.GetUsedDaysAsync() for period
         -> d. Get allowances from employee_allowances (active for period)
         -> e. Get pension enrollment from employee_pension_enrollments
         -> f. Calculate:
            -> total_allowances (sum of active allowances)
            -> pension_employee = base_salary * employee_contribution_pct
            -> pension_employer = base_salary * employer_contribution_pct
            -> taxable_income = base_salary + taxable_allowances - pension_employee
            -> tax_amount = apply progressive brackets from tax_configurations
            -> total_deductions = tax + pension_employee + leave deductions
            -> net_pay = base_salary + total_allowances - total_deductions
         -> g. INSERT into payslips
      -> 5. Sum totals -> UPDATE payroll_runs (total_gross, total_net, total_tax, status = 'completed')
      -> 6. INSERT into payroll_audit_trail
      -> 7. Release distributed lock
      -> Return Result.Success(payrollRunDto)
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Concurrent run for same tenant | Return 409 "Payroll run already in progress" |
| Employee missing salary data | Skip employee, log warning, include in error report |
| Tax config not found for country | Use 0% tax, flag in audit trail |
| Presence data unavailable | Use scheduled hours as fallback |

## Related

- [[payroll/payroll-execution/overview|Payroll Execution Overview]]
- [[payroll/adjustments/overview|Adjustments]]
- [[payroll/allowances/overview|Allowances]]
- [[payroll/audit-trail/overview|Audit Trail]]
- [[payroll/tax-configuration/overview|Tax Configuration]]
- [[payroll/pensions/overview|Pensions]]
- [[error-handling]]
- [[event-catalog]]
- [[shared-kernel]]
- [[WEEK4-payroll]]
