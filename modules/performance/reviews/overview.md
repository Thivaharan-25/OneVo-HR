# Reviews

**Module:** Performance  
**Feature:** Reviews

---

## Purpose

Multi-rater performance reviews (self, manager, peer, 360) with optional productivity scores.

## Database Tables

### `reviews`
Key columns: `cycle_id`, `employee_id`, `reviewer_id`, `review_type` (`self`, `manager`, `peer`, `360`), `overall_rating` (1.0–5.0), `productivity_score` (NEW, nullable), `comments`, `status`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/performance/reviews/{employeeId}` | `performance:read` | Reviews |
| POST | `/api/v1/performance/reviews` | `performance:write` | Submit review |

## Related

- [[database/performance|Performance Module]]
- [[modules/performance/review-cycles/overview|Review Cycles]]
- [[modules/performance/feedback/overview|Feedback]]
- [[modules/performance/goals-okr/overview|Goals Okr]]
- [[modules/performance/recognitions/overview|Recognitions]]
- [[modules/performance/improvement-plans/overview|Improvement Plans]]
- [[Userflow/Performance/succession-planning|Succession Planning]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[backend/messaging/error-handling|Error Handling]]
- Performance task file (deferred to Phase 2)
