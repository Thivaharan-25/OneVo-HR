# Leave Request Submission

**Area:** Leave Management  
**Required Permission(s):** `leave:create`  
**Related Permissions:** `leave:read-own` (to view own balance), `calendar:read` (to check calendar conflicts)

---

## Preconditions

- Employee has an active employment record
- Leave entitlements have been assigned for the current year: [[Userflow/Leave/leave-entitlement-assignment|Leave Entitlement Assignment Flow]]
- Employee has sufficient balance for the requested leave type
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Leave Request
- **UI:** Employee navigates to Leave → My Leave → clicks "New Request" button. Alternatively, clicks on a date in the calendar widget to pre-fill dates
- **API:** `GET /api/v1/leave/entitlements/me?year={year}`
- **Backend:** `LeaveEntitlementService.GetByEmployeeAsync()` → [[modules/leave/overview|Leave]]
- **Validation:** Checks `leave:create` permission via RBAC middleware
- **DB:** `leave_entitlements` (filtered by `employee_id`, `year`)

### Step 2: Select Leave Type
- **UI:** Dropdown showing available leave types with current balance beside each (e.g., "Annual Leave — 15 days remaining", "Sick Leave — 8 days remaining"). Leave types with 0 balance shown greyed out (still selectable for unpaid). Gender-restricted types hidden if not applicable
- **API:** `GET /api/v1/leave/types?active=true`
- **Backend:** `LeaveTypeService.GetAvailableForEmployeeAsync()` → [[modules/leave/overview|Leave]]
- **Validation:** Filters leave types by employee gender for gender-specific types (maternity/paternity)
- **DB:** `leave_types`, `leave_entitlements`, `employees`

### Step 3: Select Dates
- **UI:** Calendar date picker: Start Date, End Date. Toggle for "Half Day" (AM/PM selector appears). Calendar visually shows: weekends (greyed), public holidays (marked), existing leave (coloured blocks), team members on leave (count badge per date)
- **API:** `GET /api/v1/calendar/holidays?year={year}` and `GET /api/v1/leave/team-calendar?from={start}&to={end}`
- **Backend:** `CalendarService.GetHolidaysAsync()`, `LeaveService.GetTeamCalendarAsync()` → [[modules/calendar/overview|Calendar]], [[modules/leave/overview|Leave]]
- **Validation:** Start date must be today or future (unless backdating allowed by policy). End date must be ≥ start date
- **DB:** `calendar_events`, `leave_requests`

### Step 4: System Calculates Total Days
- **UI:** Real-time calculation displayed: "Total leave days: N" with breakdown showing excluded weekends and public holidays. Warning badges shown if applicable:
  - "3 team members already on leave during this period"
  - "Exceeds maximum consecutive days (policy limit: X)"
  - "Falls within a blackout period"
