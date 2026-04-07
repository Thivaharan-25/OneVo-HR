# Performance Improvement Plan (PIP)

**Area:** Performance  
**Required Permission(s):** `performance:manage`  
**Related Permissions:** `employees:write` (update employee record)

---

## Preconditions

- Employee has received below-standard review → [[manager-review]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Create PIP
- **UI:** Employee Profile → Performance → "Create Improvement Plan" → set duration (30/60/90 days)
- **API:** `POST /api/v1/performance/improvement-plans`

### Step 2: Define Improvement Areas
- **UI:** Add specific improvement areas → set measurable targets for each → set check-in schedule (weekly/bi-weekly)
- **Backend:** ImprovementPlanService.CreateAsync() → [[improvement-plans]]
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
- If not met → can trigger [[disciplinary-action]]

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Active PIP exists | Blocked | "Employee already has an active improvement plan" |
| Check-in overdue | Notification | "PIP check-in overdue for [Employee]" |

## Events Triggered

- `ImprovementPlanCreated` → [[event-catalog]]
- `ImprovementPlanEvaluated` → [[event-catalog]]
- Notifications to employee, mentor, HR → [[notification-system]]

## Related Flows

- [[manager-review]]
- [[goal-setting]]
- [[disciplinary-action]]

## Module References

- [[improvement-plans]]
- [[reviews]]
