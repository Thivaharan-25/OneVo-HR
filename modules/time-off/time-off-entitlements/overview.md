# Time Off Entitlements

**Module:** Time Off
**Feature:** Time Off Entitlements

---

## Purpose

Employee-level entitlement result for a period, calculated from Time Off Policy assignment and employee context.

Time Off Policies define the rules. Entitlements store or expose the employee-level output in minutes: entitlement, carried forward, used, pending, and available minutes.

## Database Tables

### `time_off_entitlements`

Key columns: `employee_id`, `time_off_type_id`, `period_year` or period, `policy_id`/source where implemented, `entitlement_minutes`, `used_minutes`, `pending_minutes`, `carried_forward_minutes`, and `available_minutes`.

## Key Business Rules

- Entitlements are generated/recalculated from policy assignment.
- Policy entitlement is entered in hours/minutes and stored canonically in minutes. No day-based entitlement input.
- If schedule changes mid-period, future accrual/generation uses the new effective schedule from that date.
- Past approved deductions are not recalculated automatically.
- Manual adjustment is an audited exception; it does not redefine the policy.
- Employee-specific override can affect the entitlement source where supported.
- Late arrival deductions from Time & Attendance also update `used_minutes`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/time-off/entitlements/{employeeId}` | `time_off:read` | Get entitlements |
| GET | `/api/v1/time-off/entitlements/me` | `time_off:read-own` | Get own entitlements |

## Related

- [[modules/time-off/overview|Time Off Module]]
- [[modules/time-off/time-off-policies/overview|Time Off Policies]]
- [[modules/time-off/time-off-requests/overview|Time Off Requests]]
