# Page: Time Off

**Screen ownership:** Time Off self-service plus permission-based management views
**Permission:** `time_off:read-own`, `time_off:create`, `time_off:approve`, `time_off:manage`

## Purpose

The customer-facing Time Off experience has two contexts:

1. **Self-service Time Off screen** for every active employee, including managers requesting their own time off.
2. **Management/configuration views** for authorized users managing time off requests, time off types, time off policies, and entitlements.

Do not split the self-service experience into disconnected old routes.

## Self-Service Layout

The self-service screen combines:

- Entitlement summary / balances
- Apply Time Off action
- Current and recent requests
- Request status
- Time off history
- Upcoming approved time off
- Company holidays
- Policy reminders

## Management Visibility

Users with scoped employee visibility can view time off data for employees inside their allowed area. This is separate from their own self-service Time Off screen.

## Configuration Views

Active management screens:

- **Time Off Types** - defines what time off types exist.
- **Time Off Policies** - defines rules and assignment scope.
- **Entitlements** - employee-level output for a period.

## Calendar Relationship

- Time off affects employee availability.
- Schedules define expected working pattern.
- Calendar shows time off, schedules, company holidays, and events in time context.
- Attendance reflects actual presence against schedule/policy.

## Related

- [[modules/time-off/time-off-requests/overview|Time Off Requests Overview]]
- [[modules/time-off/time-off-types/overview|Time Off Types]]
- [[modules/time-off/time-off-policies/overview|Time Off Policies]]
- [[modules/time-off/time-off-entitlements/overview|Time Off Entitlements]]
