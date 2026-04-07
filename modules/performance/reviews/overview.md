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

- [[performance|Performance Module]]
- [[review-cycles]]
- [[feedback]]
- [[goals-okr]]
- [[recognitions]]
- [[improvement-plans]]
- [[succession-planning]]
- [[multi-tenancy]]
- [[error-handling]]
- [[WEEK3-performance]]
