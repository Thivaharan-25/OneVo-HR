# Leave Approval

**Area:** Leave Management  
**Trigger:** Approver receives notification or opens approval queue (reaction — triggered by leave request)
**Required Permission(s):** `leave:approve`  
**Related Permissions:** `leave:read` (to view team leave details), `calendar:read` (to check calendar impact)

---

## Preconditions

- A leave request has been submitted with status `pending`: [[Userflow/Leave/leave-request-submission|Leave Request Submission Flow]]
- Approver is in the employee's reporting line (direct manager or delegated approver)
- Approver has `leave:approve` permission assigned via their Job Family role
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Receive Approval Notification
- **UI:** Approver receives notification via: in-app notification bell (badge count incremented), email notification with request summary, optional push notification (mobile). Notification includes: employee name, leave type, dates, total days
- **API:** N/A (notification received)
- **Backend:** `NotificationService.SendAsync()` → [[backend/notification-system|Notification System]] (triggered by `LeaveRequestCreatedEvent`)
- **Validation:** N/A
- **DB:** `notifications`

### Step 2: Navigate to Pending Approvals
- **UI:** Click notification → navigates to Leave → Pending Approvals. Or manually navigate to Leave → Pending Approvals. Table shows all pending requests with columns: Employee, Leave Type, Start Date, End Date, Total Days, Submitted On, Actions
- **API:** `GET /api/v1/leave/requests?status=pending&approverId=me`
- **Backend:** `LeaveRequestService.GetPendingForApproverAsync()` → [[modules/leave/overview|Leave]]
- **Validation:** Checks `leave:approve` permission. Only shows requests where current user is the designated approver
- **DB:** `leave_requests`, `workflow_instances`

### Step 3: Review Request Details
- **UI:** Click on a request → detail view showing:
  - **Employee Info:** Name, department, position, tenure
  - **Request Details:** Leave type, start date, end date, total days, reason, supporting documents (downloadable)
  - **Balance Impact:** Current balance → balance after approval (visual bar chart)
  - **Calendar Conflicts:** Other team members on leave during same period (list with names and dates)
  - **Leave History:** Employee's recent leave requests (last 6 months)
  - **Team Coverage:** Team size, number already on leave, coverage percentage
- **API:** `GET /api/v1/leave/requests/{requestId}/review-context`
- **Backend:** `LeaveRequestService.GetReviewContextAsync()` → [[modules/leave/overview|Leave]]
- **Validation:** N/A (read-only)
- **DB:** `leave_requests`, `leave_entitlements`, `employees`, `leave_requests` (team overlap query)

### Step 4a: Approve Request
- **UI:** Click "Approve" button → optional comment field → confirm. Success toast: "Leave request approved"
- **API:** `POST /api/v1/leave/requests/{requestId}/approve`
- **Backend:** `LeaveApprovalService.ApproveAsync()` → [[modules/leave/overview|Leave]]
  1. Updates `leave_requests` status to `approved`
  2. Deducts days from `leave_entitlements` (increments `used_days`)
  3. Creates calendar event for the leave period via [[modules/calendar/calendar-events/overview|Calendar Events]]
  4. Completes workflow instance
  5. Sends notification to employee: "Your [Leave Type] request for [Dates] has been approved"
  6. If leave is unpaid, flags for payroll deduction via [[modules/payroll/payroll-execution/overview|Payroll Execution]]
  7. Publishes `LeaveRequestApprovedEvent`
  8. Creates audit log entry
- **Validation:** Request must still be in `pending` status (prevents double-approval). Approver cannot approve own request
- **DB:** `leave_requests`, `leave_entitlements`, `calendar_events`, `workflow_instances`, `notifications`, `audit_logs`

### Step 4b: Reject Request
- **UI:** Click "Reject" button → rejection reason field (required) → confirm. Success toast: "Leave request rejected"
- **API:** `POST /api/v1/leave/requests/{requestId}/reject`
- **Backend:** `LeaveApprovalService.RejectAsync()` → [[modules/leave/overview|Leave]]
  1. Updates `leave_requests` status to `rejected`
  2. Balance remains unchanged (no deduction)
  3. Stores rejection reason
  4. Completes workflow instance
  5. Sends notification to employee: "Your [Leave Type] request for [Dates] has been rejected. Reason: [reason]"
  6. Publishes `LeaveRequestRejectedEvent`
  7. Creates audit log entry
- **Validation:** Rejection reason is mandatory. Request must still be in `pending` status
- **DB:** `leave_requests`, `workflow_instances`, `notifications`, `audit_logs`

### Step 5: Bulk Actions (Optional)
- **UI:** From Pending Approvals list → select multiple requests via checkboxes → "Bulk Approve" or "Bulk Reject" button. For bulk reject, single reason applied to all
- **API:** `POST /api/v1/leave/requests/bulk-approve` or `POST /api/v1/leave/requests/bulk-reject`
- **Backend:** `LeaveApprovalService.BulkApproveAsync()` → [[modules/leave/overview|Leave]] — iterates through each request, applies same logic as individual approval
- **Validation:** Each request validated individually. Partial success possible (some approved, some failed)
- **DB:** Same as individual approve/reject, per request

## Variations

### When request requires multi-level approval
- After first approver approves, request moves to next approver in chain (e.g., HR Head for leaves > 5 days)
- Status changes to `pending_l2_approval`
- Original approver sees status: "Approved by you. Pending [Next Approver] approval"

### When approver delegates approval authority
- Approver can set a delegate for a date range (e.g., during own leave)
- Delegate sees pending requests in their approval queue
- Audit trail shows both delegate and original approver

### When approver also has `leave:manage` (HR Admin)
- Can approve any employee's request regardless of reporting line
- Additional filter: "All Pending Requests" (not just direct reports)
- Can override policy warnings (e.g., approve despite blackout period)

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Request already processed | `409 Conflict` | "This request has already been [approved/rejected]" |
| Approver tries to approve own request | `403 Forbidden` | "You cannot approve your own leave request" |
| Employee balance changed since submission | Warning shown | "Employee's balance has changed since submission. Current balance: N days" |
| Employee terminated since submission | `422 Unprocessable` | "This employee is no longer active. Request cannot be processed" |
| Missing rejection reason | Validation fails | "A reason is required when rejecting a leave request" |

## Events Triggered

- `LeaveRequestApprovedEvent` → [[backend/messaging/event-catalog|Event Catalog]] — consumed by calendar service, payroll module (if unpaid), notification service
- `LeaveRequestRejectedEvent` → [[backend/messaging/event-catalog|Event Catalog]] — consumed by notification service
- `CalendarEventCreatedEvent` → [[backend/messaging/event-catalog|Event Catalog]] — team calendar updated (on approval)
- `AuditLogEntry` (action: `leave_request.approved` or `leave_request.rejected`) → [[modules/auth/audit-logging/overview|Audit Logging]]

## Related Flows

- [[Userflow/Leave/leave-request-submission|Leave Request Submission]] — the request being approved
- [[Userflow/Leave/leave-cancellation|Leave Cancellation]] — cancel an approved request
- [[Userflow/Leave/leave-balance-view|Leave Balance View]] — check balances affected by approval

## Module References

- [[modules/leave/overview|Leave]] — leave module overview and architecture
- [[modules/leave/leave-requests/overview|Leave Requests]] — request data model and lifecycle
- [[modules/leave/leave-entitlements/overview|Leave Entitlements]] — balance deduction on approval
- [[modules/calendar/calendar-events/overview|Calendar Events]] — calendar event creation on approval
- [[backend/notification-system|Notification System]] — approval/rejection notification dispatch
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]] — approval workflow orchestration
