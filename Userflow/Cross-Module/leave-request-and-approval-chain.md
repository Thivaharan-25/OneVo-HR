# Leave Request & Approval — Cross-Module Chain

**Area:** Cross-Module Scenario  
**Trigger:** Employee submits leave request (user action)  
**Required Permission(s):** `leave:create` (employee), `leave:approve` (manager), `payroll:read` (payroll impact)  
**Modules Involved:** Leave, Calendar, Workforce-Presence, Payroll, Notifications, Workflow Engine

---

## Context

A leave request isn't just a Leave module action. It touches the calendar (team overlap, holidays), attendance (shift coverage), payroll (unpaid leave deduction), and notifications (approval routing). This doc maps the full chain reaction from submission to payroll impact.

## Preconditions

- Employee has active leave entitlements → [[Userflow/Leave/leave-entitlement-assignment|Leave Entitlement Assignment]]
- Approval workflow configured (reporting line exists) → [[Userflow/Auth-Access/permission-assignment|Permission Assignment]]
- Leave policies active for employee's entity/country → [[Userflow/Leave/leave-policy-setup|Leave Policy Setup]]

---

## Chain Reaction Flow

| Order | Module | What Happens | Triggered By | Event Published |
|:------|:-------|:-------------|:-------------|:----------------|
| 1 | **Leave** | Leave request created with status `pending`. Days calculated excluding weekends/holidays | Employee submits form | `LeaveRequestCreated` |
| 2 | **Calendar** | Team calendar updated with tentative leave block (shown as pending). Conflict check: team absence threshold evaluated | `LeaveRequestCreated` | `CalendarEntryCreated` (tentative) |
| 3 | **Notifications** | Approval notification sent to manager via configured channels (in-app, email, push) | `LeaveRequestCreated` | `NotificationSent` |
| 4 | **Workflow Engine** | Approval workflow instance created. Multi-level approval triggered if policy requires | `LeaveRequestCreated` | `WorkflowInstanceCreated` |
| 5 | **Leave** | Manager approves → status changes to `approved`. Leave balance deducted | Manager approves | `LeaveRequestApproved` |
| 6 | **Calendar** | Tentative block changed to confirmed. Team calendar updated | `LeaveRequestApproved` | `CalendarEntryConfirmed` |
| 7 | **Workforce-Presence** | Employee's shift marked as "On Leave" for the approved dates. No attendance expected | `LeaveRequestApproved` | `ShiftOverrideCreated` |
| 8 | **Payroll** | If leave is unpaid or partially unpaid, deduction record created for next payroll run | `LeaveRequestApproved` + leave type config | `PayrollDeductionCreated` |
| 9 | **Notifications** | Employee notified of approval. Team notified if configured in policy | `LeaveRequestApproved` | `NotificationSent` |

---

## Dependency Chain

```
Leave Request Created (Step 1)
├── Calendar tentative entry (Step 2) — independent
├── Manager notification (Step 3) — independent
├── Approval workflow (Step 4) — independent
│
Manager Approves (Step 5)
├── Calendar confirmed (Step 6) — independent
├── Attendance override (Step 7) — independent
├── Payroll deduction (Step 8) — needs leave type info from Step 5
└── Approval notification (Step 9) — independent
```

---

## What If a Step Fails?

| Failed Step | Impact | Recovery |
|:------------|:-------|:---------|
| Calendar update fails | Team calendar shows stale data, but leave is valid | Auto-retry; admin can manually sync via Calendar |
| Manager notification fails | Manager unaware of pending request | Retry via notification service; employee can verbally notify |
| Attendance override fails | Employee marked absent on leave days | HR corrects via [[Userflow/Workforce-Presence/attendance-correction\|Attendance Correction]] |
| Payroll deduction not created | Employee overpaid for unpaid leave period | HR adds manual adjustment via [[Userflow/Payroll/payroll-adjustment\|Payroll Adjustment]] |

---

## Rejection Path

| Order | Module | What Happens |
|:------|:-------|:-------------|
| 5a | **Leave** | Manager rejects → status changes to `rejected` with reason |
| 6a | **Calendar** | Tentative block removed from team calendar |
| 7a | **Notifications** | Employee notified of rejection with manager's reason |

---

## Related Individual Flows

- [[Userflow/Leave/leave-request-submission|Leave Request Submission]] — detailed submission flow
- [[Userflow/Leave/leave-approval|Leave Approval]] — detailed approval flow
- [[Userflow/Leave/leave-cancellation|Leave Cancellation]] — cancellation after approval
- [[Userflow/Leave/leave-balance-view|Leave Balance View]] — balance checking
- [[Userflow/Workforce-Presence/shift-schedule-setup|Shift Schedule Setup]] — shift override context
- [[Userflow/Payroll/payroll-adjustment|Payroll Adjustment]] — manual correction flow

## Module References

- [[modules/leave/overview|Leave]]
- [[modules/calendar/overview|Calendar]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- [[backend/notification-system|Notification System]]
- [[backend/messaging/event-catalog|Event Catalog]]
