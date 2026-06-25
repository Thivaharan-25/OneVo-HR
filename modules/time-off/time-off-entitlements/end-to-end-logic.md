# Time Off Entitlements - End-to-End Logic

**Module:** Time Off
**Feature:** Time Off Entitlements

---

## 1. Get Employee Entitlements

### Flow

```
GET /api/v1/time-off/entitlements/{employeeId}?year=2026
  -> TimeOffEntitlementController.GetEntitlements(employeeId, year)
    -> [RequirePermission("time_off:read")]
    -> ITimeOffService.GetEntitlementAsync(employeeId, timeOffTypeId, year, ct)
      -> TimeOffEntitlementService.GetEntitlementAsync()
        -> 1. _employeeService.GetByIdAsync(employeeId)
        -> 2. _entitlementRepo.GetByEmployeeAndYearAsync(employeeId, year)
        -> 3. If no entitlement exists -> calculate and persist (see section 2)
        -> 4. Map to TimeOffEntitlementDto with minute balances
      -> Return Result<TimeOffEntitlementDto>
    -> HTTP 200 OK with entitlement data
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Employee not found | 404 | `EMPLOYEE_NOT_FOUND` |
| Invalid year or period | 400 | `INVALID_PERIOD` |
| Tenant mismatch | 403 | `FORBIDDEN` |

---

## 2. Calculate Entitlement Minutes

Balances are stored in minutes (integer). Policy entitlement is entered in hours/minutes and stored canonically in minutes.

### Flow

```
Triggered by: First entitlement query for employee+period OR scheduled accrual/rollover job

TimeOffEntitlementService.CalculateEntitlementAsync(employeeId, timeOffTypeId, period, ct)
  -> 1. _employeeService.GetByIdAsync(employeeId)
       -> retrieve hire_date, active employment period, Company, department, position
  -> 2. _policyResolver.GetActivePolicyAsync(employeeId, timeOffTypeId, period)
       -> resolve by assignment scope and effective date
       -> most specific valid assignment wins inside the employee's Company: employee override, position, department, legal_entity_default
  -> 3. Resolve entitlement base:
       -> base_minutes = policy.entitlement_minutes
  -> 4. Apply proration/accrual model in minutes:
       -> yearly: prorate annual minutes if employee joined/left during the period
       -> monthly: calculate monthly minutes from the annualized minute amount
       -> custom period: prorate by the configured period boundaries
  -> 5. Apply carry-forward if allowed:
       -> previous = _entitlementRepo.GetPreviousPeriodAsync(employeeId, timeOffTypeId, period)
       -> carried_forward_minutes = MIN(previous.available_minutes, policy.carry_forward_limit_minutes)
       -> Use policy.rollover_period to determine monthly, yearly, or policy-period rollover boundary
       -> If carry_forward_expiry is exceeded -> carried_forward_minutes = 0
  -> 6. entitlement_minutes = prorated_entitlement_minutes + carried_forward_minutes
  -> 7. INSERT or UPDATE time_off_entitlements with entitlement_minutes, used_minutes, pending_minutes, carried_forward_minutes, available_minutes
  -> 8. _auditService.LogAsync(employee, timeOffType, 'accrual', accrued_minutes, reason)
  -> 9. Return Result<TimeOffEntitlementDto>
```

### Entitlement Examples

| Scenario | Policy Input | Stored Entitlement |
|:---------|:-------------|:-------------------|
| 160 hours annual | 9600 minutes | 9600 minutes |
| 120h 30m annual | 7230 minutes | 7230 minutes |
| Mid-year joiner, 9600 min annual, joined Jul 1 | 9600 × 6/12 | 4800 minutes |

Schedule changes only affect future entitlement calculations by default. Already-approved Time Off deductions are not recalculated unless an authorized user runs an explicit audited recalculation.

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| No matching policy for employee scope | 422 | `NO_APPLICABLE_POLICY` |
| Employee has no hire date when proration requires it | 422 | `EMPLOYEE_MISSING_HIRE_DATE` |

---

## 3. Period Rollover Job

Carry-forward is policy-driven. It is not always yearly; the rollover boundary follows the policy period.

### Flow

```
TimeOffEntitlementRolloverJob
  -> 1. Get active employees and time off types for policies whose period is closing
  -> 2. For each employee + time_off_type:
       -> a. Get closing entitlement period
       -> b. Resolve active policy for the next period
       -> c. carried_forward_minutes = 0 unless policy.carry_forward_allowed = true
       -> d. If allowed:
            carried_forward_minutes = MIN(available_minutes, policy.carry_forward_limit_minutes)
            apply carry_forward_expiry
       -> e. forfeited_minutes = available_minutes - carried_forward_minutes
       -> f. Log forfeiture if forfeited_minutes > 0
       -> g. Calculate next-period entitlement minutes
       -> h. Create next-period time_off_entitlements row
       -> i. Log carry_forward and accrual audit entries
  -> 3. Log summary: processed count, skipped count, failures
```

### Error Scenarios

| Scenario | Result | Recovery |
|:---------|:-------|:---------|
| Employee has no policy match | Skipped, logged as warning | Admin notified |
| DB failure mid-batch | Transaction per employee | Retry via job runner |
| Duplicate run | Check if entitlement for target period exists | Skip if already created |

---

## 4. Monthly Accrual

### Flow

```
MonthlyAccrualJob
  -> 1. Query time_off_policies WHERE accrual_method = 'monthly'
  -> 2. For each matching employee:
       -> annual_entitlement_minutes = policy.entitlement_minutes
       -> monthly_minutes = annual_entitlement_minutes / 12
       -> _entitlementRepo.IncrementEntitlementMinutes(employeeId, timeOffTypeId, period, monthly_minutes)
       -> _auditService.LogAsync(employee, timeOffType, 'accrual', monthly_minutes, "Monthly accrual {month}/{year}")
```

## Related

- [[modules/time-off/time-off-entitlements/overview|Time Off Entitlements Overview]]
- [[modules/time-off/balance-audit/overview|Balance Audit]]
- [[modules/time-off/time-off-policies/overview|Time Off Policies]]
- [[modules/time-off/time-off-requests/overview|Time Off Requests]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
