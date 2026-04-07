# Self-Assessment

**Area:** Performance  
**Required Permission(s):** `performance:read-own`  
**Related Permissions:** `performance:write` (save draft)

---

## Preconditions

- Active review cycle with employee as participant → [[review-cycle-setup]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Receive Notification
- **UI:** Notification: "Self-assessment for Q1 2026 Review is open. Due by April 30."
- **API:** `GET /api/v1/performance/reviews/me?cycle_id={id}`

### Step 2: Fill Self-Assessment
- **UI:** Performance → My Reviews → select cycle → form with:
  - Rate self against each competency (using cycle's rating scale)
  - Key achievements this period (text)
  - Areas for development (text)
  - Goals progress update → [[goal-setting]]
  - Overall self-rating

### Step 3: Save Draft / Submit
- **UI:** "Save Draft" (come back later) or "Submit" (final, cannot edit after)
- **API:** `PUT /api/v1/performance/reviews/{id}` (draft) or `POST /api/v1/performance/reviews/{id}/submit`
- **Backend:** ReviewService.SubmitSelfAssessmentAsync() → [[reviews]]
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

- `SelfAssessmentSubmitted` → [[event-catalog]]
- Notification to manager → [[notification-system]]

## Related Flows

- [[review-cycle-setup]]
- [[manager-review]]
- [[goal-setting]]

## Module References

- [[reviews]]
- [[review-cycles]]
