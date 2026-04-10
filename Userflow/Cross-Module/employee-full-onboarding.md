# Employee Full Onboarding — Cross-Module Chain

**Area:** Cross-Module Scenario  
**Trigger:** `Employee Created` event from Employee Management  
**Required Permission(s):** `employees:write`, `payroll:write`, `leave:manage`, `attendance:manage`  
**Modules Involved:** Employee-Management, Auth-Access, Leave, Workforce-Presence, Payroll, Documents, Workforce-Intelligence

---

## Context

When a new employee is onboarded, the action doesn't stop at creating a profile. Multiple modules must react to set up the employee's full working environment. This doc tracks the **complete chain reaction** across all modules — so no step gets missed when any individual module changes.

## Preconditions

- Department and job family exist → [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]], [[Userflow/Org-Structure/job-family-setup|Job Family Setup]]
- Leave policies configured for employee's country/entity → [[Userflow/Leave/leave-policy-setup|Leave Policy Setup]]
- Shift schedules defined → [[Userflow/Workforce-Presence/shift-schedule-setup|Shift Schedule Setup]]
- Payroll provider configured → [[Userflow/Payroll/payroll-provider-setup|Payroll Provider Setup]]

---

## Chain Reaction Flow

| Order | Module | What Happens | Triggered By | Event Published |
|:------|:-------|:-------------|:-------------|:----------------|
| 1 | **Employee-Management** | Employee profile created, status set to "Onboarding" | Admin submits form | `EmployeeCreated`, `EmployeeOnboardingStarted` |
| 2 | **Auth-Access** | User account created with temporary password, invitation email sent | `EmployeeCreated` | `UserAccountCreated` |
| 3 | **Leave** | Leave entitlements auto-assigned based on employee's country, entity, and employment type. Pro-rated if mid-year start | `EmployeeCreated` | `LeaveEntitlementsAssigned` |
| 4 | **Workforce-Presence** | Default shift schedule assigned based on department/location. Work calendar initialized | `EmployeeCreated` | `ShiftScheduleAssigned` |
| 5 | **Payroll** | Salary structure created from compensation details entered during onboarding. Tax config applied based on country. Added to next payroll run | `EmployeeCreated` + compensation data | `PayrollProfileCreated` |
| 6 | **Documents** | Employment contract generated from template. Pending employee signature. Other required docs (NDA, handbook acknowledgement) queued | `EmployeeCreated` | `DocumentsPendingSignature` |
| 7 | **Workforce-Intelligence** | *(Only if monitoring enabled for tenant)* GDPR consent queued for employee's first login. Agent deployment instructions generated | `EmployeeCreated` + tenant monitoring config | `ConsentRequired` |

---

## Dependency Chain

```
Employee Created (Step 1)
├── Auth account (Step 2) — independent
├── Leave entitlements (Step 3) — independent
├── Shift schedule (Step 4) — independent
├── Payroll profile (Step 5) — needs compensation data from Step 1
├── Documents (Step 6) — needs employee details from Step 1
└── Monitoring consent (Step 7) — needs user account from Step 2
```

Steps 2-6 can run in parallel except Step 7 which depends on Step 2.

---

## What If a Step Fails?

| Failed Step | Impact | Recovery |
|:------------|:-------|:---------|
| Auth account creation fails | Employee cannot log in, but profile exists | Admin retries from employee profile → "Resend Invitation" |
| Leave entitlements not assigned | Employee sees 0 balance, cannot apply leave | HR Admin manually assigns via [[Userflow/Leave/leave-entitlement-assignment\|Leave Entitlement Assignment]] |
| Shift schedule not assigned | Employee not tracked in attendance | Admin assigns manually via [[Userflow/Workforce-Presence/shift-schedule-setup\|Shift Schedule Setup]] |
| Payroll profile missing | Employee excluded from next payroll run | HR Admin sets up via [[Userflow/Employee-Management/compensation-setup\|Compensation Setup]] |
| Document generation fails | Employee doesn't receive contract | Admin re-triggers from [[Userflow/Documents/template-management\|Template Management]] |
| Consent not queued | Monitoring cannot start for this employee | Auto-retries on next login; admin can trigger manually |

**Critical rule:** An employee can reach "Active" status even if Steps 3-7 partially fail. The onboarding checklist (Step 1) tracks completion of downstream setup. Employee status should NOT move to "Active" until all MUST steps are confirmed.

---

## Onboarding Checklist Items (Tracked in Workflow Engine)

These are the checklist items generated at Step 1 that track cross-module completion:

- [ ] User account created and invitation sent (Auth-Access)
- [ ] Employee sets password and completes profile (Auth-Access)
- [ ] Leave entitlements assigned (Leave)
- [ ] Shift schedule assigned (Workforce-Presence)
- [ ] Salary structure configured (Payroll)
- [ ] Employment contract signed (Documents)
- [ ] Required policy documents acknowledged (Documents)
- [ ] GDPR consent collected *(if monitoring enabled)* (Workforce-Intelligence)
- [ ] IT equipment provisioned *(external — tracked but not automated)*
- [ ] Manager welcome meeting scheduled *(external — tracked but not automated)*

---

## Related Individual Flows

- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]] — the initiating flow (Steps 1-2)
- [[Userflow/Auth-Access/user-invitation|User Invitation]] — account creation detail
- [[Userflow/Leave/leave-entitlement-assignment|Leave Entitlement Assignment]] — entitlement setup detail
- [[Userflow/Workforce-Presence/shift-schedule-setup|Shift Schedule Setup]] — schedule assignment detail
- [[Userflow/Employee-Management/compensation-setup|Compensation Setup]] — payroll setup detail
- [[Userflow/Documents/document-upload|Document Upload]] — contract generation detail
- [[Userflow/Auth-Access/gdpr-consent|GDPR Consent]] — consent collection detail
- [[Userflow/Cross-Module/employee-full-offboarding|Employee Full Offboarding]] — the reverse chain

## Module References

- [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- [[modules/core-hr/onboarding/overview|Onboarding]]
- [[modules/leave/leave-entitlements/overview|Leave Entitlements]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/notification-system|Notification System]]
