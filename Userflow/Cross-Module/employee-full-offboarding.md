# Employee Full Offboarding - Cross-Module Chain

**Area:** Cross-Module Scenario  
**Trigger:** `Employee Offboarding Initiated` event from Employee Management  
**Required Permission(s):** `employees:write`, `payroll:write`, `time_off:manage`, `attendance:write`, `documents:manage`  
**Modules Involved:** Employee-Management, Auth-Access, Time Off, Payroll, Documents, Time & Attendance, Monitoring

---

## Context

Employee offboarding is the reverse of onboarding - but more critical because it involves access revocation, final financial settlements, and data retention compliance. Missing a step here creates security risks (lingering access) or legal risks (unpaid balances).

## Preconditions

- Employee exists with status "Active" or "Notice Period"
- Offboarding reason documented (resignation, termination, contract end, retirement)
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

---

## Chain Reaction Flow

| Order | Module | What Happens | Triggered By | Event Published |
|:------|:-------|:-------------|:-------------|:----------------|
| 1 | **Employee-Management** | Offboarding initiated. Status -> "Notice Period" or "Exiting". Last working day set. Offboarding checklist generated | Admin action | `EmployeeOffboardingStarted` |
| 2 | **Time Off** | Remaining Time Off balance calculated. Pending Time Off requests auto-cancelled. Encashable balance flagged for payroll | `EmployeeOffboardingStarted` | `TimeOffBalanceFinalised` |
| 3 | **Time-Attendance** | Attendance records finalized up to last working day. Pending corrections auto-escalated. Shift schedule end-dated | `EmployeeOffboardingStarted` | `AttendanceFinalised` |
| 4 | **Payroll** | Final settlement calculated: last salary (pro-rated), Time Off encashment, pending reimbursements, deductions. Queued for next payroll run or immediate processing | `TimeOffBalanceFinalised` + `AttendanceFinalised` | `FinalSettlementCalculated` |
| 5 | **Documents** | Exit interview form generated. Experience/relieving letter generated (pending approval). All employee-held company docs flagged for return | `EmployeeOffboardingStarted` | `ExitDocumentsPending` |
| 6 | **Monitoring** | *(If monitoring was active)* Agent uninstall instructions sent. Monitoring data retained per retention policy. Activity data access revoked from managers | `EmployeeOffboardingStarted` | `MonitoringDeactivated` |
| 7 | **Auth-Access** | *(On last working day or immediate if terminated)* User account deactivated. All active sessions invalidated. SSO tokens revoked. API keys revoked | `EmployeeOffboardingStarted` + last working day reached | `UserAccountDeactivated` |

---

## Dependency Chain

```
Offboarding Initiated (Step 1)
+-- Time Off balance finalised (Step 2) - independent
+-- Attendance finalised (Step 3) - independent
+-- Final settlement (Step 4) - BLOCKED BY Steps 2 + 3
+-- Exit documents (Step 5) - independent
+-- Monitoring cleanup (Step 6) - independent
+-- Access revocation (Step 7) - scheduled for last working day
```

**Critical:** Step 4 (final settlement) MUST wait for Steps 2 and 3 to complete. Payroll needs the final Time Off encashment amount and final attendance/overtime figures.

---

## What If a Step Fails?

| Failed Step | Impact | Recovery |
|:------------|:-------|:---------|
| Time Off balance calculation fails | Final settlement will be incorrect | Authorized Time Off management user manually calculates via [[Userflow/Time-Off/time-off-balance-view\|Time Off Balance View]] |
| Attendance finalization fails | Overtime/deductions in settlement may be wrong | Admin resolves pending corrections via [[Userflow/Time-Attendance/attendance-correction\|Attendance Correction]] |
| Final settlement fails | Employee not paid correctly | HR reruns via [[Userflow/Payroll/payroll-adjustment\|Payroll Adjustment]] |
| Document generation fails | No relieving letter | Admin generates manually via [[Userflow/Documents/template-management\|Template Management]] |
| Access not revoked on time | **Security risk** - ex-employee retains access | Admin manually deactivates via user management. **This is the highest priority failure to catch** |

---

## Offboarding Checklist Items (Phase 1 checklist tasks; Workflow Engine Phase 2)

- [ ] Offboarding reason and last working day confirmed (Employee-Management)
- [ ] Pending Time Off requests cancelled, balance finalized (Time Off)
- [ ] Attendance records finalized through last working day (Time-Attendance)
- [ ] Final settlement calculated and approved (Payroll)
- [ ] Exit interview completed (Documents)
- [ ] Relieving letter generated and signed (Documents)
- [ ] Company assets returned (laptop, badge, keys) *(external - tracked but not automated)*
- [ ] Monitoring agent uninstalled *(if applicable)* (Monitoring)
- [ ] User account deactivated, sessions invalidated (Auth-Access)
- [ ] Employee status -> "Inactive" (Employee-Management)

---

## Related Individual Flows

- [[Userflow/Employee-Management/employee-offboarding|Employee Offboarding]] - the initiating flow
- [[Userflow/Time-Off/time-off-balance-view|Time Off Balance View]] - balance calculation
- [[Userflow/Time-Off/time-off-cancellation|Time Off Cancellation]] - auto-cancellation of pending requests
- [[Userflow/Time-Attendance/attendance-correction|Attendance Correction]] - finalizing records
- [[Userflow/Payroll/payroll-run-execution|Payroll Run Execution]] - final settlement processing
- [[Userflow/Payroll/payroll-adjustment|Payroll Adjustment]] - corrections to final pay
- [[Userflow/Documents/template-management|Template Management]] - relieving letter generation
- [[Userflow/Cross-Module/employee-full-onboarding|Employee Full Onboarding]] - the reverse chain

## Module References

- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- [[modules/time-off/time-off-entitlements/overview|Time Off Entitlements]]
- [[modules/payroll/overview|Payroll]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine (Phase 2)]]
- [[backend/messaging/event-catalog|Event Catalog]]