- **API:** `POST /api/v1/leave/calculate` (preview endpoint, no state change)
- **Backend:** `LeaveCalculationService.CalculateDaysAsync()` → [[modules/leave/overview|Leave]]
  1. Counts business days between start and end date
  2. Excludes weekends (based on employee's work schedule)
  3. Excludes public holidays for employee's country/location
  4. Applies half-day adjustment if selected
  5. Checks team absence threshold from policy
  6. Checks consecutive day limits
  7. Checks blackout periods
- **Validation:** Total days must be > 0. Balance check: remaining ≥ requested (warning if insufficient, blocks if leave type is not unpaid-eligible)
- **DB:** `calendar_events`, `leave_entitlements`, `leave_requests` (team overlap check), `shifts_schedules` (work pattern)

### Step 5: Enter Reason and Attachments
- **UI:** Text area: "Reason for Leave" (required for some types per policy, optional for others). File upload for supporting documents (e.g., medical certificate). Document requirement warning if policy mandates attachment after N days
- **API:** N/A (client-side form entry)
- **Backend:** N/A
- **Validation:** If leave type requires document after N days and request exceeds N days, attachment becomes mandatory
- **DB:** None

### Step 6: Submit Request
- **UI:** Review summary shown: Leave Type, Dates, Total Days, Balance Impact (current → after approval). Click "Submit Request". Success toast: "Leave request submitted. Pending approval from [Manager Name]"
- **API:** `POST /api/v1/leave/requests`
- **Backend:** `LeaveRequestService.CreateAsync()` → [[modules/leave/overview|Leave]]
  1. Creates `leave_requests` record with status `pending`
  2. Calculates and stores `total_days`, start/end dates, leave type
  3. Uploads supporting documents to storage via [[modules/documents/overview|Documents]]
  4. Determines approver(s) from employee's reporting line
  5. Creates workflow instance via [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
  6. Sends notification to approver(s) via [[backend/notification-system|Notification System]]
  7. Publishes `LeaveRequestCreatedEvent`
  8. Creates audit log entry
- **Validation:** Final server-side validation: balance sufficiency, date conflicts, policy rules (notice period, consecutive days, blackout), no duplicate overlapping pending/approved requests
- **DB:** `leave_requests`, `leave_request_documents`, `workflow_instances`, `notifications`, `audit_logs`

## Variations

### When employee has insufficient balance
- System warns: "You have N days remaining but are requesting M days"
- If leave type allows unpaid: "N days will be paid, M-N days will be unpaid"
- If leave type does not allow unpaid: submit button disabled

### When request requires extended notice period
- Policy requires N days notice → if request is for sooner, warning: "This request does not meet the minimum notice period of N days. Your manager will be informed"
- Request still submittable but flagged for approver

### When requesting on behalf of another employee (admin)
- Users with `leave:manage` can submit on behalf of employees
- Additional field: "Submitting on behalf of" with employee selector
- API: `POST /api/v1/leave/requests` with `employee_id` in body

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Insufficient leave balance | Submission blocked (if not unpaid-eligible) | "Insufficient balance. You have N days remaining for [Leave Type]" |
| Overlapping existing request | `409 Conflict` | "You already have a pending/approved leave request overlapping these dates" |
| Blackout period | Warning shown, may block | "The selected dates fall within a blackout period. Leave requests are restricted" |
| Past date without backdating permission | Validation fails | "Leave start date cannot be in the past" |
| Supporting document required but missing | Validation fails | "A supporting document is required for [Leave Type] requests exceeding N days" |
| Approver not found | Submission blocked | "No approver found in your reporting line. Please contact HR" |

## Events Triggered

- `LeaveRequestCreatedEvent` → [[backend/messaging/event-catalog|Event Catalog]] — consumed by notification service, calendar service
- `WorkflowInstanceCreatedEvent` → [[backend/messaging/event-catalog|Event Catalog]] — consumed by workflow engine for approval routing
- `AuditLogEntry` (action: `leave_request.created`) → [[modules/auth/audit-logging/overview|Audit Logging]]

## Related Flows

- [[Userflow/Leave/leave-approval|Leave Approval]] — approver processes this request
- [[Userflow/Leave/leave-cancellation|Leave Cancellation]] — employee cancels a submitted request
- [[Userflow/Leave/leave-balance-view|Leave Balance View]] — view current balances before requesting
- [[Userflow/Leave/leave-entitlement-assignment|Leave Entitlement Assignment]] — entitlements that determine available balance

## Module References

- [[modules/leave/overview|Leave]] — leave module overview and architecture
- [[modules/leave/leave-requests/overview|Leave Requests]] — request data model and lifecycle
- [[modules/leave/leave-entitlements/overview|Leave Entitlements]] — balance checking and deduction
- [[modules/calendar/calendar-events/overview|Calendar Events]] — holiday and team calendar data
- [[Userflow/Calendar/conflict-detection|Conflict Detection]] — overlap and team threshold checking
- [[backend/notification-system|Notification System]] — approval notification dispatch
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]] — approval workflow orchestration
- [[modules/documents/overview|Documents]] — supporting document storage
