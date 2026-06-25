# Time Off Cancellation

**Area:** Time Off Self-Service / Time Off
**Trigger:** User cancels their own time off request, or authorized user cancels on behalf of an employee
**Required Permission(s):** `time_off:create` for own request, `time_off:manage` for managed cancellation
**Related Permissions:** `time_off:read-own`, scoped `time_off:read`

---

## Purpose

Cancellation starts from the integrated self-service Time Off screen for a user's own requests. Managers use the same self-service screen for their own time off. Managed cancellation for another employee is a separate permission-based management action.

## Preconditions

- A time off request exists with status `pending` or `approved`.
- Own cancellation: requester owns the request and has `time_off:create`.
- Managed cancellation: user has `time_off:manage` and visibility over the employee.

## Flow Steps

### Step 1: Open Time Off Request
- **Self-service UI:** User opens their Time Off self-service screen and selects a current, recent, or upcoming request.
- **Managed UI:** Authorized user opens managed time off data for an employee inside their visibility scope.
- **API:** `GET /api/v1/time-off/requests/me` or scoped `GET /api/v1/time-off/requests?employeeId={id}`
- **DB:** `time_off_requests`

Avoid obsolete wording that implies old disconnected Time Off screens.

### Step 2: Cancel Request
- **UI:** Click "Cancel Request" from the request row/detail.
- **Validation:** Available only for cancellable pending/approved requests according to policy and date rules.

### Step 3: Confirm Cancellation
- **UI:** Confirmation shows time off type, date range/time range, deducted hours, and balance effect. Managed cancellations require a reason.

### Step 4: Process Cancellation
- **API:** `POST /api/v1/time-off/requests/{requestId}/cancel`
- **Backend:** `TimeOffRequestService.CancelAsync()`
  1. Updates request status to `cancelled`.
  2. Stores cancellation reason and actor.
  3. Restores balance when an approved future time off is cancelled.
  4. Removes or updates the related calendar event.
  5. Sends notifications.
  6. Creates audit log entry.
- **DB:** `time_off_requests`, `time_off_entitlements`, `calendar_events`, `notifications`, `audit_logs`

## Variations

### Partially taken time off
- Already-taken hours remain deducted.
- Future approved hours can be cancelled and restored according to policy.

### Managed cancellation
- User must have employee visibility/people-management access for the employee.
- Reason is mandatory.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Request already cancelled | `409 Conflict` | "This time off request has already been cancelled" |
| Request already rejected | `422 Unprocessable` | "Rejected requests cannot be cancelled" |
| Time off period fully elapsed | `422 Unprocessable` | "This time off period has already passed and cannot be cancelled" |
| Managed cancellation without reason | Validation fails | "A reason is required" |

## Events Triggered

- `TimeOffRequestCancelledEvent`
- `TimeOffBalanceRestoredEvent` when balance changes
- `AuditLogEntry` (action: `time_off_request.cancelled`)

## Related Flows

- [[Userflow/Time-Off/time-off-request-submission|Time Off Request Submission]]
- [[Userflow/Time-Off/time-off-approval|Time Off Approval]]
- [[Userflow/Time-Off/time-off-balance-view|Time Off Balance View]]

## Module References

- [[modules/time-off/overview|Time Off]]
- [[modules/time-off/time-off-requests/overview|Time Off Requests]]
- [[modules/time-off/time-off-entitlements/overview|Time Off Entitlements]]
- [[modules/calendar/calendar-events/overview|Calendar Events]]
