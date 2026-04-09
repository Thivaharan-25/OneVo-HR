# Manager Review

**Area:** Performance  
**Required Permission(s):** `performance:read-team` + `performance:write`  
**Related Permissions:** `workforce:view` (include productivity data)

---

## Preconditions

- Employee has submitted self-assessment → [[Userflow/Performance/self-assessment|Self Assessment]]
- Active review cycle → [[Userflow/Performance/review-cycle-setup|Review Cycle Setup]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: View Pending Reviews
- **UI:** Performance → Team Reviews → list of direct reports with review status
- **API:** `GET /api/v1/performance/reviews?cycle_id={id}&role=manager`

### Step 2: Review Employee
- **UI:** Select employee → view their self-assessment → see goals progress → optionally view peer feedback (if 360)

### Step 3: Rate and Comment
- **UI:** Rate employee against each competency → add comments per competency → set overall rating → write summary feedback → add development recommendations
- **Backend:** ReviewService.SubmitManagerReviewAsync() → [[modules/performance/reviews/overview|Reviews]]

### Step 4: Include Productivity Data (if `workforce:view`)
- **UI:** Toggle "Include Productivity Metrics" → system pulls: avg daily productive hours, top apps, attendance pattern, exception count
- Links: [[Userflow/Analytics-Reporting/productivity-dashboard|Productivity Dashboard]], [[Userflow/Workforce-Presence/presence-session-view|Presence Session View]]

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

- `ManagerReviewSubmitted` → [[backend/messaging/event-catalog|Event Catalog]]
- Notification to HR (for calibration) → [[backend/notification-system|Notification System]]

## Related Flows

- [[Userflow/Performance/self-assessment|Self Assessment]]
- [[Userflow/Performance/peer-feedback|Peer Feedback]]
- [[Userflow/Performance/review-cycle-setup|Review Cycle Setup]]
- [[Userflow/Performance/improvement-plan|Improvement Plan]]

## Module References

- [[modules/performance/reviews/overview|Reviews]]
- [[modules/performance/review-cycles/overview|Review Cycles]]
- [[modules/productivity-analytics/overview|Productivity Analytics]]
