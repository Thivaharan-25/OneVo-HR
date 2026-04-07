# Goal Setting

**Area:** Performance  
**Required Permission(s):** `performance:write` (own goals) or `performance:manage` (team goals)  
**Related Permissions:** `performance:read-team` (view team goals)

---

## Preconditions

- Employee is active
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Create Goal
- **UI:** Performance → Goals → "Create Goal" → enter: title, description, type (OKR, KPI, Development)
- **API:** `POST /api/v1/performance/goals`

### Step 2: Define Measurables
- **UI:** Set measurable target (e.g., "Increase test coverage to 80%") → set metric type (percentage, number, boolean) → set target value → set current value (baseline)

### Step 3: Set Timeline
- **UI:** Set start date → set deadline → link to company/team objective (optional for cascading OKRs)
- **Backend:** GoalService.CreateAsync() → [[goals-okr]]
- **DB:** `goals` — record created

### Step 4: Track Progress
- **UI:** Update progress via check-ins → add notes → update current value → progress bar auto-calculates percentage
- **API:** `PUT /api/v1/performance/goals/{id}/check-in`

### Step 5: Complete
- **UI:** Mark goal as complete when target achieved → feeds into performance review

## Variations

### Manager setting goals for direct reports
- With `performance:manage`: create goals for team members → employee sees assigned goals
- Can cascade company OKRs down to individual goals

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Deadline in past | Validation fails | "Goal deadline cannot be in the past" |
| Duplicate goal title | Warning | "A goal with this title already exists" |

## Events Triggered

- `GoalCreated` → [[event-catalog]]
- `GoalCompleted` → [[event-catalog]]

## Related Flows

- [[review-cycle-setup]]
- [[self-assessment]]
- [[development-plan]]

## Module References

- [[goals-okr]]
- [[performance]]
