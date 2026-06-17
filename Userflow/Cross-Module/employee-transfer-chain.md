# Employee Transfer â€” Cross-Module Chain

**Area:** Cross-Module Scenario  
**Trigger:** Authorized employee-management user or position-resolved manager initiates an assignment or legal entity transfer (user action)  
**Required Permission(s):** `employees:write`, `org:manage`, `attendance:write`, `leave:manage`  
**Modules Involved:** Employee-Management, Org-Structure, Workforce-Presence, Leave, Payroll, Auth-Access, Notifications

---

## Context

Transferring an employee isn't just updating a department field. It can change their legal entity, reporting line, position, shift schedule, leave policy, payroll/legal context where enabled, and access permissions. Team membership changes are handled separately through Org Structure > Teams.

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
| 3 | **Auth-Access** | Position-linked access impact is applied after admin confirmation. Approval routing updated: new position-resolved manager becomes approver for leave, expense, attendance. Old position-resolved manager loses approval authority for this employee | `ReportingLineChanged` | `ApprovalRoutingUpdated` |
| 4 | **Workforce-Presence** | Shift schedule reassigned if new department has different shift pattern. Old schedule ends on transfer date, new schedule starts | `EmployeeTransferInitiated` | `ShiftScheduleReassigned` |
| 5 | **Leave** | If transferring to a different legal entity/country: leave policy re-evaluated. Balance may be recalculated (carry-over rules). If same legal entity: no change | `EmployeeTransferInitiated` + legal entity change flag | `LeavePolicyReassigned` (if applicable) |
| 6 | **Payroll** | If payroll is enabled and the legal entity changes, payroll/legal context is re-evaluated for the new jurisdiction | `EmployeeTransferInitiated` | `PayrollAllocationUpdated` |
| 7 | **Notifications** | Old position-resolved manager notified. New position-resolved manager notified. Employee notified of transfer details | `EmployeeTransferInitiated` | `NotificationSent` |
| 8 | **Employee-Management** | On effective date: transfer completed, old assignment history row closes, new assignment history row is created, and employee status returns to "Active" | Scheduled on effective date | `EmployeeTransferCompleted` |

---

## Dependency Chain

```
Transfer Initiated (Step 1)
â”œâ”€â”€ Position reporting update (Step 2) â€” independent
â”‚   â””â”€â”€ Approval routing (Step 3) â€” needs Step 2
â”œâ”€â”€ Shift reassignment (Step 4) â€” independent
â”œâ”€â”€ Leave policy check (Step 5) â€” independent
â”œâ”€â”€ Payroll allocation (Step 6) â€” independent
â”œâ”€â”€ Notifications (Step 7) â€” independent
â”‚
Effective Date Reached (Step 8) â€” scheduled, runs after all above
```

---

## What If a Step Fails?

| Failed Step | Impact | Recovery |
|:------------|:-------|:---------|
| Position reporting context not updated | Old position-resolved manager still receives approvals for transferred employee | Authorized org-management user manually updates via Org Structure |
| Approval routing stale | Leave/expense requests go to wrong position-resolved manager | System detects on next approval attempt; authorized workflow or org-management user corrects |
| Shift schedule not reassigned | Employee tracked against old shift | Admin assigns manually via [[Userflow/Workforce-Presence/shift-schedule-setup\|Shift Schedule Setup]] |
| Leave policy not re-evaluated | Employee may have wrong entitlements for new legal entity | Authorized leave-management user manually reassigns via [[Userflow/Leave/leave-entitlement-assignment\|Leave Entitlement Assignment]] |
| Payroll context not updated | Payroll may use old legal entity context | Finance corrects via [[Userflow/Payroll/payroll-adjustment\|Payroll Adjustment]] |

---

## Special Cases

### Legal Entity / Country Transfer
- Triggers additional review: leave policy, attendance policy, payroll/legal context where enabled, and access impact.
- Uses a new legal-entity-scoped position assignment inside the same tenant.
- Does not allow the target position to report to a position in another legal entity.

### Future-Dated Transfer
- All changes are staged but not applied until effective date
- Approval routing stays with the old position-resolved manager until effective date
- Employee's current view shows "Transfer pending" badge

---

## Related Individual Flows

- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]] â€” detailed transfer form and process
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]] â€” often paired with transfer
- [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]] â€” org structure changes
- [[Userflow/Workforce-Presence/shift-schedule-setup|Shift Schedule Setup]] â€” schedule reassignment
- [[Userflow/Leave/leave-entitlement-assignment|Leave Entitlement Assignment]] â€” policy changes
- [[Userflow/Payroll/payroll-adjustment|Payroll Adjustment]] â€” cost center corrections

## Module References

- [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- [[modules/org-structure/overview|Org Structure]]
- [[modules/leave/overview|Leave]]
- [[modules/workforce-presence/overview|Workforce Presence]]
- [[modules/payroll/overview|Payroll]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/notification-system|Notification System]]
