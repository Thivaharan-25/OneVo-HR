# Attendance Dispute & Correction - Cross-Module Chain

**Area:** Cross-Module Scenario  
**Trigger:** Employee notices incorrect attendance record (user action) or Exception Engine flags anomaly (system-triggered)  
**Required Permission(s):** `attendance:write` (employee), `attendance:approve` (manager), `monitoring:alerts:read` (reviewer)  
**Modules Involved:** Time-Attendance, Exception-Engine, Payroll, Notifications, Workflow Engine (Phase 2)

---

## Context

An attendance dispute doesn't stay within Time & Attendance. It may originate from a lightweight monitoring/attendance alert, require Phase 1 module approval, and ultimately affect payroll calculations. This doc tracks both paths - employee-initiated correction and system-detected anomaly. Workflow Engine approval is Phase 2 only.

## Preconditions

- Employee has an active shift schedule -> [[Userflow/Time-Attendance/shift-schedule-setup|Shift Schedule Setup]]
- Attendance records exist for the disputed period
- Exception rules configured (for system-detected path) -> [[Userflow/Exception-Engine/exception-rule-setup|Exception Rule Setup]]

---

## Path A: Employee-Initiated Correction

| Order | Module | What Happens | Triggered By | Event Published |
|:------|:-------|:-------------|:-------------|:----------------|
| 1 | **Time-Attendance** | Employee views attendance log, identifies incorrect record (missed clock-out, wrong hours, missing entry) | Employee reviews own attendance | - |
| 2 | **Time-Attendance** | Employee submits correction request with reason and evidence (e.g., "was in a meeting, forgot to clock in") | Employee submits form | `AttendanceCorrectionRequested` |
| 3 | **Notifications** | Configured attendance-correction resolver notified of pending correction request | `AttendanceCorrectionRequested` | `NotificationSent` |
| 4 | **Time-Attendance** | Phase 1 lightweight attendance-correction request is routed through Org Structure management coverage to one eligible owner. Phase 2 may use configured Workflow Engine resolvers. | `AttendanceCorrectionRequested` | `AttendanceCorrectionApprovalAssigned` |
| 5 | **Time-Attendance** | Configured approver approves -> attendance record updated with corrected times | Configured approver approves | `AttendanceCorrectionApproved` |
| 6 | **Payroll** | If correction affects hours worked or overtime, payroll adjustment flagged for next run | `AttendanceCorrectionApproved` | `PayrollAdjustmentFlagged` |
| 7 | **Exception-Engine** | If this record had triggered an alert, alert auto-resolved | `AttendanceCorrectionApproved` | `ExceptionResolved` |

## Path B: System-Detected Anomaly

| Order | Module | What Happens | Triggered By | Event Published |
|:------|:-------|:-------------|:-------------|:----------------|
| 1 | **Exception-Engine** | Anomaly detected: e.g., employee clocked in but no activity for 4+ hours, or clock-in from unusual location | Scheduled anomaly scan | `ExceptionRaised` |
| 2 | **Notifications** | Alert sent to configured resolver outputs via escalation chain | `ExceptionRaised` | `NotificationSent` |
| 3 | **Exception-Engine** | Reviewer investigates: views attendance data, activity snapshots, employee's response | Reviewer opens alert | - |
| 4a | **Exception-Engine** | Alert dismissed as false positive -> alert status set to `dismissed` | Reviewer dismisses | `ExceptionDismissed` |
| 4b | **Time-Attendance** | Reviewer initiates correction on employee's behalf -> same flow as Path A Step 2 onwards | Reviewer submits correction | `AttendanceCorrectionRequested` |
| 4c | **Exception-Engine** | Alert escalated through the configured resolver for further investigation | Reviewer escalates | `ExceptionEscalated` |

---

## Dependency Chain

```
Path A: Employee-Initiated
Correction Request (Step 2)
+-- Owner notification (Step 3) - independent
+-- Approval assignment (Step 4) - independent
|
Correction Approved (Step 5)
+-- Payroll adjustment flag (Step 6) - independent
+-- Exception auto-resolve (Step 7) - independent

Path B: System-Detected
Exception Raised (Step 1)
+-- Alert notification (Step 2) - independent
|
Investigation (Step 3)
+-- Dismiss (Step 4a) - terminal
+-- Correct (Step 4b) -> joins Path A at Step 2
+-- Escalate (Step 4c) -> new investigation cycle
```

---

## What If a Step Fails?

| Failed Step | Impact | Recovery |
|:------------|:-------|:---------|
| Correction request not saved | Employee must re-submit | Retry; if persistent, authorized attendance-management user submits on behalf |
| Approver notification fails | Correction sits pending | Retry; visible in the configured approver's queue |
| Payroll adjustment not flagged | Hours/overtime calculated on uncorrected data | Authorized payroll user applies [[Userflow/Payroll/payroll-adjustment\|Payroll Adjustment]] manually |
| Exception auto-resolve fails | Alert stays open after correction | Reviewer manually dismisses alert |

---

## Related Individual Flows

- [[Userflow/Time-Attendance/attendance-correction|Attendance Correction]] - detailed correction flow
- [[Userflow/Time-Attendance/overtime-management|Overtime Management]] - overtime recalculation
- [[Userflow/Exception-Engine/alert-review|Alert Review]] - exception investigation detail
- [[Userflow/Exception-Engine/escalation-chain-setup|Escalation Chain Setup]] - escalation configuration
- [[Userflow/Payroll/payroll-adjustment|Payroll Adjustment]] - payroll impact correction

## Module References

- [[modules/time-attendance/overview|Time & Attendance]]
- [[modules/exception-engine/overview|Exception Engine]]
- [[modules/payroll/overview|Payroll]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine (Phase 2)]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/notification-system|Notification System]]
