# Leave Cancellation

**Area:** Leave Management  
**Trigger:** Employee cancels submitted or approved leave (user action)
**Required Permission(s):** `leave:create` (own requests) or `leave:manage` (admin cancellation of any request)  
**Related Permissions:** `leave:read-own`, `leave:read`

---

## Preconditions

- A leave request exists with status `pending` or `approved`
- For own cancellation: employee is the request owner and has `leave:create`
- For admin cancellation: user has `leave:manage` permission
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Leave Request
- **UI:** Employee: navigates to Leave → My Leave → sees list of requests filtered by status (Pending, Approved, Rejected, Cancelled). Admin: navigates to Leave → All Requests or searches for specific employee
- **API:** `GET /api/v1/leave/requests/me` (employee) or `GET /api/v1/leave/requests?employeeId={id}` (admin)
- **Backend:** `LeaveRequestService.GetByEmployeeAsync()` → [[modules/leave/overview|Leave]]
- **Validation:** Checks `leave:create` or `leave:manage` permission
- **DB:** `leave_requests` (filtered by `employee_id` or all with admin access)

### Step 2: Select Request to Cancel
- **UI:** Click on an approved or pending request → detail view. "Cancel Request" button visible (disabled for already cancelled/rejected requests and for past completed leaves)
- **API:** N/A (navigation)
- **Backend:** N/A
- **Validation:** Cancel button only enabled if: request status is `pending` or `approved`, and leave start date has not fully passed (partial cancellation possible for in-progress leaves)
- **DB:** None

### Step 3: Confirm Cancellation
- **UI:** Click "Cancel Request" → confirmation dialog: "Are you sure you want to cancel this leave request? [Leave Type] from [Start Date] to [End Date] ([N days])". If request was approved, additional note: "Your balance of N days will be restored." Optional: cancellation reason text field (required for admin cancellations)
- **API:** N/A (client-side confirmation)
- **Backend:** N/A
- **Validation:** Client-side confirmation required
- **DB:** None

### Step 4: Process Cancellation
- **UI:** Click "Confirm Cancel". Success toast: "Leave request cancelled successfully"
- **API:** `POST /api/v1/leave/requests/{requestId}/cancel`
- **Backend:** `LeaveRequestService.CancelAsync()` → [[modules/leave/overview|Leave]]
  1. Updates `leave_requests` status to `cancelled`
  2. Stores cancellation reason and cancelling user
  3. If request was `approved`:
     - Restores balance: decrements `used_days` in `leave_entitlements`
     - Removes calendar event via [[modules/calendar/calendar-events/overview|Calendar Events]]
     - If unpaid leave, removes payroll deduction flag
  4. If request was `pending`:
     - Cancels workflow instance
     - No balance change needed
  5. Sends notifications:
     - To employee (if admin-cancelled): "Your [Leave Type] request for [Dates] has been cancelled by [Admin Name]"
     - To manager (if employee-cancelled and was approved): "[Employee Name] has cancelled their approved [Leave Type] for [Dates]"
  6. Creates audit log entry with before/after state
  7. Publishes `LeaveRequestCancelledEvent`
- **Validation:** Request must be in `pending` or `approved` status. Cannot cancel if leave period has fully elapsed. Partial cancellation: if leave is in progress, only remaining days can be cancelled
- **DB:** `leave_requests`, `leave_entitlements`, `calendar_events`, `workflow_instances`, `notifications`, `audit_logs`

## Variations

### When cancelling a partially taken leave
- Leave start date is in the past but end date is in the future
- System calculates days already taken vs. remaining days
- Only remaining (future) days are cancelled and restored to balance
- Already-taken days remain deducted
- API body includes `effective_cancel_date` (defaults to today)

### When admin cancels on behalf of employee
- Admin must provide a reason (mandatory)
- Employee receives notification with reason
- Audit trail clearly shows admin-initiated cancellation

### When leave was part of multi-level approval
- If only first level approved, cancellation reverts workflow
- All approvers in the chain are notified of the cancellation

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Request already cancelled | `409 Conflict` | "This leave request has already been cancelled" |
| Request already rejected | `422 Unprocessable` | "Rejected requests cannot be cancelled" |
| Leave period fully elapsed | `422 Unprocessable` | "This leave period has already passed and cannot be cancelled" |
| Admin cancellation without reason | Validation fails | "A reason is required when cancelling on behalf of an employee" |
| Concurrent modification | `409 Conflict` | "This request was modified by another user. Please refresh and try again" |

## Events Triggered

- `LeaveRequestCancelledEvent` → [[backend/messaging/event-catalog|Event Catalog]] — consumed by calendar service (remove event), payroll module (remove deduction if unpaid), notification service
- `LeaveBalanceRestoredEvent` → [[backend/messaging/event-catalog|Event Catalog]] — consumed by entitlement tracking
- `CalendarEventDeletedEvent` → [[backend/messaging/event-catalog|Event Catalog]] — team calendar updated
- `AuditLogEntry` (action: `leave_request.cancelled`) → [[modules/auth/audit-logging/overview|Audit Logging]]

## Related Flows

- [[Userflow/Leave/leave-request-submission|Leave Request Submission]] — the original request being cancelled
- [[Userflow/Leave/leave-approval|Leave Approval]] — approved requests that may be cancelled
- [[Userflow/Leave/leave-balance-view|Leave Balance View]] — balance restored after cancellation

## Module References

- [[modules/leave/overview|Leave]] — leave module overview and architecture
- [[modules/leave/leave-requests/overview|Leave Requests]] — request data model and lifecycle
- [[modules/leave/leave-entitlements/overview|Leave Entitlements]] — balance restoration on cancellation
- [[modules/leave/balance-audit/overview|Balance Audit]] — audit trail for balance changes
- [[modules/calendar/calendar-events/overview|Calendar Events]] — calendar event removal
- [[backend/notification-system|Notification System]] — cancellation notification dispatch
