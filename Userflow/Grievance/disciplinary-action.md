# Disciplinary Action

**Area:** Grievance  
**Required Permission(s):** `grievance:manage`  
**Related Permissions:** `employees:write` (record on profile)

---

## Preconditions

- Grievance investigated or performance issue documented → [[grievance-investigation]], [[improvement-plan]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Initiate Action
- **UI:** Grievance → case → "Issue Disciplinary Action" or Employee Profile → Actions → "Disciplinary Action"
- **API:** `POST /api/v1/grievance/disciplinary-actions`

### Step 2: Select Type
- **UI:** Select type: Verbal Warning, Written Warning, Final Warning, Suspension (with duration), Termination
- Enter details: specific violation, evidence reference, expected behavior change

### Step 3: Set Review Date
- **UI:** For warnings: set review date (30/60/90 days) → employee must show improvement by this date
- **Backend:** DisciplinaryService.IssueAsync() → [[grievance]]
- **DB:** `disciplinary_actions` — linked to employee and case

### Step 4: Notify Employee
- **UI:** Employee notified → must acknowledge receipt → acknowledgement recorded
- **Backend:** Notification → [[notification-system]]

### Step 5: Record on Profile
- **Backend:** Action visible on employee's HR profile (restricted to `grievance:manage` viewers)

### Step 6: Follow-Up
- **If termination:** triggers [[employee-offboarding]] automatically
- **If warning:** review at set date → either close or escalate to next level

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Active action exists | Warning | "Employee has an active warning — consider escalating" |
| Termination without approval | Requires confirmation | "Termination requires secondary approval from [HR Director]" |

## Events Triggered

- `DisciplinaryActionIssued` → [[event-catalog]]
- `EmployeeTerminated` (if termination) → [[event-catalog]]
- Notification to employee → [[notification-system]]

## Related Flows

- [[grievance-investigation]]
- [[improvement-plan]]
- [[employee-offboarding]]

## Module References

- [[grievance]]
- [[employee-lifecycle]]
