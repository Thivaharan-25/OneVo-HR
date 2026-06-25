# Employee Full Onboarding - Cross-Module Chain

**Area:** Cross-Module Scenario  
**Trigger:** `Employee Created` event from Employee Management  
**Required Permission(s):** `employees:write`, `payroll:write`, `time_off:manage`, `attendance:write`  
**Modules Involved:** Employee-Management, Auth-Access, Time Off, Time & Attendance, Payroll, Documents, Monitoring

---

## Context

When a new employee is onboarded, the action doesn't stop at creating a profile. Multiple modules must react to set up the employee's full working environment. This doc tracks the **complete chain reaction** across all modules - so no step gets missed when any individual module changes.

## Preconditions

- Department and target position exist -> [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]], [[Userflow/Org-Structure/position-setup|Position Setup]]
- Time Off policies configured for employee's country/entity -> [[Userflow/Time-Off/time-off-policy-setup|Time Off Policy Setup]]
- Shift schedules defined -> [[Userflow/Time-Attendance/shift-schedule-setup|Shift Schedule Setup]]
- Payroll provider configured -> [[Userflow/Payroll/payroll-provider-setup|Payroll Provider Setup]]

---

## Chain Reaction Flow

| Order | Module | What Happens | Triggered By | Event Published |
|:------|:-------|:-------------|:-------------|:----------------|
| 1 | **Employee-Management** | Employee profile created, status set to "Onboarding" | Admin submits form | `EmployeeCreated`, `EmployeeOnboardingStarted` |
| 2 | **Auth-Access** | User account created and email invitation sent; employee completes password setup or uses SSO if enabled | `EmployeeCreated` | `UserAccountCreated` |
| 3 | **Time Off** | Time Off entitlements auto-assigned based on employee's country, entity, and employment type. Pro-rated if mid-year start | `EmployeeCreated` | `TimeOffEntitlementsAssigned` |
| 4 | **Time-Attendance** | Default shift schedule assigned based on department/location. Work calendar initialized | `EmployeeCreated` | `ShiftScheduleAssigned` |
| 5 | **Payroll** | Salary structure created from compensation details entered during onboarding. Tax config applied based on country. Added to next payroll run | `EmployeeCreated` + compensation data | `PayrollProfileCreated` |
| 6 | **Documents** | Employment contract generated from template. Pending employee signature. Other required docs (NDA, handbook acknowledgement) queued | `EmployeeCreated` | `DocumentsPendingSignature` |
| 7 | **Monitoring** | *(Only if monitoring enabled for tenant)* Required Legal & Privacy monitoring/screenshot/biometric items queued for invite acceptance or first login. Agent deployment instructions generated | `EmployeeCreated` + tenant monitoring config | `LegalPrivacyRequired` |

---

## Dependency Chain

```
Employee Created (Step 1)
+-- Auth account (Step 2) - independent
+-- Time Off entitlements (Step 3) - independent
+-- Shift schedule (Step 4) - independent
+-- Payroll profile (Step 5) - needs compensation data from Step 1
+-- Documents (Step 6) - needs employee details from Step 1
+-- Legal & Privacy monitoring gate (Step 7) - needs user account from Step 2
```

Steps 2-6 can run in parallel except Step 7 which depends on Step 2.

---

## What If a Step Fails?

| Failed Step | Impact | Recovery |
|:------------|:-------|:---------|
| Auth account creation fails | Employee cannot log in, but profile exists | Admin retries from employee profile -> "Resend Invitation" |
| Time Off entitlements not assigned | Employee sees 0 balance and cannot apply Time Off | Authorized Time Off management user manually assigns via [[Userflow/Time-Off/time-off-entitlement-assignment\|Time Off Entitlement Assignment]] |
| Shift schedule not assigned | Employee not tracked in attendance | Admin assigns manually via [[Userflow/Time-Attendance/shift-schedule-setup\|Shift Schedule Setup]] |
| Payroll profile missing | Employee excluded from next payroll run | Authorized compensation-management user sets up via [[Userflow/Employee-Management/compensation-setup\|Compensation Setup]] |
| Document generation fails | Employee doesn't receive contract | Admin re-triggers from [[Userflow/Documents/template-management\|Template Management]] |
| Legal & Privacy item not queued | Affected monitoring collection cannot start for this employee | Auto-retries on invite acceptance, next login, or agent startup; admin can trigger manually |

**Critical rule:** An employee can reach "Active" status even if Steps 3-7 partially fail. The onboarding checklist (Step 1) tracks completion of downstream setup. Employee status should NOT move to "Active" until all MUST steps are confirmed.

---

## Onboarding Checklist Items (Phase 1 checklist tasks; Workflow Engine Phase 2)

These are the checklist items generated at Step 1 that track cross-module completion:

- [ ] User account created and invitation sent (Auth-Access)
- [ ] Employee sets password and completes profile (Auth-Access)
- [ ] Time Off entitlements assigned (Time Off)
- [ ] Shift schedule assigned (Time-Attendance)
- [ ] Salary structure configured (Payroll)
- [ ] Employment contract signed (Documents)
- [ ] Required policy documents acknowledged (Documents)
- [ ] Required Legal & Privacy items completed *(if monitoring/screenshot/biometric enabled)* (Monitoring)
- [ ] IT equipment provisioned *(external - tracked but not automated)*
- [ ] Manager welcome meeting scheduled *(external - tracked but not automated)*

---

## Related Individual Flows

- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]] - the initiating flow (Steps 1-2)
- [[Userflow/Auth-Access/user-invitation|User Invitation]] - account creation detail
- [[Userflow/Time-Off/time-off-entitlement-assignment|Time Off Entitlement Assignment]] - entitlement setup detail
- [[Userflow/Time-Attendance/shift-schedule-setup|Shift Schedule Setup]] - schedule assignment detail
- [[Userflow/Employee-Management/compensation-setup|Compensation Setup]] - payroll setup detail
- [[Userflow/Documents/document-upload|Document Upload]] - contract generation detail
- [[Userflow/Auth-Access/gdpr-consent|Legal & Privacy Acceptance]] - terms, notices, and consent detail
- [[Userflow/Cross-Module/employee-full-offboarding|Employee Full Offboarding]] - the reverse chain

## Module References

- [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- [[modules/core-hr/onboarding/overview|Onboarding]]
- [[modules/time-off/time-off-entitlements/overview|Time Off Entitlements]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine (Phase 2)]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/notification-system|Notification System]]
