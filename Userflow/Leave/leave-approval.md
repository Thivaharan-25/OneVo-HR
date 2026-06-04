# Leave Approval

**Area:** Leave Management  
**Trigger:** Approver receives workflow action card after leave request submission  
**Required Permission(s):** `leave:approve`  
**Related Permissions:** `leave:read`, `leave:approve`, `calendar:read`, `workflows:read`

---

## Preconditions

- A leave request has been submitted with status `pending`: [[Userflow/Leave/leave-request-submission|Leave Request Submission Flow]]
- The tenant has an active Automation Center workflow for leave requests or a default approval workflow.
- Approver assignment is resolved dynamically, such as employee's reporting manager, users with selected permission, department owner, team lead, specific employee, or configured escalation owner.
- Approver has `leave:approve` permission through the tenant's dynamic permission model.

---

## Flow Steps

### Step 1: Receive Approval Action Card

- **UI:** Approver receives an action card through the delivery router. If WorkSync Chat is enabled, ONEVO creates or reuses a leave request case conversation and posts the card there. If Chat is not enabled, the card appears in Inbox. Email or push can still notify the approver that action is waiting.
- **API:** N/A
- **Backend:** Automation workflow starts from `LeaveRequestCreatedEvent`, resolves approver dynamically, creates a case conversation when configured, and routes the action card through Chat or Inbox.
- **Validation:** N/A
- **DB:** `workflow_instances`, `workflow_step_instances`, `approval_actions`, `notifications`; case conversation tables when Chat is enabled

### Step 2: Open Approval Context

- **UI:** Click action card -> opens the leave request case conversation or Inbox detail panel. Users can also open Leave -> Pending Approvals. The request shows employee, leave type, dates, total days, submitted time, current approver state, and available actions.
- **API:** `GET /api/v1/leave/requests?status=pending&approverId=me`
- **Backend:** `LeaveRequestService.GetPendingForApproverAsync()` loads requests where the workflow has assigned the current user.
- **Validation:** Checks `leave:approve` permission and verifies the current user is an active assignee from the workflow resolver.
- **DB:** `leave_requests`, `workflow_instances`, `workflow_step_instances`

### Step 3: Review Request Details

- **UI:** Detail view shows employee info, leave type, dates, total days, reason, supporting documents, balance impact, calendar conflicts, leave history, and team coverage.
- **API:** `GET /api/v1/leave/requests/{requestId}/review-context`
- **Backend:** `LeaveRequestService.GetReviewContextAsync()` loads leave, calendar, employee, and team context.
- **Validation:** Read-only access is scoped to the workflow assignment and `leave:read`.
- **DB:** `leave_requests`, `leave_entitlements`, `employees`, calendar and team overlap data

### Step 4a: Approve Request

- **UI:** Click Approve -> optional comment -> confirm.
- **API:** `POST /api/v1/leave/requests/{requestId}/approve`
- **Backend:** Workflow records the approval action. If the approval step is complete, Leave updates status, deducts balance, creates calendar event, notifies employee, handles payroll flagging for unpaid leave, publishes `LeaveRequestApprovedEvent`, and writes audit logs.
- **Validation:** Request must still be pending and caller must be an active assignee. Approver cannot approve their own request unless a specific policy allows it.
- **DB:** `leave_requests`, `leave_entitlements`, `calendar_events`, `workflow_instances`, `approval_actions`, `notifications`, `audit_logs`

### Step 4b: Reject Request

- **UI:** Click Reject -> required reason -> confirm.
- **API:** `POST /api/v1/leave/requests/{requestId}/reject`
- **Backend:** Workflow records rejection, Leave updates status to `rejected`, stores reason, notifies employee, publishes `LeaveRequestRejectedEvent`, and writes audit logs.
- **Validation:** Rejection reason is mandatory. Request must still be pending and caller must be an active assignee.
- **DB:** `leave_requests`, `workflow_instances`, `approval_actions`, `notifications`, `audit_logs`

### Step 4c: Request More Information

- **UI:** Click Request information -> add question/comment -> submit. The employee or original requester is added to the case conversation if the automation allows it.
- **API:** `POST /api/v1/workflows/{instanceId}/request-info`
- **Backend:** Workflow records the action, posts the request into the case conversation or Inbox detail panel, and pauses or changes the step state according to the automation timing rule.
- **Validation:** Caller must be an active assignee for the workflow step.
- **DB:** `approval_actions`, `workflow_step_instances`, case conversation messages or Inbox comments, `audit_logs`

### Step 5: Bulk Actions

- **UI:** Pending Approvals can support bulk approve/reject for similar requests when policy allows it.
- **API:** `POST /api/v1/leave/requests/bulk-approve` or `POST /api/v1/leave/requests/bulk-reject`
- **Backend:** Applies the same workflow validation per request. Partial success is possible.
- **Validation:** Each request validates current workflow assignment and state independently.
- **DB:** Same as individual approve/reject, per request

---

## Variations

### When Multiple Approvers Are Assigned

The workflow step must specify an approval mode:

- **Only one approval is required:** both managers receive it; Manager A approves; the request is approved; Manager B sees it as completed.
- **All assigned approvers must approve:** Manager A approves; status becomes "Waiting for Manager B"; leave is approved only after Manager B approves.
- **Approve in order:** Manager A receives and approves first; Manager B receives it after Manager A approves.

### When Request Requires Multi-Level Approval

After one approval step completes, the workflow advances to the next resolver. Example: employee's reporting manager first, then department owner for long leave. The status should name the pending resolver outcome, not a fixed role name.

### When Approver Delegates This Approval

Approver can delegate the current workflow action to another allowed approver. This is request-specific and does not require a separate manager-absence setup. The audit trail records the original approver, delegated approver, comment, and timestamp.

### When Approver Is Unavailable Or Does Not Act

If the assigned approver does not act before the workflow SLA, the unresolved item follows the configured escalation path. For normal leave, the default escalation target should be department owner or configured escalation owner, not a fixed HR role name.

### When Administrative Intervention Is Allowed

Users with broader leave permissions can intervene only when the workflow, permission, or override policy permits it. ONEVO must not assume a fixed HR role name.

---

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Request already processed | `409 Conflict` | "This request has already been approved or rejected" |
| Caller is not an active workflow assignee | `403 Forbidden` | "This request is not assigned to you" |
| Approver tries to approve own request | `403 Forbidden` unless policy allows | "You cannot approve your own leave request" |
| Employee balance changed since submission | Warning shown | "Employee's balance has changed since submission. Current balance: N days" |
| Employee terminated since submission | `422 Unprocessable` | "This employee is no longer active. Request cannot be processed" |
| Missing rejection reason | Validation fails | "A reason is required when rejecting a leave request" |

## Events Triggered

- `LeaveRequestApprovedEvent`
- `LeaveRequestRejectedEvent`
- `WorkflowApprovalActionRecorded`
- `WorkflowApproved` or `WorkflowRejected`
- `CalendarEventCreatedEvent`
- `AuditLogEntry`

## Related Flows

- [[Userflow/Automation/automation-center|Automation Center]]
- [[Userflow/Leave/leave-request-submission|Leave Request Submission]]
- [[Userflow/Leave/leave-cancellation|Leave Cancellation]]
- [[Userflow/Notifications/inbox|Inbox]]
- [[Userflow/Chat/chat-overview|Chat Overview]]

## Module References

- [[modules/leave/overview|Leave]]
- [[modules/calendar/calendar-events/overview|Calendar Events]]
- [[backend/notification-system|Notification System]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
