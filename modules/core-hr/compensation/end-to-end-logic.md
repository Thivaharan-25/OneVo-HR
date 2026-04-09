# Compensation — End-to-End Logic

**Module:** Core HR
**Feature:** Compensation (Salary History)

---

## Update Salary

### Flow

```
POST /api/v1/employees/{id}/salary
  -> CompensationController.UpdateSalary(id, UpdateSalaryCommand)
    -> [RequirePermission("payroll:read")]
    -> CompensationService.UpdateSalaryAsync(employeeId, command, ct)
      -> 1. Load employee
      -> 2. INSERT into employee_salary_history
         -> effective_date, base_salary, currency_code, change_reason
         -> approved_by_id = current user
      -> 3. Create lifecycle event: event_type = 'salary_change'
         -> details_json includes old salary, new salary, reason
      -> 4. Publish EmployeePromoted event (if change_reason = 'promotion')
      -> Return Result.Success(salaryHistoryDto)
```

## Get Salary History

### Flow

```
GET /api/v1/employees/{id}/salary-history
  -> CompensationController.GetHistory(id)
    -> [RequirePermission("payroll:read")]
    -> CompensationService.GetHistoryAsync(employeeId, ct)
      -> Query employee_salary_history ORDER BY effective_date DESC
      -> Return Result.Success(historyDtos)
```

### Key Rules

- **Bank details are encrypted** via `IEncryptionService` (AES-256). The `account_number_encrypted` column stores bytea.
- **Salary changes always create a lifecycle event** for audit purposes.

## Related

- [[modules/core-hr/compensation/overview|Compensation Overview]]
- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- [[modules/core-hr/offboarding/overview|Offboarding]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
