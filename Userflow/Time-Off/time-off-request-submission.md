# Time Off Request Submission

**Area:** Time Off Self-Service
**Trigger:** User applies for time off for themselves (user action)
**Required Permission(s):** `time_off:create`
**Related Permissions:** `time_off:read-own`, `calendar:read`

---

## Purpose

The self-service Time Off screen is one integrated operational page for a user's own time off. It combines:

- Time off balances / entitlement summary
- Apply Time Off action
- Current and recent time off requests
- Time off request status
- Time off history
- Upcoming approved time off
- Company holidays
- Policy reminders

Managers use the same self-service Time Off screen for their own time off. Management authority does not replace or remove personal Time Off access.

## Visibility Boundary

- **Self-service Time Off access** is a personal employee function.
- **Managed Time Off visibility** is a permission-based management function for employees inside the user's allowed visibility area.

Do not mix "my own Time Off" with "time off I can manage for others".

## Preconditions

- User has an active employee record.
- Time off entitlements exist for the period: [[Userflow/Time-Off/time-off-entitlement-assignment|Time Off Entitlement Assignment]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Open Self-Service Time Off
- **UI:** User opens the Time Off self-service screen and sees balances, recent/current requests, upcoming approved time off, holidays, and policy reminders.
- **API:** `GET /api/v1/time-off/entitlements/me?year={year}`, `GET /api/v1/time-off/requests/me?year={year}`
- **Backend:** `TimeOffEntitlementService.GetByEmployeeAsync()`, `TimeOffRequestService.GetByEmployeeAsync()` -> [[modules/time-off/overview|Time Off]]
- **DB:** `time_off_entitlements`, `time_off_requests`

Do not describe this as disconnected old screens. The self-service Time Off page is one cohesive operational screen.

### Step 2: Apply Time Off
- **UI:** Click "Apply Time Off" from the self-service screen or select a date from the calendar context.
- **Fields:**
  - Time Off type
  - Start date and end date
  - Start time and end time (optional; for specifying exact hours)
  - Requested duration in hours/minutes
  - Reason, if required by policy
  - Supporting document, if required by policy
- **API:** Preview uses `POST /api/v1/time-off/calculate` if available.

### Step 3: System Converts and Validates
- **Backend:** `TimeOffCalculationService.CalculateDurationMinutesAsync()` -> [[modules/time-off/overview|Time Off]]
- **Rules:**
  - System converts the requested duration to `request_duration_minutes`.
  - Calendar supplies holidays and conflict warnings.
  - Time Off policy supplies entitlement, notice, document, carry-forward, and limit rules.
  - Shift schedules are used for attendance expectations, calendar display, and availability context — they do not calculate Time Off request duration in Phase 1.
  - Full-day and half-day are not canonical request modes in Phase 1. If UI shortcuts are added later, they must convert to explicit minutes before saving.
- **Validation:** Conflicts are warnings; minute balance and policy validation can block where policy requires.

### Step 4: Submit Request
- **API:** `POST /api/v1/time-off/requests`
- **Backend:** `TimeOffRequestService.CreateAsync()`
  1. Creates `time_off_requests` with status `pending`.
  2. Stores `request_duration_minutes`, `deduction_minutes` when approved, and conflict snapshot when applicable.
  3. Stores supporting documents if provided.
  4. Resolves one Phase 1 owner through management coverage.
  5. Sends notification to the assigned owner, or creates a routing issue if no eligible owner exists.
- **DB:** `time_off_requests`, `time_off_request_documents`, `notifications`, `audit_logs`

## Variations

### Insufficient balance
- System warns when requested minutes exceed available balance (displayed as hours/minutes).
- Submission is blocked only when the policy does not allow unpaid/over-balance behavior.

### Manager requesting own time off
- Manager follows the same self-service flow.
- Having `time_off:approve` or `time_off:manage` does not block self-service Time Off.
- Manager cannot approve their own request unless a policy explicitly allows self-approval.

### Requesting on behalf of another employee
- This is a managed Time Off action, not self-service time_off.
- User must have management authority and employee visibility for the target employee.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Insufficient time off balance | Blocked only when policy requires | "Insufficient balance for this time off type" |
| Overlapping existing request | `409 Conflict` | "You already have a pending/approved time off request overlapping these dates" |
| Past date without backdating permission | Validation fails | "Time off start date cannot be in the past" |
| Supporting document required but missing | Validation fails | "A supporting document is required by policy" |
| Approver not found | Submission blocked | "No approver found. Please contact HR" |

## Events Triggered

- `TimeOffRequestCreatedEvent` -> notification and calendar consumers
- `AuditLogEntry` (action: `time_off_request.created`)

## Related Flows

- [[Userflow/Time-Off/time-off-approval|Time Off Approval]]
- [[Userflow/Time-Off/time-off-cancellation|Time Off Cancellation]]
- [[Userflow/Time-Off/time-off-balance-view|Time Off Balance View]]
- [[Userflow/Time-Off/time-off-entitlement-assignment|Time Off Entitlement Assignment]]

## Module References

- [[modules/time-off/overview|Time Off]]
- [[modules/time-off/time-off-requests/overview|Time Off Requests]]
- [[modules/time-off/time-off-entitlements/overview|Time Off Entitlements]]
- [[modules/calendar/overview|Calendar]]
