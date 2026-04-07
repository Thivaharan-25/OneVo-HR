# Leave Entitlements — End-to-End Logic

**Module:** Leave  
**Feature:** Leave Entitlements

---

## 1. Get Employee Entitlements

### Flow

```
GET /api/v1/leave/entitlements/{employeeId}?year=2026
  -> LeaveEntitlementController.GetEntitlements(employeeId, year)
    -> [RequirePermission("leave:read")]
    -> ILeaveService.GetEntitlementAsync(employeeId, leaveTypeId, year, ct)
      -> LeaveEntitlementService.GetEntitlementAsync()
        -> 1. _employeeService.GetByIdAsync(employeeId)  // validate employee exists
        -> 2. _entitlementRepo.GetByEmployeeAndYearAsync(employeeId, year)
        -> 3. If no entitlement exists → calculate and persist (see §2)
        -> 4. Map to LeaveEntitlementDto
      -> Return Result<LeaveEntitlementDto>
    -> HTTP 200 OK with entitlement data
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Employee not found | 404 | `EMPLOYEE_NOT_FOUND` |
| Invalid year (future beyond next year) | 400 | `INVALID_YEAR` |
| Tenant mismatch | 403 | `FORBIDDEN` |

---

## 2. Calculate Entitlement (New Year / New Hire)

### Flow

```
Triggered by: First entitlement query for employee+year OR YearEndEntitlementJob

LeaveEntitlementService.CalculateEntitlementAsync(employeeId, leaveTypeId, year, ct)
  -> 1. _employeeService.GetByIdAsync(employeeId)
       -> retrieve hire_date, country_id, job_level_id
  -> 2. _policyRepo.GetActivePolicyAsync(leaveTypeId, countryId, jobLevelId)
       -> SQL: WHERE superseded_by_id IS NULL
              AND leave_type_id = @leaveTypeId
              AND (country_id = @countryId OR country_id IS NULL)
              AND (job_level_id = @jobLevelId OR job_level_id IS NULL)
       -> ORDER BY country_id DESC NULLS LAST, job_level_id DESC NULLS LAST
       -> LIMIT 1  (most specific policy wins)
  -> 3. Calculate proration if hire_date is within the entitlement year:
       -> proration_method = 'calendar_days':
            prorated = annual_entitlement_days * (remaining_calendar_days / 365)
       -> proration_method = 'working_days':
            prorated = annual_entitlement_days * (remaining_working_days / total_working_days)
       -> Round to 1 decimal place (HALF_UP)
  -> 4. Calculate carry-forward from previous year:
       -> _entitlementRepo.GetByEmployeeAndYearAsync(employeeId, year - 1)
       -> carried = MIN(previous.remaining_days, policy.carry_forward_max_days)
       -> If carry_forward_expiry_months exceeded → carried = 0
  -> 5. total_days = prorated_entitlement + carried_forward_days
  -> 6. INSERT into leave_entitlements
  -> 7. _auditService.LogAsync(employee, leaveType, 'accrual', total_days, reason)
  -> 8. Return Result<LeaveEntitlementDto>
```

### Proration Examples

| Scenario | Hire Date | Annual Days | Method | Prorated |
|:---------|:----------|:------------|:-------|:---------|
| Full year employee | 2025-01-15 | 20 | any | 20.0 |
| Mid-year hire (calendar) | 2026-07-01 | 20 | calendar_days | 10.0 |
| Q4 hire (working days) | 2026-10-01 | 20 | working_days | 5.0 (approx) |

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| No matching policy for employee's country/level | 422 | `NO_APPLICABLE_POLICY` |
| Employee has no hire date | 422 | `EMPLOYEE_MISSING_HIRE_DATE` |

---

## 3. Year-End Rollover (Hangfire Job)

### Flow

```
YearEndEntitlementJob (Hangfire, scheduled Jan 1 00:05 UTC)
  -> 1. Get all active employees across tenants
  -> 2. For each employee + leave_type:
       -> a. Get current year entitlement (year = previous year)
       -> b. Get active policy for that employee
       -> c. carry_forward = MIN(remaining_days, policy.carry_forward_max_days)
       -> d. forfeited = remaining_days - carry_forward
       -> e. If forfeited > 0:
            -> _auditService.LogAsync(employee, leaveType, 'forfeiture', -forfeited, "Year-end forfeiture")
       -> f. Calculate new year entitlement (year = current year):
            -> total_days = policy.annual_entitlement_days + carry_forward
            -> INSERT into leave_entitlements for new year
       -> g. _auditService.LogAsync(employee, leaveType, 'carry_forward', carry_forward, "Carried from {prevYear}")
       -> h. _auditService.LogAsync(employee, leaveType, 'accrual', policy.annual_entitlement_days, "Annual entitlement {newYear}")
  -> 3. Log summary: processed count, failures
```

### Error Scenarios

| Scenario | Result | Recovery |
|:---------|:-------|:---------|
| Employee has no policy match | Skipped, logged as warning | Admin notified |
| DB failure mid-batch | Transaction per employee | Retry via Hangfire |
| Duplicate run (idempotency) | Check if entitlement for new year exists | Skip if already created |

---

## 4. Monthly Accrual (for `accrual_method = 'monthly'`)

### Flow

```
MonthlyAccrualJob (Hangfire, 1st of each month 01:00 UTC)
  -> 1. Query leave_policies WHERE accrual_method = 'monthly'
  -> 2. For each matching employee:
       -> monthly_amount = annual_entitlement_days / 12
       -> _entitlementRepo.IncrementTotalDays(employeeId, leaveTypeId, year, monthly_amount)
       -> _auditService.LogAsync(employee, leaveType, 'accrual', monthly_amount, "Monthly accrual {month}/{year}")
```

## Related

- [[leave-entitlements|Leave Entitlements Overview]]
- [[balance-audit]]
- [[leave-policies]]
- [[leave-requests]]
- [[event-catalog]]
- [[error-handling]]
