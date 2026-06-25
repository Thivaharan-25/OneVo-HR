# Employee Transfer - Cross-Module Chain

**Area:** Cross-Module Scenario  
**Trigger:** Authorized employee-management user initiates an assignment or legal entity transfer (user action)  
**Required Permission(s):** `employees:write`, `org:manage`, `attendance:write`, `time_off:manage`  
**Modules Involved:** Employee-Management, Org-Structure, Time & Attendance, Time Off, Payroll, Auth-Access, Notifications

---

## Context


## Preconditions

- Target legal entity exists when changing company.
- Target position exists inside the selected legal entity; department is derived from the position -> [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- Position occupancy capacity must be validated for the target position; broader headcount planning remains out of scope unless a future headcount-planning module is enabled
- Target position must not report to a position in another legal entity.
- Transfer effective date set (can be future-dated)

---

## Chain Reaction Flow

| Order | Module | What Happens | Triggered By | Event Published |
|:------|:-------|:-------------|:-------------|:----------------|
| 1 | **Employee-Management** | Transfer record created with old/new legal entity where applicable, old/new position, derived department snapshots, effective date, and reason. Employee status temporarily set to "Transferring" | Authorized employee-management user submits transfer | `EmployeeTransferInitiated` |
| 2 | **Org-Structure** | Position assignment and derived reporting context updated. Org chart reflects change on effective date | `EmployeeTransferInitiated` | `ReportingLineChanged` |
| 3 | **Auth-Access** | Position-linked access impact is applied after authorized confirmation or `access_grant_requests` approval. Employee visibility and approval routing are recalculated from management coverage for the new assignment | `ReportingLineChanged` | `ApprovalRoutingUpdated` |
| 4 | **Time-Attendance** | Shift schedule reassigned if new department has different shift pattern. Old schedule ends on transfer date, new schedule starts | `EmployeeTransferInitiated` | `ShiftScheduleReassigned` |
| 5 | **Time Off** | If transferring to a different legal entity/country: Time Off policy re-evaluated. Balance may be recalculated (carry-over rules). If same legal entity: no change | `EmployeeTransferInitiated` + legal entity change flag | `TimeOffPolicyReassigned` (if applicable) |
| 6 | **Payroll** | If payroll is enabled and the legal entity changes, payroll/legal context is re-evaluated for the new jurisdiction | `EmployeeTransferInitiated` | `PayrollAllocationUpdated` |
| 7 | **Notifications** | Relevant old/new coverage owners are notified where their pending work or visibility changes. Employee is notified of transfer details | `EmployeeTransferInitiated` | `NotificationSent` |
| 8 | **Employee-Management** | On effective date: transfer completed, old assignment history row closes, new assignment history row is created, and employee status returns to "Active" | Scheduled on effective date | `EmployeeTransferCompleted` |

---

## Dependency Chain

```
Transfer Initiated (Step 1)
+-- Position reporting update (Step 2) - independent
|   +-- Management coverage recalculation (Step 3) - needs Step 2
+-- Shift reassignment (Step 4) - independent
+-- Time Off policy check (Step 5) - independent
+-- Payroll allocation (Step 6) - independent
+-- Notifications (Step 7) - independent
|
Effective Date Reached (Step 8) - scheduled, runs after all above
```

---

## What If a Step Fails?

| Failed Step | Impact | Recovery |
|:------------|:-------|:---------|
| Position reporting context not updated | Org chart/reporting view is stale for the transferred employee | Authorized org-management user manually updates via Org Structure |
| Approval routing stale | Requests may resolve to the wrong coverage owner | System detects on next approval attempt; authorized org-management or access-authority user corrects |
| Shift schedule not reassigned | Employee tracked against old shift | Admin assigns manually via [[Userflow/Time-Attendance/shift-schedule-setup\|Shift Schedule Setup]] |
| Time Off policy not re-evaluated | Employee may have wrong entitlements for new legal entity | Authorized Time Off management user manually reassigns via [[Userflow/Time-Off/time-off-entitlement-assignment\|Time Off Entitlement Assignment]] |
| Payroll context not updated | Payroll may use old legal entity context | Finance corrects via [[Userflow/Payroll/payroll-adjustment\|Payroll Adjustment]] |

---

## Special Cases

### Legal Entity / Country Transfer
- Triggers additional review: Time Off policy, attendance policy, payroll/legal context where enabled, and access impact.
- Uses a new legal-entity-scoped position assignment inside the same tenant.
- Does not allow the target position to report to a position in another legal entity.
- If this creates a new Primary Employment Assignment, old primary assignment closes and policies re-evaluate from the new primary assignment.
- Additional Authority Assignments can cross legal entities but do not change policy inheritance.

### Future-Dated Transfer
- All changes are staged but not applied until effective date
- Approval routing continues to use the current effective assignment until the transfer effective date
- Employee's current view shows "Transfer pending" badge

---

## Related Individual Flows

- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]] - detailed transfer form and process
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]] - often paired with transfer
- [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]] - org structure changes
- [[Userflow/Time-Attendance/shift-schedule-setup|Shift Schedule Setup]] - schedule reassignment
- [[Userflow/Time-Off/time-off-entitlement-assignment|Time Off Entitlement Assignment]] - policy changes

## Module References

- [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- [[modules/org-structure/overview|Org Structure]]
- [[modules/time-off/overview|Time Off]]
- [[modules/time-attendance/overview|Time & Attendance]]
- [[modules/payroll/overview|Payroll]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/notification-system|Notification System]]
