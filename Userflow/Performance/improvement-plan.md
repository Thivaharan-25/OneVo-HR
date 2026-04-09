# Performance Improvement Plan (PIP)

**Area:** Performance  
**Required Permission(s):** `performance:manage`  
**Related Permissions:** `employees:write` (update employee record)

---

## Preconditions

- Employee has received below-standard review → [[Userflow/Performance/manager-review|Manager Review]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Create PIP
- **UI:** Employee Profile → Performance → "Create Improvement Plan" → set duration (30/60/90 days)
- **API:** `POST /api/v1/performance/improvement-plans`

### Step 2: Define Improvement Areas
- **UI:** Add specific improvement areas → set measurable targets for each → set check-in schedule (weekly/bi-weekly)
- **Backend:** ImprovementPlanService.CreateAsync() → [[modules/performance/improvement-plans/overview|Improvement Plans]]
- **DB:** `improvement_plans`, `improvement_plan_goals`

### Step 3: Assign Support
- **UI:** Assign mentor/coach → set meeting schedule → employee and mentor notified

### Step 4: Track Progress
- **UI:** Regular check-ins → manager records observations → updates progress per improvement area → employee can add self-notes
- **API:** `POST /api/v1/performance/improvement-plans/{id}/check-ins`

### Step 5: Evaluate at End
- **UI:** At plan end date → manager evaluates: "Targets Met" (close PIP, positive record) or "Partially Met" (extend) or "Not Met" (escalate to disciplinary)
- **API:** `PUT /api/v1/performance/improvement-plans/{id}/evaluate`

## Variations

### Extension
- If partially met → extend PIP with revised targets → new end date

### Escalation to disciplinary
- If not met → can trigger [[Userflow/Grievance/disciplinary-action|Disciplinary Action]]

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Active PIP exists | Blocked | "Employee already has an active improvement plan" |
| Check-in overdue | Notification | "PIP check-in overdue for [Employee]" |

## Events Triggered

- `ImprovementPlanCreated` → [[backend/messaging/event-catalog|Event Catalog]]
- `ImprovementPlanEvaluated` → [[backend/messaging/event-catalog|Event Catalog]]
- Notifications to employee, mentor, HR → [[backend/notification-system|Notification System]]

## Related Flows

- [[Userflow/Performance/manager-review|Manager Review]]
- [[Userflow/Performance/goal-setting|Goal Setting]]
- [[Userflow/Grievance/disciplinary-action|Disciplinary Action]]

## Module References

- [[modules/performance/improvement-plans/overview|Improvement Plans]]
- [[modules/performance/reviews/overview|Reviews]]
