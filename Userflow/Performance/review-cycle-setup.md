# Review Cycle Setup

**Area:** Performance  
**Trigger:** HR Admin creates review cycle (user action — configuration)
**Required Permission(s):** `performance:manage`  
**Related Permissions:** `employees:read` (select participants)

---

## Preconditions

- Employees exist and are active → [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Create Cycle
- **UI:** Sidebar → Performance → Cycles → "Create Cycle" → enter: name (e.g., "Q1 2026 Review"), period start/end dates, review type (self-only, manager, 360-degree)
- **API:** `POST /api/v1/performance/cycles`

### Step 2: Configure Rating Scale
- **UI:** Select rating scale: 1-5 stars, 1-10 numeric, or custom labels (Exceeds/Meets/Below Expectations) → define competencies to rate against

### Step 3: Set Deadlines
- **UI:** Self-review deadline → manager review deadline → peer feedback deadline (if 360) → calibration deadline
- **Validation:** Each deadline must be after the previous

### Step 4: Select Participants
- **UI:** Add: all active employees, specific departments, or individual employees → exclude probationary employees (optional)
- **Backend:** ReviewCycleService.CreateAsync() → [[modules/performance/review-cycles/overview|Review Cycles]]
- **DB:** `review_cycles`, `review_cycle_participants`

### Step 5: Launch Cycle
- **UI:** Click "Launch" → confirm → notifications sent to all participants with deadlines
- **API:** `POST /api/v1/performance/cycles/{id}/launch`
- **Result:** Self-assessment forms become available to participants

## Variations

### Mid-year vs annual review
- Different competency sets and depth of assessment

### When productivity data available (`workforce:view`)
- Option to include productivity metrics in manager review form

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Overlapping cycle | Warning | "An active cycle already exists for this period" |
| No participants | Blocked | "Add at least one participant" |
| Past start date | Validation fails | "Cycle start date cannot be in the past" |

## Events Triggered

- `ReviewCycleLaunched` → [[backend/messaging/event-catalog|Event Catalog]]
- Notifications to all participants → [[backend/notification-system|Notification System]]

## Related Flows

- [[Userflow/Performance/self-assessment|Self Assessment]]
- [[Userflow/Performance/manager-review|Manager Review]]
- [[Userflow/Performance/peer-feedback|Peer Feedback]]
- [[Userflow/Performance/goal-setting|Goal Setting]]

## Module References

- [[modules/performance/review-cycles/overview|Review Cycles]]
- [[modules/performance/reviews/overview|Reviews]]
- [[database/performance|Performance]]
