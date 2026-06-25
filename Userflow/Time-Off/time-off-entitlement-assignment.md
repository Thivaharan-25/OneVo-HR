# Time Off Entitlement Assignment

**Area:** Time Off
**Trigger:** Policy assignment, employee creation, year rollover, or authorized recalculation
**Required Permission(s):** `time_off:manage`
**Related Permissions:** `employees:read`

---

## Purpose

Time Off Policies define the rules and assignment scope. Entitlements are the employee-level result for a period.

Entitlements are not a separate place to define time off rules. They show or store what each employee receives after policy assignment is applied. The stored balance unit is minutes. The UI displays hours and minutes.

## Preconditions

- Time off types exist.
- Time Off Policies exist in the selected Company and are assigned to Company default (`legal_entity_default`), department, position, or employee-specific override where supported.
- Employees exist with employment assignment data.

## Flow Steps

### Step 1: Open Entitlements
- **UI:** Authorized user opens Time Off management and selects **Entitlements**.
- **Screen shows:** employee, time off type, period/year, entitlement (hours/minutes), carried-forward (hours/minutes), used (hours/minutes), pending (hours/minutes), available (hours/minutes), policy source, and status. UI may also display an approximate day equivalent for readability, but days are never used for calculation.
- **API:** `GET /api/v1/time-off/entitlements?year={year}`
- **Backend:** `TimeOffEntitlementService.GetAllAsync()` -> [[modules/time-off/overview|Time Off]]
- **DB:** `time_off_entitlements`

Avoid old dashboard wording that makes entitlement generation feel like a separate admin product. This is the operational output of policy assignment.

### Step 2: Generate or Recalculate Entitlements
- **UI:** Run generation/recalculation for a period and scope when supported.
- **Scope examples:** all employees in the selected Company, Company default (`legal_entity_default`), department, position, or selected employees depending on permissions and implementation.
- **API:** `POST /api/v1/time-off/entitlements/generate` or `POST /api/v1/time-off/entitlements/recalculate`
- **Backend:** `TimeOffEntitlementService.GenerateBulkAsync()` / `RecalculateAsync()`
  1. Finds active employees in scope.
  2. Resolves applicable policy by assignment priority.
  3. Calculates employee-level entitlement minutes for each time off type.
  4. Policy entitlement is already in minutes (admin enters hours/minutes, system stores minutes).
  5. Applies carry-forward according to policy.
  6. Creates or updates `time_off_entitlements`.

### Step 3: Manual Adjustment
- **UI:** Open employee entitlement row -> adjust allowed fields -> enter reason.
- **API:** `PUT /api/v1/time-off/entitlements/{entitlementId}`
- **Rule:** Manual adjustment is an exception/audit action. It does not redefine the policy.

## Policy and Override Priority

Where supported, the source can resolve in this order:

1. Employee-specific override.
2. Position assignment.
3. Department assignment.
4. Company default assignment stored as `legal_entity_default`.

If the final implementation uses a different priority order, update this section from the implemented access rules.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No applicable policy | Employee skipped or error | "No time off policy applies to this employee" |
| Entitlement already exists | Recalculate path required | "Entitlement already exists for this period" |
| Manual adjustment below used balance | Warning | "Employee will show a negative balance" |
| Missing management permission | `403 Forbidden` | "You do not have permission to manage entitlements" |

## Events Triggered

- `TimeOffEntitlementCreatedEvent`
- `TimeOffEntitlementUpdatedEvent`
- `AuditLogEntry` (action: `time_off_entitlement.generated` or `time_off_entitlement.adjusted`)

## Related Flows

- [[Userflow/Time-Off/time-off-policy-setup|Time Off Policy Setup]]
- [[Userflow/Time-Off/time-off-type-configuration|Time Off Type Configuration]]
- [[Userflow/Time-Off/time-off-request-submission|Time Off Request Submission]]
- [[Userflow/Time-Off/time-off-balance-view|Time Off Balance View]]

## Module References

- [[modules/time-off/overview|Time Off]]
- [[modules/time-off/time-off-entitlements/overview|Time Off Entitlements]]
- [[modules/time-off/time-off-policies/overview|Time Off Policies]]
