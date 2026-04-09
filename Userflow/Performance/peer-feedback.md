# Peer Feedback

**Area:** Performance  
**Required Permission(s):** `performance:read-own` (for nominated employees)  
**Related Permissions:** `performance:manage` (configure 360-degree reviews)

---

## Preconditions

- Review cycle configured as 360-degree → [[Userflow/Performance/review-cycle-setup|Review Cycle Setup]]
- Peer feedback nominations assigned
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Receive Feedback Request
- **UI:** Notification: "You've been asked to provide feedback for [Employee Name]"
- **API:** `GET /api/v1/performance/feedback/requests`

### Step 2: Provide Feedback
- **UI:** Performance → Feedback Requests → select colleague → answer structured questions (strengths, areas for improvement, collaboration rating) → rate on scale → option for anonymous submission
- **API:** `POST /api/v1/performance/feedback`
- **Backend:** FeedbackService.SubmitAsync() → [[modules/performance/feedback/overview|Feedback]]
- **DB:** `peer_feedback` — record with optional `is_anonymous` flag

### Step 3: Aggregation
- **Backend:** All peer feedback aggregated into employee's review → anonymized if configured → visible to manager during manager review

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Deadline passed | Form locked | "Feedback deadline has passed" |
| Feedback for self | Blocked | "Cannot provide feedback for yourself" |

## Events Triggered

- `PeerFeedbackSubmitted` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Performance/review-cycle-setup|Review Cycle Setup]]
- [[Userflow/Performance/manager-review|Manager Review]]
- [[Userflow/Performance/self-assessment|Self Assessment]]

## Module References

- [[modules/performance/feedback/overview|Feedback]]
- [[modules/performance/reviews/overview|Reviews]]
