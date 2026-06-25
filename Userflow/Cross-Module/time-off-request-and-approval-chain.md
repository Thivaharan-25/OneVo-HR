# Time Off Request & Approval - Cross-Module Chain

**Area:** Cross-Module Scenario  
**Trigger:** Employee submits a Time Off request  
**Required Permission(s):** `time_off:create`, `time_off:approve`
**Modules Involved:** Time Off, Calendar, Time & Attendance, Payroll, Notifications, Chat or Inbox. Workflow Engine / Automation Center is Phase 2.

---

## Context

A Time Off request touches the calendar, attendance, payroll, notifications, and sometimes Work Chat or Microsoft Teams. Phase 1 approval routing is owned by Time Off using Org Structure management coverage, not Workflow Engine.

## Preconditions

- Employee has active Time Off entitlements: [[Userflow/Time-Off/time-off-entitlement-assignment|Time Off Entitlement Assignment]]
- Management coverage is configured for the employee's position, department, or Company.
- Time Off policies are active for the employee's entity/country: [[Userflow/Time-Off/time-off-policy-setup|Time Off Policy Setup]]

---

## Chain Reaction Flow

| Order | Module | What Happens | Triggered By | Event Published |
|:------|:-------|:-------------|:-------------|:----------------|
| 1 | **Time Off** | Time Off request created with status `pending`. Requested hours are calculated from request mode, effective schedule, and holiday/calendar exclusions | Employee submits form | `TimeOffRequestCreated` |
| 3 | **Time Off** | Phase 1 owner resolved from management coverage. No workflow instance is created. | `TimeOffRequestCreated` | `TimeOffApprovalAssigned` |
| 4 | **Chat or Inbox** | Notification/action item is created in Inbox or Chat when enabled | `TimeOffApprovalAssigned` | `CaseConversationCreated` / `NotificationSent` |
| 5 | **Time Off** | Assigned approver approves. Status changes to `approved` and time off balance is deducted | Time Off approval action | `TimeOffRequestApproved` |
| 7 | **Time & Attendance** | Employee's shift marked as "On Time Off" for the approved dates. For partial-day Time Off, a time_off exclusion interval is created for the approved time range | `TimeOffRequestApproved` | `ShiftOverrideCreated` |
| 7b | **Agent Gateway** | For partial-day Time Off during a workday: sends `PauseMonitoring(reason = approved_time_off)` at interval start; sends `ResumeMonitoring` at interval end. Activity Monitoring, work-location evidence, and Discrepancy Engine treat this interval as explained absence | `TimeOffIntervalStarted` / `TimeOffIntervalEnded` | - |
| 8 | **Payroll** | If Time Off is unpaid or partially unpaid, deduction record created for next payroll run | `TimeOffRequestApproved` + Time Off type config | `PayrollDeductionCreated` |

---

## Approval Modes

Multi-approver modes are Phase 2 Workflow/Automation Engine behavior. Phase 1 uses one assigned owner resolved from management coverage.

## Manager Unavailable Handling

ONEVO does not need a separate manager-absence setup for the normal Time Off approval path. If the primary owner is unavailable or invalid:

- Backup owner 1, Backup owner 2, and later owners are tried in order.
- If no valid owner exists, create a routing issue for authorized admins.
- The Time Off request stays auditable through Time Off approval history and audit logs.

---

## Dependency Chain

```text
Time Off Request Created
+-- Calendar tentative entry
+-- Management coverage owner resolution
+-- Chat case conversation or Inbox action card
|
Time Off approval completed
+-- Calendar confirmed
+-- Attendance override (full-day or partial-day exclusion interval)
+-- Monitoring pause during approved Time Off intervals (partial-day)
+-- Payroll deduction if unpaid
+-- Approval notification
```

---

## What If a Step Fails?

| Failed Step | Impact | Recovery |
|:------------|:-------|:---------|
| Resolver returns no approver | Approval is blocked | Create routing issue: "No eligible owner could approve this request. Check position coverage and permissions." |
| Action-item delivery fails | Approver may not see pending request | Retry notification delivery; blocked approval appears for authorized admins |
| Time & Attendance override fails | Employee may be marked absent during approved time off ranges | Authorized attendance user corrects via [[Userflow/Time-Attendance/attendance-correction\|Attendance Correction]] |
| Payroll deduction not created | Employee overpaid for unpaid time off period | Payroll user adds manual adjustment via [[Userflow/Payroll/payroll-adjustment\|Payroll Adjustment]] |

---

## Rejection Path

| Order | Module | What Happens |
|:------|:-------|:-------------|
| 5a | **Time Off** | Assigned approver rejects with reason and Time Off status changes to `rejected` |
| 7a | **Notifications** | Employee notified of rejection with approver's reason |

---

## Related Individual Flows

- [[Userflow/Automation/automation-center|Automation Center]] - Phase 2
- [[Userflow/Time-Off/time-off-request-submission|Time Off Request Submission]]
- [[Userflow/Time-Off/time-off-approval|Time Off Approval]]
- [[Userflow/Time-Off/time-off-cancellation|Time Off Cancellation]]
- [[Userflow/Time-Attendance/shift-schedule-setup|Shift Schedule Setup]]
- [[Userflow/Payroll/payroll-adjustment|Payroll Adjustment]]

## Module References

- [[modules/time-off/overview|Time Off]]
- [[modules/calendar/overview|Calendar]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]] - Phase 2
- [[backend/notification-system|Notification System]]
