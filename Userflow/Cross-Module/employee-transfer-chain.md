# Employee Transfer — Cross-Module Chain

**Area:** Cross-Module Scenario  
**Trigger:** HR Admin or Manager initiates department/team/location transfer (user action)  
**Required Permission(s):** `employees:write`, `org:manage`, `attendance:manage`, `leave:manage`  
**Modules Involved:** Employee-Management, Org-Structure, Workforce-Presence, Leave, Payroll, Auth-Access, Notifications

---

## Context

Transferring an employee isn't just updating a department field. It can change their reporting line (affecting approvals), shift schedule, leave policy (if changing country/entity), payroll tax rules, cost center allocation, and access permissions. This doc ensures nothing gets missed during a transfer.

## Preconditions

- Target department/team exists → [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]], [[Userflow/Org-Structure/team-creation|Team Creation]]
- Target position has capacity (if headcount tracking enabled)
- Transfer effective date set (can be future-dated)

---

## Chain Reaction Flow

| Order | Module | What Happens | Triggered By | Event Published |
|:------|:-------|:-------------|:-------------|:----------------|
| 1 | **Employee-Management** | Transfer record created: old dept/team → new dept/team, effective date, reason. Employee status temporarily set to "Transferring" | HR Admin submits transfer | `EmployeeTransferInitiated` |
| 2 | **Org-Structure** | Reporting line updated: old manager removed, new manager assigned. Org chart reflects change on effective date | `EmployeeTransferInitiated` | `ReportingLineChanged` |
| 3 | **Auth-Access** | Approval routing updated: new manager becomes approver for leave, expense, attendance. Old manager loses approval authority for this employee | `ReportingLineChanged` | `ApprovalRoutingUpdated` |
| 4 | **Workforce-Presence** | Shift schedule reassigned if new department has different shift pattern. Old schedule ends on transfer date, new schedule starts | `EmployeeTransferInitiated` | `ShiftScheduleReassigned` |
| 5 | **Leave** | If transferring to different entity/country: leave policy re-evaluated. Balance may be recalculated (carry-over rules). If same entity: no change | `EmployeeTransferInitiated` + location change flag | `LeavePolicyReassigned` (if applicable) |
| 6 | **Payroll** | Cost center allocation updated. If cross-country transfer: tax rules updated, salary may be restructured for new jurisdiction | `EmployeeTransferInitiated` | `PayrollAllocationUpdated` |
| 7 | **Notifications** | Old manager notified (team member leaving). New manager notified (team member joining). Employee notified of transfer details | `EmployeeTransferInitiated` | `NotificationSent` |
| 8 | **Employee-Management** | On effective date: transfer completed, employee status returns to "Active" under new department | Scheduled on effective date | `EmployeeTransferCompleted` |

---

## Dependency Chain

```
Transfer Initiated (Step 1)
├── Reporting line update (Step 2) — independent
│   └── Approval routing (Step 3) — needs Step 2
├── Shift reassignment (Step 4) — independent
├── Leave policy check (Step 5) — independent
├── Payroll allocation (Step 6) — independent
├── Notifications (Step 7) — independent
│
Effective Date Reached (Step 8) — scheduled, runs after all above
```

---

## What If a Step Fails?

| Failed Step | Impact | Recovery |
|:------------|:-------|:---------|
| Reporting line not updated | Old manager still receives approvals for transferred employee | HR Admin manually updates via Org-Structure |
| Approval routing stale | Leave/expense requests go to wrong manager | System detects on next approval attempt; HR corrects |
| Shift schedule not reassigned | Employee tracked against old shift | Admin assigns manually via [[Userflow/Workforce-Presence/shift-schedule-setup\|Shift Schedule Setup]] |
| Leave policy not re-evaluated | Employee may have wrong entitlements for new location | HR manually reassigns via [[Userflow/Leave/leave-entitlement-assignment\|Leave Entitlement Assignment]] |
| Payroll allocation not updated | Salary charged to old cost center | Finance corrects via [[Userflow/Payroll/payroll-adjustment\|Payroll Adjustment]] |

---

## Special Cases

### Cross-Country Transfer
- Triggers additional steps: tax re-registration, benefits re-enrollment, new employment contract generation
- May require offboarding from old entity and onboarding into new entity (two separate employment records)
- Links to: [[Userflow/Cross-Module/employee-full-offboarding|Offboarding]] + [[Userflow/Cross-Module/employee-full-onboarding|Onboarding]]

### Future-Dated Transfer
- All changes are staged but not applied until effective date
- Approval routing stays with old manager until effective date
- Employee's current view shows "Transfer pending" badge

---

## Related Individual Flows

- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]] — detailed transfer form and process
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]] — often paired with transfer
- [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]] — org structure changes
- [[Userflow/Workforce-Presence/shift-schedule-setup|Shift Schedule Setup]] — schedule reassignment
- [[Userflow/Leave/leave-entitlement-assignment|Leave Entitlement Assignment]] — policy changes
- [[Userflow/Payroll/payroll-adjustment|Payroll Adjustment]] — cost center corrections

## Module References

- [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- [[modules/org-structure/overview|Org Structure]]
- [[modules/leave/overview|Leave]]
- [[modules/workforce-presence/overview|Workforce Presence]]
- [[modules/payroll/overview|Payroll]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/notification-system|Notification System]]
