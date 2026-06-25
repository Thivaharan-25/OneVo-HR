# Time Off Approval

**Area:** Time Off
**Trigger:** Approver receives notification/action item after time off request submission
**Required Permission(s):** `time_off:approve`
**Related Permissions:** `time_off:read`, `time_off:approve`, `calendar:read`

---

## Preconditions

- A time off request has been submitted with status `pending`: [[Userflow/Time-Off/time-off-request-submission|Time Off Request Submission Flow]]
- Phase 1 uses management coverage as the single routing source. Workflow/Automation Engine routing is Phase 2.
- Approver assignment resolves to one eligible owner from management coverage.
- Approver has `time_off:approve` permission through the tenant's dynamic permission model.

## Default Management Coverage Approval

When no custom Phase 2 workflow is configured, ONEVO resolves the Phase 1 owner from management coverage:

1. Load the employee's active Company, active position, and department.
2. Try position coverage owners in order: Primary owner, Backup owner 1, Backup owner 2, etc.
3. If no valid position owner exists, try department coverage owners in the same order.
4. If no valid department owner exists, try company-wide coverage owners in the same order.
5. A candidate is valid only when the occupant is active, has an active linked user account, has `time_off:approve`, belongs to the same Company context, and is not blocked by self-approval rules.
6. Assign the request to the first valid owner only.
7. If no valid owner exists, create a routing issue.

This default path must not use a fixed HR role name. HR users can approve time_off when their role gives `time_off:approve` and their position has management coverage for the employee.

---

## Flow Steps

### Step 1: Receive Approval Action Card

- **UI:** Approver receives an action item through Notifications/Inbox. If WorkSync Chat is enabled, ONEVO may create or reuse a time off request case conversation and post the action there. Email or push can still notify the approver that action is waiting.
- **API:** N/A
- **Backend:** Time off approval routing starts from `TimeOffRequestCreatedEvent`, resolves the Phase 1 approver, creates a case conversation when configured, and routes the action through Notifications/Inbox.
- **Validation:** N/A
- **DB:** `time_off_requests`, `notifications`, `audit_logs`; case conversation tables when Chat is enabled

### Step 2: Open Approval Context

- **UI:** Click action card -> opens the time off request case conversation or Inbox detail panel. Authorized approvers can also open the managed time off approvals view. The request shows employee, time off type, dates/time range, requested hours, deducted hours preview, submitted time, current approver state, and available actions.
- **API:** `GET /api/v1/time-off/requests?status=pending&approverId=me`
- **Backend:** `TimeOffRequestService.GetPendingForApproverAsync()` loads requests assigned to the current user by Phase 1 approval routing.
- **Validation:** Checks `time_off:approve` permission and verifies the current user is the assigned owner.
- **DB:** `time_off_requests`, `notifications`

### Step 3: Review Request Details

- **API:** `GET /api/v1/time-off/requests/{requestId}/review-context`
- **Validation:** Read-only access is scoped to the approval assignment, employee visibility, and `time_off:read`.

### Step 4a: Approve Request

- **UI:** Click Approve -> optional comment -> confirm.
- **API:** `POST /api/v1/time-off/requests/{requestId}/approve`
- **Backend:** Time Off records the approval action, updates status, deducts balance, creates calendar event, notifies employee, handles payroll flagging for unpaid time_off, publishes `TimeOffRequestApprovedEvent`, and writes audit logs.
- **Validation:** Request must still be pending and caller must be the assigned owner. Approver cannot approve their own request unless a specific policy allows it.
- **DB:** `time_off_requests`, `time_off_entitlements`, `calendar_events`, `notifications`, `audit_logs`

### Step 4b: Reject Request

- **UI:** Click Reject -> required reason -> confirm.
- **API:** `POST /api/v1/time-off/requests/{requestId}/reject`
- **Backend:** Time Off records rejection, updates status to `rejected`, stores reason, notifies employee, publishes `TimeOffRequestRejectedEvent`, and writes audit logs.
- **Validation:** Rejection reason is mandatory. Request must still be pending and caller must be an active assignee.
- **DB:** `time_off_requests`, `notifications`, `audit_logs`

### Step 4c: Request More Information

- **UI:** Click Request information -> add question/comment -> submit. The employee or original requester is added to the case conversation if enabled.
- **API:** `POST /api/v1/time-off/requests/{requestId}/request-info`
- **Backend:** Time Off records the action, posts the request into the case conversation or Inbox detail panel, and keeps the request pending.
- **Validation:** Caller must be the assigned owner.
- **DB:** `time_off_requests`, case conversation messages or Inbox comments, `audit_logs`

### Step 5: Bulk Actions

- **UI:** Pending Approvals can support bulk approve/reject for similar requests when policy allows it.
- **API:** `POST /api/v1/time-off/requests/bulk-approve` or `POST /api/v1/time-off/requests/bulk-reject`
- **Backend:** Applies the same Phase 1 approval validation per request. Partial success is possible.
- **Validation:** Each request validates current approver assignment and state independently.
- **DB:** Same as individual approve/reject, per request

---

## Variations

### When Multiple Approvers Are Assigned

Multi-approver and sequential approval modes are Phase 2 Workflow/Automation Engine behavior. Phase 1 uses a single assigned owner.

### When Request Requires Multi-Level Approval

Multi-level approval is Phase 2. Phase 1 sends the request to the single eligible owner resolved from management coverage.

### When Approver Delegates This Approval

Request-specific delegation is Phase 2.

### When Approver Is Unavailable Or Does Not Act

Phase 1 can send reminder notifications and surface blocked approvals to authorized admins. SLA escalation paths are Phase 2 Workflow/Automation behavior.

### When Administrative Intervention Is Allowed

Users with broader Time Off permissions can intervene only when their role and management coverage permit it. ONEVO must not assume a fixed HR role name.

### When HR Approves Time Off

HR approval is management coverage, not org chart shape. If the company wants HR to approve time_off for everyone in Phase 1, grant the HR position `time_off:approve` and company-wide **Can manage employees in** coverage. Do not set every employee's Reports to value to an HR position just because HR approves time_off.

---

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Request already processed | `409 Conflict` | "This request has already been approved or rejected" |
| Caller is not the assigned owner | `403 Forbidden` | "This request is not assigned to you" |
| No eligible owner exists | Routing issue created | "No eligible owner could approve this request. Check position coverage and permissions." |
| Approver tries to approve own request | `403 Forbidden` unless policy allows | "You cannot approve your own time off request" |
| Employee balance changed since submission | Warning shown | "Employee's balance has changed since submission. Current balance: N hours" |
| Employee terminated since submission | `422 Unprocessable` | "This employee is no longer active. Request cannot be processed" |
| Missing rejection reason | Validation fails | "A reason is required when rejecting a time off request" |

## Events Triggered

- `TimeOffRequestApprovedEvent`
- `TimeOffRequestRejectedEvent`
- `CalendarEventCreatedEvent`
- `AuditLogEntry`

## Related Flows

- [[Userflow/Automation/automation-center|Automation Center]] - Phase 2
- [[Userflow/Time-Off/time-off-request-submission|Time Off Request Submission]]
- [[Userflow/Time-Off/hr-coverage-routing|HR Coverage Routing]]
- [[Userflow/Time-Off/time-off-cancellation|Time Off Cancellation]]
- [[Userflow/Notifications/inbox|Inbox]]
- [[Userflow/Chat/chat-overview|Chat Overview]]

## Module References

- [[modules/time-off/overview|Time Off]]
- [[modules/calendar/calendar-events/overview|Calendar Events]]
- [[backend/notification-system|Notification System]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]] - Phase 2
