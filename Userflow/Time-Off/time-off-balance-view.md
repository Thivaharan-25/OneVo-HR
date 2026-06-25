# Time Off Balance View

**Area:** Time Off Self-Service
**Trigger:** User opens the integrated time_off self-service screen
**Related Permissions:** `time_off:create`, `time_off:read-own`

---

## Purpose

The time off balance view is part of the integrated self-service Time Off screen. It is not a separate disconnected balance-only page.

The screen combines:

- Time off balances / entitlement summary
- Apply Time Off action
- Current and recent time off requests
- Time off request status
- Time off history
- Upcoming approved time_off
- Company holidays
- Policy reminders

Managers use this same screen for their own time_off. Management permissions do not remove self-service access.

## Visibility Boundary

- **Own time_off:** every active employee with self-service time_off access can see their own balances and requests.
- **Managed time_off visibility:** users with people-management access can view Time Off data for employees inside their allowed scope. This is separate from their own self-service screen.

## Preconditions

- User has an active employee record.
- Time off entitlements have been assigned or can be calculated for the selected period.

## Flow Steps

### Step 1: Open Self-Service Time Off
- **API:** `GET /api/v1/time-off/entitlements/me?year={year}`
- **Backend:** `TimeOffEntitlementService.GetBalanceSummaryAsync()` -> [[modules/time-off/overview|Time Off]]
- **DB:** `time_off_entitlements`, `time_off_requests`

### Step 2: View Entitlement Summary
- **UI:** Summary cards or compact table show:
  - Time Off type
  - Entitlement (displayed as hours and minutes, e.g., "160h 0m")
  - Carried-forward (hours/minutes)
  - Used (hours/minutes)
  - Pending (hours/minutes)
  - Available (hours/minutes)
  - Optional approximate day helper for readability (never used for calculation)
  - Expiring carry-forward warning where applicable

### Step 3: View Requests and History
- **UI:** Same screen shows current/recent requests, request status, upcoming approved time_off, and time_off history.
- **API:** `GET /api/v1/time-off/requests/me?year={year}`
- **DB:** `time_off_requests`

### Step 4: Apply Time Off
- **UI:** "Apply Time Off" starts [[Userflow/Time-Off/time-off-request-submission|Time Off Request Submission]] from the same screen.

### Step 5: Managed Visibility
- **UI:** If the user has scoped management visibility, they can switch to a managed employee/team time_off view or open employee Time Off data from the people-management context.
- **Validation:** Scope can come from position-based access, role grants, or approved access grants.
- **Rule:** Managed visibility does not replace the user's own self-service Time Off screen.

## Variations

### Negative balance
- Remaining balance shown as negative with a warning.
- Policy and entitlement audit explain how the balance was reached.

### Carry-forward expiring
- Screen shows a reminder with expiry date and minutes affected (displayed as hours/minutes).

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No entitlements assigned | Empty state | "No time off entitlements found for this period" |
| Year out of range | Validation fails | "Balance data is not available for the selected year" |
| Managed view outside scope | Blocked | "You do not have access to this employee's Time Off data" |

## Events Triggered

- No events for normal read-only viewing.
- Export or adjustment actions, if supported, create audit entries in their own flows.

## Related Flows

- [[Userflow/Time-Off/time-off-request-submission|Time Off Request Submission]]
- [[Userflow/Time-Off/time-off-entitlement-assignment|Time Off Entitlement Assignment]]
- [[Userflow/Time-Off/time-off-cancellation|Time Off Cancellation]]

## Module References

- [[modules/time-off/overview|Time Off]]
- [[modules/time-off/time-off-entitlements/overview|Time Off Entitlements]]
- [[modules/time-off/time-off-requests/overview|Time Off Requests]]
