# Self-Assessment

**Area:** Performance  
**Trigger:** Employee opens self-assessment during review cycle (reaction — triggered by cycle launch)
**Required Permission(s):** `performance:read-own`  
**Related Permissions:** `performance:write` (save draft)

---

## Preconditions

- Active review cycle with employee as participant → [[Userflow/Performance/review-cycle-setup|Review Cycle Setup]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Receive Notification
- **UI:** Notification: "Self-assessment for Q1 2026 Review is open. Due by April 30."
- **API:** `GET /api/v1/performance/reviews/me?cycle_id={id}`

### Step 2: Fill Self-Assessment
- **UI:** Performance → My Reviews → select cycle → form with:
  - Rate self against each competency (using cycle's rating scale)
  - Key achievements this period (text)
  - Areas for development (text)
  - Goals progress update → [[Userflow/Performance/goal-setting|Goal Setting]]
  - Overall self-rating

### Step 3: Save Draft / Submit
- **UI:** "Save Draft" (come back later) or "Submit" (final, cannot edit after)
- **API:** `PUT /api/v1/performance/reviews/{id}` (draft) or `POST /api/v1/performance/reviews/{id}/submit`
- **Backend:** ReviewService.SubmitSelfAssessmentAsync() → [[modules/performance/reviews/overview|Reviews]]
- **DB:** `reviews` — status: "Draft" or "Submitted"

### Step 4: Post-Submit
- Manager notified that self-assessment is ready for review
- Employee cannot edit submitted assessment

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Past deadline | Form locked | "Self-assessment deadline has passed" |
| Incomplete required fields | Cannot submit | "Please complete all required fields" |

## Events Triggered

- `SelfAssessmentSubmitted` → [[backend/messaging/event-catalog|Event Catalog]]
- Notification to manager → [[backend/notification-system|Notification System]]

## Related Flows

- [[Userflow/Performance/review-cycle-setup|Review Cycle Setup]]
- [[Userflow/Performance/manager-review|Manager Review]]
- [[Userflow/Performance/goal-setting|Goal Setting]]

## Module References

- [[modules/performance/reviews/overview|Reviews]]
- [[modules/performance/review-cycles/overview|Review Cycles]]
