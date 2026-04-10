# Disciplinary Action

**Area:** Grievance  
**Trigger:** HR Admin issues disciplinary action after investigation (user action — post-investigation)
**Required Permission(s):** `grievance:manage`  
**Related Permissions:** `employees:write` (record on profile)

---

## Preconditions

- Grievance investigated or performance issue documented → [[Userflow/Grievance/grievance-investigation|Grievance Investigation]], [[Userflow/Performance/improvement-plan|Improvement Plan]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Initiate Action
- **UI:** Grievance → case → "Issue Disciplinary Action" or Employee Profile → Actions → "Disciplinary Action"
- **API:** `POST /api/v1/grievance/disciplinary-actions`

### Step 2: Select Type
- **UI:** Select type: Verbal Warning, Written Warning, Final Warning, Suspension (with duration), Termination
- Enter details: specific violation, evidence reference, expected behavior change

### Step 3: Set Review Date
- **UI:** For warnings: set review date (30/60/90 days) → employee must show improvement by this date
- **Backend:** DisciplinaryService.IssueAsync() → [[modules/grievance/overview|Grievance]]
- **DB:** `disciplinary_actions` — linked to employee and case

### Step 4: Notify Employee
- **UI:** Employee notified → must acknowledge receipt → acknowledgement recorded
- **Backend:** Notification → [[backend/notification-system|Notification System]]

### Step 5: Record on Profile
- **Backend:** Action visible on employee's HR profile (restricted to `grievance:manage` viewers)

### Step 6: Follow-Up
- **If termination:** triggers [[Userflow/Employee-Management/employee-offboarding|Employee Offboarding]] automatically
- **If warning:** review at set date → either close or escalate to next level

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Active action exists | Warning | "Employee has an active warning — consider escalating" |
| Termination without approval | Requires confirmation | "Termination requires secondary approval from [HR Director]" |

## Events Triggered

- `DisciplinaryActionIssued` → [[backend/messaging/event-catalog|Event Catalog]]
- `EmployeeTerminated` (if termination) → [[backend/messaging/event-catalog|Event Catalog]]
- Notification to employee → [[backend/notification-system|Notification System]]

## Related Flows

- [[Userflow/Grievance/grievance-investigation|Grievance Investigation]]
- [[Userflow/Performance/improvement-plan|Improvement Plan]]
- [[Userflow/Employee-Management/employee-offboarding|Employee Offboarding]]

## Module References

- [[modules/grievance/overview|Grievance]]
- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
