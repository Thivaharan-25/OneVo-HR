# Goal Setting

**Area:** Performance  
**Trigger:** Employee or manager creates goals or OKRs (user action)

---

## Preconditions

- Employee is active
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Create Goal
- **UI:** Performance -> Goals -> "Create Goal" -> enter: title, description, type (OKR, KPI, Development)
- **API:** `POST /api/v1/performance/goals`

### Step 2: Define Measurables
- **UI:** Set measurable target (e.g., "Increase test coverage to 80%") -> set metric type (percentage, number, boolean) -> set target value -> set current value (baseline)

### Step 3: Set Timeline
- **Backend:** GoalService.CreateAsync() -> [[modules/performance/goals-okr/overview|Goals Okr]]
- **DB:** `goals` - record created

### Step 4: Track Progress
- **UI:** Update progress via check-ins -> add notes -> update current value -> progress bar auto-calculates percentage
- **API:** `PUT /api/v1/performance/goals/{id}/check-in`

### Step 5: Complete
- **UI:** Mark goal as complete when target achieved -> feeds into performance review

## Variations

### Coverage owner setting goals for covered employees
- Can cascade company OKRs down to individual goals when permission and management coverage allow it

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Deadline in past | Validation fails | "Goal deadline cannot be in the past" |
| Duplicate goal title | Warning | "A goal with this title already exists" |

## Events Triggered

- `GoalCreated` -> [[backend/messaging/event-catalog|Event Catalog]]
- `GoalCompleted` -> [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Performance/review-cycle-setup|Review Cycle Setup]]
- [[Userflow/Performance/self-assessment|Self Assessment]]
- [[Userflow/Skills-Learning/development-plan|Development Plan]]

## Module References

- [[modules/performance/goals-okr/overview|Goals Okr]]
- [[database/performance|Performance]]
