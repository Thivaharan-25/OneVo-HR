# Manager Review

**Area:** Performance  
**Required Permission(s):** `performance:read-team` + `performance:write`  
**Related Permissions:** `workforce:view` (include productivity data)

---

## Preconditions

- Employee has submitted self-assessment → [[self-assessment]]
- Active review cycle → [[review-cycle-setup]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: View Pending Reviews
- **UI:** Performance → Team Reviews → list of direct reports with review status
- **API:** `GET /api/v1/performance/reviews?cycle_id={id}&role=manager`

### Step 2: Review Employee
- **UI:** Select employee → view their self-assessment → see goals progress → optionally view peer feedback (if 360)

### Step 3: Rate and Comment
- **UI:** Rate employee against each competency → add comments per competency → set overall rating → write summary feedback → add development recommendations
- **Backend:** ReviewService.SubmitManagerReviewAsync() → [[reviews]]

### Step 4: Include Productivity Data (if `workforce:view`)
- **UI:** Toggle "Include Productivity Metrics" → system pulls: avg daily productive hours, top apps, attendance pattern, exception count
- Links: [[productivity-dashboard]], [[presence-session-view]]

### Step 5: Submit
- **API:** `POST /api/v1/performance/reviews/{id}/manager-submit`
- **DB:** `reviews` — manager rating, comments stored, status: "Manager Reviewed"
- **Result:** Moves to calibration phase or directly to employee visibility (based on cycle config)

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Self-assessment not submitted | Cannot review | "Waiting for employee's self-assessment" |
| Past manager deadline | Form locked | "Manager review deadline has passed" |

## Events Triggered

- `ManagerReviewSubmitted` → [[event-catalog]]
- Notification to HR (for calibration) → [[notification-system]]

## Related Flows

- [[self-assessment]]
- [[peer-feedback]]
- [[review-cycle-setup]]
- [[improvement-plan]]

## Module References

- [[reviews]]
- [[review-cycles]]
- [[productivity-analytics]]
