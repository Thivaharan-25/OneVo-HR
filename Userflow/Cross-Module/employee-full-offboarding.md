# Employee Full Offboarding — Cross-Module Chain

**Area:** Cross-Module Scenario  
**Trigger:** `Employee Offboarding Initiated` event from Employee Management  
**Required Permission(s):** `employees:write`, `payroll:write`, `leave:manage`, `attendance:manage`, `documents:manage`  
**Modules Involved:** Employee-Management, Auth-Access, Leave, Payroll, Documents, Workforce-Presence, Workforce-Intelligence

---

## Context

Employee offboarding is the reverse of onboarding — but more critical because it involves access revocation, final financial settlements, and data retention compliance. Missing a step here creates security risks (lingering access) or legal risks (unpaid balances).

## Preconditions

- Employee exists with status "Active" or "Notice Period"
- Offboarding reason documented (resignation, termination, contract end, retirement)
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

---

## Chain Reaction Flow

| Order | Module | What Happens | Triggered By | Event Published |
|:------|:-------|:-------------|:-------------|:----------------|
| 1 | **Employee-Management** | Offboarding initiated. Status → "Notice Period" or "Exiting". Last working day set. Offboarding checklist generated | Admin action | `EmployeeOffboardingStarted` |
| 2 | **Leave** | Remaining leave balance calculated. Pending leave requests auto-cancelled. Encashable balance flagged for payroll | `EmployeeOffboardingStarted` | `LeaveBalanceFinalised` |
| 3 | **Workforce-Presence** | Attendance records finalized up to last working day. Pending corrections auto-escalated. Shift schedule end-dated | `EmployeeOffboardingStarted` | `AttendanceFinalised` |
| 4 | **Payroll** | Final settlement calculated: last salary (pro-rated), leave encashment, pending reimbursements, deductions. Queued for next payroll run or immediate processing | `LeaveBalanceFinalised` + `AttendanceFinalised` | `FinalSettlementCalculated` |
| 5 | **Documents** | Exit interview form generated. Experience/relieving letter generated (pending approval). All employee-held company docs flagged for return | `EmployeeOffboardingStarted` | `ExitDocumentsPending` |
| 6 | **Workforce-Intelligence** | *(If monitoring was active)* Agent uninstall instructions sent. Monitoring data retained per retention policy. Activity data access revoked from managers | `EmployeeOffboardingStarted` | `MonitoringDeactivated` |
| 7 | **Auth-Access** | *(On last working day or immediate if terminated)* User account deactivated. All active sessions invalidated. SSO tokens revoked. API keys revoked | `EmployeeOffboardingStarted` + last working day reached | `UserAccountDeactivated` |

---

## Dependency Chain

```
Offboarding Initiated (Step 1)
├── Leave balance finalised (Step 2) — independent
├── Attendance finalised (Step 3) — independent
├── Final settlement (Step 4) — BLOCKED BY Steps 2 + 3
├── Exit documents (Step 5) — independent
├── Monitoring cleanup (Step 6) — independent
└── Access revocation (Step 7) — scheduled for last working day
```

**Critical:** Step 4 (final settlement) MUST wait for Steps 2 and 3 to complete. Payroll needs the final leave encashment amount and final attendance/overtime figures.

---

## What If a Step Fails?

| Failed Step | Impact | Recovery |
|:------------|:-------|:---------|
| Leave balance calculation fails | Final settlement will be incorrect | HR Admin manually calculates via [[Userflow/Leave/leave-balance-view\|Leave Balance View]] |
| Attendance finalization fails | Overtime/deductions in settlement may be wrong | Admin resolves pending corrections via [[Userflow/Workforce-Presence/attendance-correction\|Attendance Correction]] |
| Final settlement fails | Employee not paid correctly | HR reruns via [[Userflow/Payroll/payroll-adjustment\|Payroll Adjustment]] |
| Document generation fails | No relieving letter | Admin generates manually via [[Userflow/Documents/template-management\|Template Management]] |
| Access not revoked on time | **Security risk** — ex-employee retains access | Admin manually deactivates via user management. **This is the highest priority failure to catch** |

---

## Offboarding Checklist Items (Tracked in Workflow Engine)

- [ ] Offboarding reason and last working day confirmed (Employee-Management)
- [ ] Pending leave requests cancelled, balance finalized (Leave)
- [ ] Attendance records finalized through last working day (Workforce-Presence)
- [ ] Final settlement calculated and approved (Payroll)
- [ ] Exit interview completed (Documents)
- [ ] Relieving letter generated and signed (Documents)
- [ ] Company assets returned (laptop, badge, keys) *(external — tracked but not automated)*
- [ ] Monitoring agent uninstalled *(if applicable)* (Workforce-Intelligence)
- [ ] User account deactivated, sessions invalidated (Auth-Access)
- [ ] Employee status → "Inactive" (Employee-Management)

---

## Related Individual Flows

- [[Userflow/Employee-Management/employee-offboarding|Employee Offboarding]] — the initiating flow
- [[Userflow/Leave/leave-balance-view|Leave Balance View]] — balance calculation
- [[Userflow/Leave/leave-cancellation|Leave Cancellation]] — auto-cancellation of pending requests
- [[Userflow/Workforce-Presence/attendance-correction|Attendance Correction]] — finalizing records
- [[Userflow/Payroll/payroll-run-execution|Payroll Run Execution]] — final settlement processing
- [[Userflow/Payroll/payroll-adjustment|Payroll Adjustment]] — corrections to final pay
- [[Userflow/Documents/template-management|Template Management]] — relieving letter generation
- [[Userflow/Cross-Module/employee-full-onboarding|Employee Full Onboarding]] — the reverse chain

## Module References

- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- [[modules/leave/leave-entitlements/overview|Leave Entitlements]]
- [[modules/payroll/overview|Payroll]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- [[backend/messaging/event-catalog|Event Catalog]]
