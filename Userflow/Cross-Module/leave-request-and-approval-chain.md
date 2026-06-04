# Leave Request & Approval - Cross-Module Chain

**Area:** Cross-Module Scenario  
**Trigger:** Employee submits leave request  
**Required Permission(s):** `leave:create`, `leave:approve`, `workflows:read`  
**Modules Involved:** Leave, Calendar, Workforce Presence, Payroll, Notifications, Workflow Engine, Automation Center, Chat or Inbox

---

## Context

A leave request touches the calendar, attendance, payroll, notifications, workflow automation, and sometimes WorkSync Chat or Microsoft Teams. Approval routing is owned by Automation Center and the workflow engine, using dynamic resolvers instead of fixed role names.

## Preconditions

- Employee has active leave entitlements: [[Userflow/Leave/leave-entitlement-assignment|Leave Entitlement Assignment]]
- Approval automation is configured in [[Userflow/Automation/automation-center|Automation Center]]
- Resolver source exists, such as reporting line, team lead, department owner, selected permission, selected employee, or configured escalation owner
- Leave policies are active for the employee's entity/country: [[Userflow/Leave/leave-policy-setup|Leave Policy Setup]]

---

## Chain Reaction Flow

| Order | Module | What Happens | Triggered By | Event Published |
|:------|:-------|:-------------|:-------------|:----------------|
| 1 | **Leave** | Leave request created with status `pending`. Days calculated excluding weekends/holidays | Employee submits form | `LeaveRequestCreated` |
| 2 | **Calendar** | Team calendar updated with tentative leave block. Conflict check evaluates team absence threshold | `LeaveRequestCreated` | `CalendarEntryCreated` |
| 3 | **Workflow Engine / Automation Center** | Workflow instance created. Resolver finds approver or approvers. Approval mode determines whether any one, all, or sequential approvals are required | `LeaveRequestCreated` | `WorkflowInstanceCreated` |
| 4 | **Chat or Inbox** | Delivery router creates a case conversation and action card in Chat, or an Inbox detail item if Chat is not enabled | `WorkflowStepAssigned` | `CaseConversationCreated` / `NotificationSent` |
| 5 | **Leave** | Assigned approver approves according to workflow mode. When required approval is complete, status changes to `approved` and leave balance is deducted | Workflow approval action | `LeaveRequestApproved` |
| 6 | **Calendar** | Tentative block changed to confirmed. Team calendar updated | `LeaveRequestApproved` | `CalendarEntryConfirmed` |
| 7 | **Workforce Presence** | Employee's shift marked as "On Leave" for the approved dates | `LeaveRequestApproved` | `ShiftOverrideCreated` |
| 8 | **Payroll** | If leave is unpaid or partially unpaid, deduction record created for next payroll run | `LeaveRequestApproved` + leave type config | `PayrollDeductionCreated` |
| 9 | **Notifications** | Employee notified of approval. Team notified if configured in policy | `LeaveRequestApproved` | `NotificationSent` |

---

## Approval Modes

When a resolver returns two reporting managers or multiple approvers, the workflow step defines the mode:

| Mode | Result |
|:-----|:-------|
| Only one approval is required | Both managers receive it. First approval completes the leave request. |
| All assigned approvers must approve | Request stays pending until every assigned approver approves. |
| Approve in order | Approver A receives it first; Approver B receives it only after Approver A approves. |

## Manager Unavailable Handling

ONEVO does not need a separate manager-absence setup for the normal leave approval path. If the reporting manager is unavailable:

- The manager can delegate that specific workflow action to another allowed approver.
- If no action happens before the configured wait/SLA, the unresolved workflow escalates to the configured resolver, such as department owner or configured escalation owner.
- The leave request stays auditable through `approval_actions`, including original assignee, delegated approver, escalation, and final decision.

---

## Dependency Chain

```text
Leave Request Created
├── Calendar tentative entry
├── Automation resolver evaluation
├── Chat case conversation or Inbox action card
│
Workflow approval completed
├── Calendar confirmed
├── Attendance override
├── Payroll deduction if unpaid
└── Approval notification
```

---

## What If a Step Fails?

| Failed Step | Impact | Recovery |
|:------------|:-------|:---------|
| Calendar update fails | Team calendar shows stale data, but leave is valid | Auto-retry; admin can manually sync via Calendar |
| Resolver returns no approver | Workflow is blocked | Notify automation owner or configured escalation owner to fix routing |
| Action-card delivery fails | Approver may not see pending request | Retry via delivery router; unresolved workflow can escalate |
| Attendance override fails | Employee marked absent on leave days | Authorized attendance user corrects via [[Userflow/Workforce-Presence/attendance-correction\|Attendance Correction]] |
| Payroll deduction not created | Employee overpaid for unpaid leave period | Payroll user adds manual adjustment via [[Userflow/Payroll/payroll-adjustment\|Payroll Adjustment]] |

---

## Rejection Path

| Order | Module | What Happens |
|:------|:-------|:-------------|
| 5a | **Workflow / Leave** | Assigned approver rejects with reason. Workflow completes rejected and leave status changes to `rejected` |
| 6a | **Calendar** | Tentative block removed from team calendar |
| 7a | **Notifications** | Employee notified of rejection with approver's reason |

---

## Related Individual Flows

- [[Userflow/Automation/automation-center|Automation Center]]
- [[Userflow/Leave/leave-request-submission|Leave Request Submission]]
- [[Userflow/Leave/leave-approval|Leave Approval]]
- [[Userflow/Leave/leave-cancellation|Leave Cancellation]]
- [[Userflow/Workforce-Presence/shift-schedule-setup|Shift Schedule Setup]]
- [[Userflow/Payroll/payroll-adjustment|Payroll Adjustment]]

## Module References

- [[modules/leave/overview|Leave]]
- [[modules/calendar/overview|Calendar]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- [[backend/notification-system|Notification System]]
